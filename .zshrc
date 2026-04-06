# 如果是 macOS，添加 Homebrew 路径
if [[ "$OSTYPE" == "darwin"* ]]; then
  export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
fi

# Enable Powerlevel10k instant prompt.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# Oh My Zsh 所在路径
export ZSH="$HOME/.oh-my-zsh"

DISABLE_MAGIC_FUNCTIONS="true"
ENABLE_CORRECTION="true"
COMPLETION_WAITING_DOTS="true"
DISABLE_AUTO_UPDATE=true
DISABLE_UPDATE_PROMPT=true

# 启用的插件 (结合通用和高效开发)
plugins=(
  git
  fzf
  extract
  zsh-autosuggestions
  zsh-syntax-highlighting
  zsh-history-substring-search
)

source $ZSH/oh-my-zsh.sh

# User configuration
export HISTCONTROL=ignoreboth
export HISTORY_IGNORE="(&|[bf]g|c|clear|history|exit|q|pwd|* --help)"

# Custom less colors for man pages
export LESS_TERMCAP_md="$(tput bold 2> /dev/null; tput setaf 2 2> /dev/null)"
export LESS_TERMCAP_me="$(tput sgr0 2> /dev/null)"
export PROMPT_COMMAND="history -a; $PROMPT_COMMAND"

# 通用别名
alias c="clear"
alias ls="ls --color=auto"
alias ll="ls -l"
alias la="ls -la"

# 根据系统设置不同系统的包管理器快捷操作
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if command -v pacman &> /dev/null; then
        alias update="sudo pacman -Syu"
        alias rmpkg="sudo pacman -Rsn"
        alias cleanup="sudo pacman -Rsn \$(pacman -Qtdq)"
    elif command -v apt &> /dev/null; then
        alias update="sudo apt update && sudo apt upgrade"
        alias rmpkg="sudo apt remove --purge"
        alias cleanup="sudo apt autoremove"
    elif command -v dnf &> /dev/null; then
        alias update="sudo dnf upgrade"
        alias rmpkg="sudo dnf remove"
        alias cleanup="sudo dnf autoremove"
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    if command -v brew &> /dev/null; then
        alias update="brew update && brew upgrade"
        alias rmpkg="brew uninstall"
        alias cleanup="brew cleanup"
    fi
fi

# Powerlevel10k 主题 (安装在 oh-my-zsh custom themes 下)
if [[ -f ${ZSH_CUSTOM:-$USER_ZSH_CUSTOM}/themes/powerlevel10k/powerlevel10k.zsh-theme ]]; then
    source ${ZSH_CUSTOM:-$USER_ZSH_CUSTOM}/themes/powerlevel10k/powerlevel10k.zsh-theme
fi

# 引入 p10k 配置
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

### USER SPECIFIC PATHS
[[ -d "$HOME/.rd/bin" ]] && export PATH="$HOME/.rd/bin:$PATH"

# no spell correct
unsetopt correct_all

# Completion: prefer case-sensitive matches
zstyle ':completion:*' matcher-list \
  'm:{a-zA-Z}={a-zA-Z}' \
  'm:{a-z}={A-Z}'
