#!/bin/sh
set -e
for u in $HOME/dev/git/*/; do
	for d in $(find $u -name .git -type d -prune | sort); do
		u=$(basename $u)
		r=$(basename -s .git `git --git-dir $d config --get remote.origin.url`)
		echo "updating $r..."
		git -C $d remote remove origin
		git -C $d remote add origin git@github.com:$s/$r.git
		git -C $d remote set-url --add --push origin git@github.com:$u/$r.git
		git -C $d remote set-url --add --push origin git@gitlab.com:$u/$r.git
		git -C $d remote set-url --add --push origin git@contra:$r.git
	done
done