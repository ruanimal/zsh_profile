#!/usr/bin/env python3
"""
Zsh History Cleaner - 清理和优化 zsh 历史文件

功能：
1. 清理超过指定保留时间的多行命令历史
2. 清理超过 3 倍保留时间的所有历史记录
3. 对所有时间的历史记录进行去重（保留最近一条）
4. 备份原始文件和维护完整历史备份

使用方法：
    python3 clean_history.py [options]

选项：
    --days N        保留时间（天），默认 30
    --dry-run       预览模式，不实际修改文件
    --backup-dir    备份目录，默认 ~/.zsh_history_backups/
    --history-file  历史文件路径，默认 ~/.zsh_history
"""

import re
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple, Optional


class ZshHistoryCleaner:
    """Zsh 历史文件清理器"""

    def __init__(self, history_file: str, backup_dir: str, retention_days: int, dry_run: bool = False):
        self.history_file = Path(history_file).expanduser()
        self.backup_dir = Path(backup_dir).expanduser()
        self.retention_days = retention_days
        self.dry_run = dry_run

        # 计算时间阈值
        now = datetime.now()
        self.retention_threshold = now - timedelta(days=retention_days)
        self.cleanup_threshold = now - timedelta(days=retention_days * 3)  # 3 倍保留时间

    def parse_history_line(self, line: str) -> Optional[Tuple[Optional[datetime], str, bool]]:
        """
        解析 zsh 历史行

        返回：(时间戳, 命令内容, 是否为多行命令)
        """
        line = line.rstrip('\n')

        # 匹配扩展历史格式：: <timestamp>:<duration>;<command>
        extended_pattern = r'^: (\d+):(\d+);(.*)'
        match = re.match(extended_pattern, line)

        if match:
            timestamp = int(match.group(1))
            command = match.group(3)
            dt = datetime.fromtimestamp(timestamp)
            is_multiline = command.rstrip().endswith('\\')
            return (dt, command, is_multiline)

        # 普通历史行（无时间戳）
        if line and not line.startswith(':'):
            is_multiline = line.rstrip().endswith('\\')
            return (None, line, is_multiline)

        return None

    def read_history_file(self) -> List[Tuple[Optional[datetime], str, bool]]:
        """读取历史文件，返回解析后的历史记录列表"""
        if not self.history_file.exists():
            print(f"错误：历史文件不存在: {self.history_file}")
            sys.exit(1)

        history_entries = []
        with open(self.history_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                entry = self.parse_history_line(line)
                if entry:
                    history_entries.append(entry)

        return history_entries

    def should_keep_entry(self, entry: Tuple[Optional[datetime], str, bool]) -> bool:
        """
        判断是否应该保留该历史记录

        清理规则：
        1. 无时间戳的记录直接清理
        2. 多行命令：超过保留时间则清理
        3. 单行命令：超过 3 倍保留时间则清理
        """
        timestamp, command, is_multiline = entry

        # 无时间戳的记录直接清理
        if timestamp is None:
            return False

        # 多行命令：超过保留时间则清理
        if is_multiline:
            return timestamp >= self.retention_threshold

        # 单行命令：超过 3 倍保留时间则清理
        return timestamp >= self.cleanup_threshold

    def deduplicate_history(self, entries: List[Tuple[Optional[datetime], str, bool]]) -> List[Tuple[Optional[datetime], str, bool]]:
        """
        对历史记录进行去重，保留最近的一条

        注意：去重对所有时间生效，不受保留时间限制
        """
        seen_commands = {}
        deduplicated = []

        # 从后往前遍历，保留最新的记录
        for entry in reversed(entries):
            timestamp, command, is_multiline = entry

            # 对于多行命令，使用完整命令内容作为键
            if is_multiline:
                key = command
            else:
                # 对于单行命令，使用命令内容作为键
                key = command.strip()

            # 如果命令未见过，或者当前记录更新
            if key not in seen_commands:
                seen_commands[key] = entry
            elif timestamp and seen_commands[key][0] is None:
                seen_commands[key] = entry
            elif timestamp and seen_commands[key][0] and timestamp > seen_commands[key][0]:
                seen_commands[key] = entry

        # 按时间排序（无时间戳的记录放在最后）
        for entry in seen_commands.values():
            deduplicated.append(entry)

        # 按时间排序
        def sort_key(entry):
            ts = entry[0]
            if ts is None:
                return datetime.min
            return ts

        deduplicated.sort(key=sort_key)
        return deduplicated

    def backup_original_file(self) -> Path:
        """备份原始历史文件"""
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"zsh_history_backup_{timestamp}"

        if not self.dry_run:
            import shutil
            shutil.copy2(self.history_file, backup_file)
            print(f"已备份到: {backup_file}")

        return backup_file

    def cleanup_old_backups(self, keep_count: int = 30):
        """清理旧备份文件，保留最近的指定数量"""
        if not self.backup_dir.exists():
            return

        backup_files = sorted(
            self.backup_dir.glob("zsh_history_backup_*"),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )

        # 删除多余的备份
        for old_backup in backup_files[keep_count:]:
            if not self.dry_run:
                old_backup.unlink()
                print(f"已删除旧备份: {old_backup}")
            else:
                print(f"[预览] 将删除旧备份: {old_backup}")

    def update_full_history_backup(self, entries: List[Tuple[Optional[datetime], str, bool]]):
        """更新完整历史备份文件"""
        full_backup_file = self.backup_dir / "zsh_history_full"

        if not self.dry_run:
            self.backup_dir.mkdir(parents=True, exist_ok=True)

            # 读取现有完整备份
            existing_entries = []
            if full_backup_file.exists():
                existing_entries = self.read_history_file_from(full_backup_file)

            # 合并去重
            all_entries = existing_entries + entries
            deduplicated = self.deduplicate_history(all_entries)

            # 写入完整备份
            with open(full_backup_file, 'w', encoding='utf-8') as f:
                for entry in deduplicated:
                    timestamp, command, is_multiline = entry
                    if timestamp:
                        # 扩展历史格式
                        duration = 0  # 假设持续时间为 0
                        f.write(f": {int(timestamp.timestamp())}:{duration};{command}\n")
                    else:
                        f.write(f"{command}\n")

            print(f"已更新完整历史备份: {full_backup_file}")
        else:
            print(f"[预览] 将更新完整历史备份: {full_backup_file}")

    def read_history_file_from(self, file_path: Path) -> List[Tuple[Optional[datetime], str, bool]]:
        """从指定文件读取历史记录"""
        entries = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    entry = self.parse_history_line(line)
                    if entry:
                        entries.append(entry)
        except Exception as e:
            print(f"警告：读取文件失败 {file_path}: {e}")
        return entries

    def write_cleaned_history(self, entries: List[Tuple[Optional[datetime], str, bool]]):
        """写入清理后的历史文件"""
        if not self.dry_run:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                for entry in entries:
                    timestamp, command, is_multiline = entry
                    if timestamp:
                        # 扩展历史格式
                        duration = 0  # 假设持续时间为 0
                        f.write(f": {int(timestamp.timestamp())}:{duration};{command}\n")
                    else:
                        f.write(f"{command}\n")

            print(f"已写入清理后的历史文件: {self.history_file}")
        else:
            print(f"[预览] 将写入清理后的历史文件: {self.history_file}")

    def run(self):
        """执行清理流程"""
        print(f"开始清理 zsh 历史文件...")
        print(f"历史文件: {self.history_file}")
        print(f"备份目录: {self.backup_dir}")
        print(f"保留时间: {self.retention_days} 天")
        print(f"多行命令清理: 超过 {self.retention_days} 天")
        print(f"历史记录清理: 超过 {self.retention_days * 3} 天")
        print(f"预览模式: {'是' if self.dry_run else '否'}")
        print("-" * 50)

        # 读取历史文件
        original_entries = self.read_history_file()
        original_count = len(original_entries)
        print(f"原始历史记录数: {original_count}")

        # 备份原始文件
        self.backup_original_file()

        # 清理旧备份
        self.cleanup_old_backups()

        # 过滤历史记录
        filtered_entries = [entry for entry in original_entries if self.should_keep_entry(entry)]
        filtered_count = len(filtered_entries)
        print(f"过滤后历史记录数: {filtered_count}")
        print(f"已清理记录数: {original_count - filtered_count}")

        # 去重处理
        deduplicated_entries = self.deduplicate_history(filtered_entries)
        deduplicated_count = len(deduplicated_entries)
        print(f"去重后历史记录数: {deduplicated_count}")
        print(f"已去除重复记录数: {filtered_count - deduplicated_count}")

        # 更新完整历史备份
        self.update_full_history_backup(deduplicated_entries)

        # 写入清理后的历史文件
        self.write_cleaned_history(deduplicated_entries)

        print("-" * 50)
        print("清理完成！")

        if self.dry_run:
            print("注意：预览模式，未实际修改文件")


def main():
    parser = argparse.ArgumentParser(description="Zsh 历史文件清理工具")
    parser.add_argument("--days", type=int, default=30, help="保留时间（天），默认 30")
    parser.add_argument("--dry-run", action="store_true", help="预览模式，不实际修改文件")
    parser.add_argument("--backup-dir", type=str, default="~/.zsh_history_backups/", help="备份目录，默认 ~/.zsh_history_backups/")
    parser.add_argument("--history-file", type=str, default="~/.zsh_history", help="历史文件路径，默认 ~/.zsh_history")

    args = parser.parse_args()

    # 验证参数
    if args.days < 1:
        print("错误：保留时间必须大于 0")
        sys.exit(1)

    cleaner = ZshHistoryCleaner(
        history_file=args.history_file,
        backup_dir=args.backup_dir,
        retention_days=args.days,
        dry_run=args.dry_run
    )

    cleaner.run()


if __name__ == "__main__":
    main()
