use std::collections::{HashMap, VecDeque};

use typemap_rev::{TypeMap, TypeMapKey};

use crate::{config::IrcConfig, Channel, Irc, System};

#[derive(Default)]
pub struct IrcBuilder {
    host: Option<String>,
    port: Option<u16>,
    ssl: Option<bool>,

    channels: Vec<Channel>,

    nick: Option<String>,
    user: Option<String>,
    real: Option<String>,

    cmdkey: Option<String>,

    data: TypeMap,
    default_system: Option<System>,
    systems: HashMap<String, System>,
}

impl From<IrcConfig> for IrcBuilder {
    fn from(config: IrcConfig) -> Self {
        Self {
            host: Some(config.host),
            port: Some(config.port),
            ssl: Some(config.ssl),

            channels: config.channels.into_iter().map(Channel::from).collect(),

            nick: Some(config.nick),
            user: Some(config.user),
            real: Some(config.real),

            cmdkey: Some(config.cmdkey),

            data: TypeMap::default(),
            default_system: None,

            systems: HashMap::default(),
        }
    }
}

impl IrcBuilder {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn host(&mut self, host: &str) -> &mut Self {
        self.host = Some(host.to_owned());
        self
    }

    pub fn port(&mut self, port: u16) -> &mut Self {
        self.port = Some(port);
        self
    }

    pub fn ssl(&mut self, ssl: bool) -> &mut Self {
        self.ssl = Some(ssl);
        self
    }

    pub fn channel(&mut self, channel: &str, key: Option<&str>) -> &mut Self {
        self.channels.push(Channel {
            name: channel.to_owned(),
            key: if key.is_some() {
                Some(key.unwrap().to_owned())
            } else {
                None
            },
        });
        self
    }

    pub fn nick(&mut self, nick: &str) -> &mut Self {
        self.nick = Some(nick.to_owned());
        self
    }

    pub fn user(&mut self, user: &str) -> &mut Self {
        self.user = Some(user.to_owned());
        self
    }

    pub fn real(&mut self, real: &str) -> &mut Self {
        self.real = Some(real.to_owned());
        self
    }

    pub fn cmdkey(&mut self, cmdkey: &str) -> &mut Self {
        self.cmdkey = Some(cmdkey.to_owned());
        self
    }

    pub fn add_resource<V: Send + Sync + 'static, T: TypeMapKey + TypeMapKey<Value = V>>(
        &mut self,
        resource: V,
    ) -> &mut Self {
        self.data.insert::<T>(resource);
        self
    }

    pub fn add_default_system(&mut self, func: System) -> &mut Self {
        self.default_system = Some(func);
        self
    }

    pub fn add_system(&mut self, system_name: &str, func: System) -> &mut Self {
        self.systems.insert(system_name.to_owned(), func);
        self
    }

    pub fn build(&mut self) -> Irc {
        Irc {
            stream: None,
            host: self.host.as_ref().unwrap().clone(),
            port: self.port.unwrap_or_default(),
            ssl: self.ssl.unwrap_or_default(),

            channels: std::mem::take(&mut self.channels),

            nick: self.nick.as_ref().unwrap().clone(),
            user: self.user.as_ref().unwrap().clone(),
            real: self.real.as_ref().unwrap().clone(),

            cmdkey: self.cmdkey.as_ref().unwrap().clone(),

            data: std::mem::take(&mut self.data),

            default_system: self.default_system,
            systems: std::mem::take(&mut self.systems),

            send_queue: VecDeque::new(),
            recv_queue: VecDeque::new(),

            partial_line: String::new(),
        }
    }
}
