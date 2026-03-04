#!/bin/bash

# ZSH 配置自动化安装脚本

echo "========================================="
echo "  开始安装 Zsh 环境及相关配置"
echo "========================================="

# 检测操作系统
OS="Unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
fi

echo ">> 检测到系统: $OS"

# 1. 安装 Zsh, Git, Fzf
echo ">> 正在安装前置依赖 (zsh, git, fzf)..."
if [[ "$OS" == "macOS" ]]; then
    if ! command -v brew &> /dev/null; then
        echo "未检测到 Homebrew, 正在安装..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew install zsh git fzf
elif [[ "$OS" == "Linux" ]]; then
    if command -v pacman &> /dev/null; then
        sudo pacman -S --needed --noconfirm zsh git fzf
    elif command -v apt &> /dev/null; then
        sudo apt update
        sudo apt install -y zsh git fzf
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y zsh git fzf
    fi
fi

# 2. 安装 Oh My Zsh
if [ ! -d "$HOME/.oh-my-zsh" ]; then
    echo ">> 正在安装 Oh My Zsh..."
    RUNZSH=no CHSH=no sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
else
    echo ">> Oh My Zsh 已安装, 跳过"
fi

ZSH_CUSTOM=${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}

# 3. 安装插件
echo ">> 正在安装 Zsh 插件..."
# zsh-syntax-highlighting
if [ ! -d "$ZSH_CUSTOM/plugins/zsh-syntax-highlighting" ]; then
    git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM}/plugins/zsh-syntax-highlighting
fi
# zsh-autosuggestions
if [ ! -d "$ZSH_CUSTOM/plugins/zsh-autosuggestions" ]; then
    git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM}/plugins/zsh-autosuggestions
fi
# zsh-history-substring-search
if [ ! -d "$ZSH_CUSTOM/plugins/zsh-history-substring-search" ]; then
    git clone https://github.com/zsh-users/zsh-history-substring-search ${ZSH_CUSTOM}/plugins/zsh-history-substring-search
fi

# 4. 安装 Powerlevel10k 主题
if [ ! -d "$ZSH_CUSTOM/themes/powerlevel10k" ]; then
    echo ">> 正在安装 Powerlevel10k 主题..."
    git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ${ZSH_CUSTOM}/themes/powerlevel10k
fi

# 5. 复制配置文件
echo ">> 配置 .zshrc ..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "$SCRIPT_DIR/.zshrc" "$HOME/.zshrc"

echo ">> 配置 .p10k.zsh ..."
if [ -f "$SCRIPT_DIR/.p10k.zsh" ]; then
    cp "$SCRIPT_DIR/.p10k.zsh" "$HOME/.p10k.zsh"
    echo ">> 已应用自带的 .p10k.zsh 主题配置"
elif [ -f "$HOME/.p10k.zsh" ]; then
    echo ">> 找到已存在的 .p10k.zsh 配置，保留使用"
else
    echo ">> 未找到 .p10k.zsh，重启终端时 p10k 会引导您进行配置"
fi

# 6. 切换默认 Shell
if [ "$SHELL" != "$(which zsh)" ]; then
    echo ">> 正在切换默认 shell 为 zsh..."
    chsh -s $(which zsh)
fi

echo "========================================="
echo "  配置完成！请关闭终端并重新打开，或者执行: "
echo "  exec zsh"
echo "========================================="
