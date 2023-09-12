[[ $- != *i* ]] && return

shopt -s checkwinsize

export LC_CTYPE=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# color
alias diff='diff --color=auto'
alias dir='dir --color=auto'
alias egrep='egrep --color=auto'
alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias ip='ip -color=auto'
alias ls='ls --color=auto'
alias ncdu='ncdu --color dark -rr'
alias vdir='vdir --color=auto'

# rewrites
alias pip='pip3'
alias python='python3'
alias wget='wget -q --show-progress'

# random
alias ..="cd ../"
alias up="sudo apt-get update && sudo apt-get upgrade && sudo apt autoremove"

if [ $(id -u) == "0" ]; then
	export PS1="\e[31m\u@\h\e[0m \e[33m\w \e[0m: "
else
	export PS1="\e[38;5;41m\u@\h\e[0m \e[38;5;69m\w \e[0m: "
fi
