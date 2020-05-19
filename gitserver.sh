#/bin/sh
[ ! getent group ssh                       ] && groupadd ssh
[ ! grep -q /usr/bin/git-shell /etc/shells ] && echo /usr/bin/git-shell >> /etc/shells
[ ! $(getent passwd git > /dev/null)       ] && userdel -f git
[ ! -d /srv/git                            ] && mkdir /srv/git
useradd -d /srv/git -G ssh -k /dev/null -m -s /usr/bin/git-shell -U git
echo "PUBLICKEY" > /etc/ssh/authorized_keys/git
mkdir /srv/git/$1.git && git -C /srv/git/$1.git --bare init && chown -R git:git /srv/git/$1.git