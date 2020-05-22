###### Information
This project is no longer being maintained & is made available for historical purposes only.

The IRCS project is basically a stripped down version of [Anope](https://www.anope.org/)'s bots all crammed into one & was developed for usage with [UnrealIRCd](https://www.unrealircd.org/) 4.

###### Setup
You will get the lowest ping having the bot connect to localhost on the same box as the IRCd is running.

The bot *will* require network operator privledges in order to work, so make sure you add that into your IRCd configuration.

Edit [`config.py`](https://github.com/acidvegas/ircs/blob/master/ircs/core/config.py) and change the `oper_passwd` and the `admin_host` settings.

###### Commands
| Mode Command | Description | Restriction |
| --- | --- | --- |
| !mode \<chan> | Read all the auto-mode hosts for \<channel>. | *+q only* |
| !mode \<chan> \<mode> | Read all the \<mode> auto-mode hosts for \<channel>. | *+q only* |
| !mode \<chan> \<mode> +\<ident> | Automatically +\<mode> a user matching \<ident>. | *+q only* |
| !mode \<chan> \<mode> -\<ident> | Remove automatic +\<mode> from a user matching \<ident>. | *+q only* |
| !sync \<chan> | Set all the channels stored in the database for \<channel>. | *+q only* |

| Vhost Command | Description | Restriction |
| --- | --- | --- |
| !vhost add \<ident> \<vhost> | Change the host of \<ident> to \<vhost> on connect. | *admin only*|
| !vhost drop \<ident> | Delete the VHOST registered to \<ident>. | *admin only* |
| !vhost list | Return a list of all activated VHOSTs. | *admin only* |
| !vhost on | Turn on your VHOST. | *vhost users only* |
| !vhost off | Turn off your VHOST. | *vhost users only*|
| !vhost sync | Change your current hostmask to your VHOST. | *vhost users only* |

| Admin Command | Description | Restriction |
| --- | --- | --- |
| !husers | List all users connected but not joined to any channel(s). | *admin only* |
| !husers join \<channel> | Force join all hidden users into \<channe>. | *admin only* |
| !husers kill | Kill the connection of all hidden users. | *admin only* |
| !husers gline | G:Line the connection of all hidden users. | *admin only* |
| !husers gzline | GZ:Line the connection of all hidden users. | *admin only* |

###### Mirrors
- [acid.vegas](https://acid.vegas/random) *(main)*
- [GitHub](https://github.com/acidvegas/random)
- [GitLab](https://gitlab.com/acidvegas/random)
