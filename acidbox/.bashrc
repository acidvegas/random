[[ $- != *i* ]] && return

export LC_CTYPE=en_US.UTF-8
export LC_ALL=en_US.UTF-8

alias backup='rm ~/.backup/*.tar.gz && tar cvf ~/.backup/backup-DATE,tar.gz ~/'
alias cmds='sh ~/.scripts/cmds'
alias colors='sh ~/.scripts/colors.sh'
alias contact='sh ~/.scripts/contact'
alias diff='diff --color=auto'
alias dvtm-help='cat ~/.scripts/dvtm-help'
alias grep='grep --color=auto'
alias ls='ls --color=auto'
alias rtach='abduco -a main'
alias rules='sh ~/.scripts/rules'
alias startx='abduco -c main sh ~/.scripts/dvtm-status.sh'
alias tb='(exec 3<>/dev/tcp/termbin.com/9999; cat >&3; cat <&3; exec 3<&-)'
alias title='echo -ne "\033]0;$*\007"'
alias vhosts='sh ~/.scripts/vhosts'

extract () {
	if [ -f $1 ] ; then
		case $1 in
			*.tar.bz2) tar xjvf $1   ;;
			*.tar.gz)  tar xzvf $1   ;;
			*.bz2)     bzip2 -d $1   ;;
			*.rar)     unrar2dir $1  ;;
			*.gz)      gunzip $1     ;;
			*.tar)     tar xf $1     ;;
			*.tbz2)    tar xjf $1    ;;
			*.tgz)     tar xzf $1    ;;
			*.zip)     unzip2dir $1  ;;
			*.Z)       uncompress $1 ;;
			*.7z)      7z x $1       ;;
			*.ace)     unace x $1    ;;
			*)         echo "unkown archive format" ;;
		esac
	else
		echo "'$1' is not a valid file"
	fi
}

rnd() {
	cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w $1 | head -n 1
}

transfer() {
	tmpfile=$( mktemp -t transferXXX )
	curl -H "Max-Downloads: 1" -H "Max-Days: 1" --progress-bar --upload-file $1 https://transfer.sh/$(basename $1) >> $tmpfile;
	cat $tmpfile;
	rm -f $tmpfile;
}

PS1='\e[1;34m> \e[0;32m\w \e[0;37m: '
