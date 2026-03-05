## Zsh Profile 一键安装脚本

用于快速配置一套开箱即用的 Zsh 环境（Oh My Zsh + Powerlevel10k + 常用插件），适用于 macOS 和常见 Linux 发行版。

## 来源说明

本仓库中的 Zsh profile 来源于 **CachyOS 的 Zsh 默认 profile**，并在此基础上整理为可在 macOS/Linux 上复用的一键安装脚本与配置。

上游项目链接：<https://github.com/CachyOS/cachyos-zsh-config>

## 功能概览

- 自动安装依赖：`zsh`、`git`、`fzf`
- 自动安装 `Oh My Zsh`
- 自动安装插件：
	- `zsh-syntax-highlighting`
	- `zsh-autosuggestions`
	- `zsh-history-substring-search`
- 自动安装主题：`powerlevel10k`
- 自动应用仓库内的配置：`.zshrc`、`.p10k.zsh`
- 自动备份已有配置文件（带时间戳）
- 自动切换默认 shell 到 `zsh`（若当前不是）

## 相比 Oh My Zsh 默认配置的优势

- **启动速度更快**：在保留常用能力的前提下使用更精简的插件组合，并结合 `powerlevel10k` 的 Instant Prompt 机制，减少打开新终端时的等待感。
- **补全体验更好**：`zsh-autosuggestions` 基于历史命令提供实时建议，减少重复输入。
- **可读性更高**：`zsh-syntax-highlighting` 提供命令语法高亮，降低输错命令的概率。
- **历史检索更高效**：`zsh-history-substring-search` 支持按子串快速回溯历史命令。
- **提示信息更丰富**：`powerlevel10k` 提供更高信息密度的提示符（如 Git 状态、执行耗时等）。

## 项目结构

```text
.
├── setup.sh      # 一键安装脚本
├── .zshrc        # Zsh 主配置
└── .p10k.zsh     # Powerlevel10k 主题配置
```

## 使用方式

### 1) 克隆仓库

```bash
git clone <your-repo-url> zsh_profile
cd zsh_profile
```

### 2) 赋予执行权限并运行

```bash
chmod +x setup.sh
./setup.sh
```

### 3) 重新加载终端

脚本结束后执行：

```bash
exec zsh
```

或直接关闭并重新打开终端。

## 脚本会做什么

`setup.sh` 的执行流程如下：

1. 检测系统类型（`macOS` / `Linux`）
2. 安装依赖（在 macOS 上使用 `brew`，Linux 上尝试 `pacman/apt/dnf`）
3. 安装 `Oh My Zsh`（如果未安装）
4. 安装插件和 `powerlevel10k` 主题
5. 备份并覆盖 `~/.zshrc`、`~/.p10k.zsh`
6. 将默认 shell 切换到 `zsh`

## 备份与恢复

脚本会在覆盖前自动备份原文件：

- `~/.zshrc.bak.YYYYMMDDHHMMSS`
- `~/.p10k.zsh.bak.YYYYMMDDHHMMSS`

如需恢复：

```bash
cp ~/.zshrc.bak.时间戳 ~/.zshrc
cp ~/.p10k.zsh.bak.时间戳 ~/.p10k.zsh
exec zsh
```

## 手动安装（可选）

如果不想使用脚本，也可以手动复制配置：

```bash
cp .zshrc ~/.zshrc
cp .p10k.zsh ~/.p10k.zsh
exec zsh
```

## 常见问题

- **第一次使用 powerlevel10k 字体显示异常**
	- 安装并启用 Nerd Font（如 MesloLGS NF），然后重启终端。

- **`chsh` 切换失败**
	- 可能需要管理员权限，或当前系统策略限制；可手动执行：
		```bash
		chsh -s "$(which zsh)"
		```

- **已经安装过 Oh My Zsh/插件**
	- 脚本会检测目录并尽量跳过重复安装。

## 适配说明

- 已支持：`macOS`、`Linux`（`pacman` / `apt` / `dnf`）
- 其他发行版可参考脚本逻辑自行调整依赖安装命令。
