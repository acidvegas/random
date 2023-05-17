extern crate typemap_rev;

use std::{
    collections::{HashMap, VecDeque},
    error::Error,
    io::{ErrorKind, Read, Write},
    net::{TcpStream, ToSocketAddrs},
    time::Duration,
};

use builder::IrcBuilder;
use config::{ChannelConfig, IrcConfig};
use irc_command::IrcCommand;
use native_tls::{TlsConnector, TlsStream};
use typemap_rev::TypeMap;

pub mod builder;
pub mod config;
pub mod irc_command;

pub mod typemap {
    pub use typemap_rev::*;
}

pub(crate) const MAX_MSG_LEN: usize = 512;
pub(crate) type System = fn(&mut Irc, &IrcPrefix, Vec<&str>) -> Option<Vec<String>>;

pub enum Stream {
    Plain(TcpStream),
    Tls(TlsStream<TcpStream>),
}

impl Stream {
    pub fn read(&mut self, buf: &mut [u8]) -> Result<usize, std::io::Error> {
        match self {
            Stream::Plain(stream) => stream.read(buf),
            Stream::Tls(stream) => stream.read(buf),
        }
    }

    pub fn write(&mut self, buf: &[u8]) -> Result<usize, std::io::Error> {
        match self {
            Stream::Plain(stream) => stream.write(buf),
            Stream::Tls(stream) => stream.write(buf),
        }
    }
}

#[derive(Debug, Default)]
pub struct IrcPrefix<'a> {
    pub nick: &'a str,
    pub user: Option<&'a str>,
    pub host: Option<&'a str>,
}

impl<'a> From<&'a str> for IrcPrefix<'a> {
    fn from(prefix_str: &'a str) -> Self {
        let prefix_str = &prefix_str[1..];

        let nick_split: Vec<&str> = prefix_str.split('!').collect();
        let nick = nick_split[0];

        // we only have a nick
        if nick_split.len() == 1 {
            return Self {
                nick,
                ..Default::default()
            };
        }

        let user_split: Vec<&str> = nick_split[1].split('@').collect();
        let user = user_split[0];

        // we don't have an host
        if user_split.len() == 1 {
            return Self {
                nick: nick,
                user: Some(user),
                ..Default::default()
            };
        }

        Self {
            nick: nick,
            user: Some(user),
            host: Some(user_split[1]),
        }
    }
}

pub struct IrcMessage<'a> {
    prefix: Option<IrcPrefix<'a>>,
    command: IrcCommand,
    parameters: Vec<&'a str>,
}

impl<'a> From<&'a str> for IrcMessage<'a> {
    fn from(line: &'a str) -> Self {
        let mut elements = line.split_whitespace();

        let tmp = elements.next().unwrap();

        if tmp.chars().next().unwrap() == ':' {
            return Self {
                prefix: Some(tmp.into()),
                command: elements.next().unwrap().into(),
                parameters: elements.collect(),
            };
        }

        Self {
            prefix: None,
            command: tmp.into(),
            parameters: elements.collect(),
        }
    }
}

#[derive(Clone)]
pub struct Channel {
    name: String,
    key: Option<String>,
}

impl From<ChannelConfig> for Channel {
    fn from(channel_config: ChannelConfig) -> Self {
        Self {
            name: channel_config.name,
            key: channel_config.key,
        }
    }
}

pub struct Irc {
    stream: Option<Stream>,
    host: String,
    port: u16,
    ssl: bool,

    channels: Vec<Channel>,

    nick: String,
    user: String,
    real: String,

    cmdkey: String,

    data: TypeMap,

    default_system: Option<System>,
    systems: HashMap<String, System>,

    send_queue: VecDeque<String>,
    recv_queue: VecDeque<String>,

    partial_line: String,
}

impl Irc {
    pub fn from_config(config_path: &str) -> IrcBuilder {
        let config = IrcConfig::from_file(config_path).unwrap();
        config.into()
    }

    pub fn new() -> IrcBuilder {
        IrcBuilder::new()
    }

    pub fn data(&self) -> &TypeMap {
        &self.data
    }

    pub fn data_mut(&mut self) -> &mut TypeMap {
        &mut self.data
    }

