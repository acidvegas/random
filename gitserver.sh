#/bin/sh
[ ! getent group ssh                       ] && groupadd ssh
[ ! grep -q /usr/bin/git-shell /etc/shells ] && echo /usr/bin/git-shell >> /etc/shells
[ ! $(getent passwd git > /dev/null)       ] && userdel -f git
useradd -d /srv/git -G ssh -k /dev/null -m -s /usr/bin/git-shell -U git
echo "PUBLICKEY" > /etc/ssh/authorized_keys/git
mkdir "$1.git" && cd "$1.git" && git -C "$1.git" --bare init chown -R git:git "$1.git"