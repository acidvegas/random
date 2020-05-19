# Modes

#### User Modes
| Mode | Description                                                          | Restriction     |
| ---- | -------------------------------------------------------------------- | --------------- |
| B    | marks you as being a bot in WHOIS                                    |                 |
| d    | can only see messages prefixed with `!@$.                            |                 |
| D    | can only receive private messages from operators, servers & services |                 |
| H    | hide operator status in WHOIS                                        | oper-only       |
| I    | hide online time in WHOIS                                            | oper-only       |
| i    | hidden from WHO & NAMES if queried from outside the channel          |                 |
| o    | network operator                                                     | set by server   |
| p    | hide your channels in WHOIS                                          |                 |
| q    | unkickable                                                           | oper-only       |
| r    | registered nick                                                      | set by services |
| R    | can only receive private messages from registered users              |                 |
| S    | services bot                                                         | services-only   |
| s    | receive server notices                                               | oper-only       |
| T    | can not recieve CTCPs                                                |                 |
| t    | indicates using a vhost                                              | set by server   |
| w    | receive wallops messages                                             |                 |
| x    | hidden cloaked hostname                                              |                 |
| Z    | can only send/receive private messages with ssl/tls users            |                 |
| z    | indicates connected via ssl/tls                                      | set by server   |

#### Channel Modes
###### Access Levels
| Mode | Description                                              | Restriction     |
| ---- | -------------------------------------------------------- | --------------- |
| v	   | voice  - able to speak in +m/+M channels                 | +h              |
| h	   | halfop - has most of the privledges as op                | +o              |
| o	   | op     - full privledges                                 | +o              |
| a	   | admin  - same as op except can not be kick by +ho users  | +q              |
| q    | owner  - same as op except can not be kick by +hoa users | set by services |

###### List Modes
| Mode | Description           | Restriction |
| ---- | --------------------- | ----------- |
| b    | ban user from channel | +h          |
| e    | ban exemption         | +h          |
| I    | invite exemption      | +h          |

###### Settings
| Mode | Description                                            | Restriction     |
| ---- | ------------------------------------------------------ | --------------- |
| c	   | no color                                               | +o              |
| C    | no ctcp                                                | +o              |
| D	   | delay JOIN messages until they speak                   | +o              |
| d	   | indicates hidden users after unsetting +D              | set by server   |
| f	   | flood protection see below                             | +o              |
| G	   | enable word filters                                    | +o              |
| H	   | channel history                                        | +o              |
| i	   | requires people to be /INVITE'd to the channel         | +o              |
| k	   | users must specify a channel key in order to join      | +h              |
| K	   | /KNOCK command is not allowed                          | +o              |
| L	   | users who cant join are be redirected to this channel  | +o              |
| l	   | limit the amount of users that may be in the channel   | +o              |
| m	   | only people with +v or higher (+vhoaq) may speak       | +h              |
| M	   | must be authenticated or have +v to speak              | +o              |
| N	   | no nick-changes permitted                              | +o              |
| n	   | no external messages                                   | +h              |
| O	   | operator only channel                                  | oper-only       |
| P	   | permanent channel                                      | oper-only       |
| p    | private channel                                        | +o              |
| Q    | no /KICK allowed. Can use services for kicking         | +o              |
| R    | only registered users may join                         | +o              |
| r    | channel is registered                                  | set by services |
| s    | channel hidden from /LIST and /WHOIS                   | +o              |
| S    | strip color codes                                      | +o              |
| T    | channel notices are not permitted                      | +o              |
| t    | restricts /TOPIC to +h or higher                       | +h              |
| V    | can not invite users to channel                        | +o              |
| z    | only allow SSL/TLS users to join                       | +o              |
| Z    | indicates all users connected via SSL/TLS when +z      | set by server   |



NOT FINISHED BELOW THIS LINE YADDA YADDA YA

###### Mode f

###### Extended Bands
H max-lines-to-record:max-time-to-record-in-minutes
server-time cap


c 	CTCPs 	Set channel mode +C (block all CTCP's) 	m, M 	
j 	joins 	Set channel mode +i (invite only) 	R 	
k 	knocks 	Set channel mode +K (no /knock's) 		Counted for local clients only
m 	messages/notices 	Set channel mode +m (regular users cannot speak) 	M 	
n 	nick changes 	Set channel mode +N (no nick-changes permitted) 		
t 	text 	Kick the user 	b 	Unlike all the rest, these are per-user message/notice limits. Action is to kick or kick+ban the user.









t 	extbans/timedban 	Timed ban that will make a ban unset after the specified number of minutes. 	+b ~t:3:*!*@hostname

The following ban types specify which actions (join, nick-change or speaking) are affected by a ban:
Extban 	Module 	Explanation 	Example
q 	extbans/quiet 	People matching these bans can join but are unable to speak, unless they have +v or higher. 	+b ~q:*!*@*.blah.com
n 	extbans/nickchange 	People matching these bans cannot change nicks, unless they have +v or higher. 	+b ~n:*!*@*.aol.com
j 	extbans/join 	When a user matches this (s)he may not join the channel but if already in the channel then all activities are permitted such as speaking or changing the nick. This can be useful to ban an entire ISP and then manually /INVITE people to the channel so once joined they can behave as normal. 	+b ~j:*!*@*.aol.com
f 	chanmodes/link 	Forward user to another channel if matching mask. 	+b ~f:#badispchannel:*!*@*.isp.com
m 	extbans/msgbypass 	Bypass message restrictions. This extended ban is only available as +e and not as +b. Syntax: +e ~m:type:mask.

Valid types are: external (bypass +n), moderated (bypass +m/+M), censor (bypass +G), color (bypass +S/+c) and notice (bypass +T).
	+e ~m:moderated:*!*@192.168.*

+e ~m:external:*!*@192.168.*
+e ~m:color:~a:ColorBot

These bantypes introduce new criteria which can be used:
Extban 	Module 	Explanation 	Example
a 	extbans/account 	If a user is logged in to services with this account name, then this ban will match. This is slightly different than ~R, in the sense that a user with nick ABC may be logged in under account XYZ. Not all services packages support this, in which case you will have to use ~R instead. 	+e ~a:SomeAccount

+I ~a:SomeAccount
c 	extbans/inchannel 	If the user is in this channel then (s)he is unable to join. A prefix can also be specified (+/%/@/&/~) which means that it will only match if the user has that rights or higher on the specified channel. 	+b ~c:#lamers

+e ~c:@#trustedops
O 	extbans/operclass 	If the user is an IRCOp and the oper::operclass matches this name then the ban/invex will match. You can use this to for example create *admin* only channels. 	+iI ~O:*admin*
r 	extbans/realname 	If the realname (gecos) of a user matches this then (s)he is unable to join. Since real names may contain spaces you can use a underscore to match a space (and underscore) 	+b ~r:*Stupid_bot_script*
S 	extbans/certfp 	When a user is using SSL/TLS with a client certificate then you can match the user by his/her SSL fingerprint (the one you see in /WHOIS). Useful for ban exemptions (+e) and invite exceptions (+I). 	+e ~S:0000000etc

+I ~S:0000000etc
T 	extbans/textban 	Channel-specific text filtering. Supports two actions: 'censor' and 'block', see examples on the right. 	+b ~T:censor:*badword*


https://www.unrealircd.org/docs/User_%26_Oper_commands