    pub fn connect(&mut self) -> Result<(), Box<dyn Error>> {
        let domain = format!("{}:{}", self.host, self.port);

        let mut addrs = domain
            .to_socket_addrs()
            .expect("Unable to get addrs from domain {domain}");

        let sock = addrs
            .next()
            .expect("Unable to get ip from addrs: {addrs:?}");

        let stream = TcpStream::connect(sock)?;
        stream.set_nonblocking(true)?;

        if self.ssl {
            let connector = TlsConnector::new().unwrap();
            let mut tls_stream = connector.connect(&self.host, stream);

            while tls_stream.is_err() {
                tls_stream = match tls_stream.err().unwrap() {
                    native_tls::HandshakeError::Failure(f) => panic!("{f}"),
                    native_tls::HandshakeError::WouldBlock(mid_handshake) => {
                        mid_handshake.handshake()
                    }
                }
            }

            self.stream = Some(Stream::Tls(tls_stream.unwrap()));
            return Ok(());
        }

        self.stream = Some(Stream::Plain(stream));
        Ok(())
    }

    fn join(&mut self) {
        for i in 0..self.channels.len() {
            let channel = &self.channels[i];
            if channel.key.is_some() {
                self.queue(&format!(
                    "JOIN {} {}",
                    channel.name,
                    channel.key.as_ref().unwrap()
                ))
            } else {
                self.queue(&format!("JOIN {}", channel.name))
            }
        }
    }

    fn join_manual(&mut self, channel: &str, key: Option<&str>) {
        if key.is_some() {
            self.queue(&format!("JOIN {} {}", channel, key.unwrap()));
        } else {
            self.queue(&format!("JOIN {}", channel));
        }
    }

    pub fn register(&mut self) {
        self.queue(&format!("USER {} 0 * {}", self.user, self.real));
        self.queue(&format!("NICK {}", self.nick));
    }

    pub fn run(&mut self) {
        // main loop!
        loop {
            self.recv().unwrap();
            self.send().unwrap();
            self.handle_commands();

            std::thread::sleep(Duration::from_millis(50));
        }
    }

    pub fn update(&mut self) {
        self.recv().unwrap();
        self.send().unwrap();
        self.handle_commands();
    }

    fn recv(&mut self) -> Result<(), Box<dyn Error>> {
        let Some(stream) = &mut self.stream else { panic!("stream gwan boom."); };

        let mut lines = VecDeque::new();

        loop {
            let mut buf = [0; MAX_MSG_LEN];

            let bytes_read = match stream.read(&mut buf) {
                Ok(bytes_read) => bytes_read,
                Err(err) => match err.kind() {
                    ErrorKind::WouldBlock => {
                        self.recv_queue.append(&mut lines);
                        return Ok(());
                    }
                    _ => panic!("{:?}", err),
                },
            };

            if bytes_read == 0 {
                break;
            }

            let buf = &buf[..bytes_read];

            let mut str_buf = self.partial_line.clone();
            str_buf += String::from_utf8_lossy(buf).into_owned().as_str();
            let new_lines: Vec<&str> = str_buf.split("\r\n").collect();
            let len = new_lines.len();

            for (index, line) in new_lines.into_iter().enumerate() {
                if index == len - 1 {
                    self.partial_line = line.to_owned();
                    break;
                }
                lines.push_back(line.to_owned());
            }
        }
        Ok(())
    }

    fn send(&mut self) -> Result<(), Box<dyn Error>> {
        let Some(stream) = &mut self.stream else { panic!("stream gwan boom."); };

        while self.send_queue.len() > 0 {
            let msg = self.send_queue.pop_front().unwrap();

            let bytes_written = match stream.write(msg.as_bytes()) {
                Ok(bytes_written) => bytes_written,
                Err(err) => match err.kind() {
                    ErrorKind::WouldBlock => {
                        println!("would block send.");
                        return Ok(());
                    }
                    _ => panic!("{err}"),
                },
            };

            if bytes_written < msg.len() {
                self.send_queue.push_front(msg[bytes_written..].to_owned());
            }
        }

        Ok(())
    }

    fn handle_commands(&mut self) {
        while self.recv_queue.len() != 0 {
            let owned_line = self.recv_queue.pop_front().unwrap();
            let line = owned_line.as_str();

            println!("<< {:?}", line);

            let message: IrcMessage = line.into();

            self.handle_message(&message);
        }
    }

    fn handle_message(&mut self, message: &IrcMessage) {
        match message.command {
            IrcCommand::PING => self.event_ping(&message.parameters[0]),
            IrcCommand::RPL_WELCOME => self.event_welcome(),
            IrcCommand::ERR_NICKNAMEINUSE => self.update_nick(&format!("{}_", &self.nick)),
            IrcCommand::KICK => self.event_kick(
                message.parameters[0],
                message.parameters[1],
                &message.parameters[3..].join(" "),
            ),
            IrcCommand::QUIT => self.event_quit(message.prefix.as_ref().unwrap()),
            IrcCommand::INVITE => self.event_invite(
                message.prefix.as_ref().unwrap(),
                &message.parameters[0][1..],
            ),
            IrcCommand::PRIVMSG => self.event_privmsg(
                message.prefix.as_ref().unwrap(),
                &message.parameters[0],
                &message.parameters[1..].join(" ")[1..],
            ),
            IrcCommand::JOIN => self.event_join(
                message.prefix.as_ref().unwrap(),
                &message.parameters[0][1..],
            ),
            _ => {}
        }
    }

    fn queue(&mut self, msg: &str) {
        let mut msg = msg.replace("\r", "").replace("\n", "");

        if msg.len() > MAX_MSG_LEN - "\r\n".len() {
            let mut i = 0;

            while i < msg.len() {
                let max = (MAX_MSG_LEN - "\r\n".len()).min(msg[i..].len());

                let mut m = msg[i..(i + max)].to_owned();
                println!(">> {:?}", m);
                m = m + "\r\n";
                self.send_queue.push_back(m);
                i += MAX_MSG_LEN - "\r\n".len()
            }
        } else {
            println!(">> {:?}", msg);
            msg = msg + "\r\n";
            self.send_queue.push_back(msg);
        }
    }

    fn event_ping(&mut self, ping_token: &str) {
        self.queue(&format!("PONG {}", ping_token));
    }

    fn event_welcome(&mut self) {
        self.join();
    }

    fn update_nick(&mut self, new_nick: &str) {
        self.nick = new_nick.to_owned();
        self.queue(&format!("NICK {}", self.nick));
    }

    fn event_kick(&mut self, channel: &str, nick: &str, message: &str) {
        if nick != &self.nick {
            return;
        }

        println!("we got kicked!");
        println!("{message}");

        //TODO: fix this in case a key is needed.
        self.join_manual(channel, None);
    }

    fn event_quit(&mut self, prefix: &IrcPrefix) {
        if prefix.nick != self.nick {
            return;
        }

        println!("need to reconnect.");
        std::thread::sleep(Duration::from_secs(15));
        self.connect().unwrap();
        self.register();
    }

    fn event_invite(&mut self, prefix: &IrcPrefix, channel: &str) {
        println!("{} invited us to {}", prefix.nick, channel);
    }

    fn execute_default(&mut self, prefix: &IrcPrefix, channel: &str, message: &str) {
        let Some(default_func) = self.default_system else { return; };

        let mut elements = message.split_whitespace();
        elements.next();

        let Some(output) = default_func(self, prefix, elements.collect()) else {
            return;
        };

        for line in output {
            self.privmsg(channel, &line);
        }
    }

    fn event_privmsg(&mut self, prefix: &IrcPrefix, channel: &str, message: &str) {
        if message.starts_with(&self.cmdkey) {
            let mut elements = message.split_whitespace();
            let sys_name = &elements.next().unwrap()[1..];

            let Some(func) = self.systems.get(sys_name) else { 
                self.execute_default(prefix, channel, message);
                return; 
            };

            let Some(output) = func(self, prefix, elements.collect()) else {
                return;
            };

            for line in output {
                self.privmsg(channel, &line);
            }
        }
    }

    fn event_join(&mut self, prefix: &IrcPrefix, _channel: &str) {
        if prefix.nick != self.nick {
            return;
        }
    }

    pub fn privmsg(&mut self, channel: &str, message: &str) {
        self.queue(&format!("PRIVMSG {} :{}", channel, message));
    }

    pub fn privmsg_all(&mut self, message: &str) {
        for i in 0..self.channels.len() {
            let channel = &self.channels[i];
            self.queue(&format!("PRIVMSG {} :{}", channel.name, message));
        }
    }
}
