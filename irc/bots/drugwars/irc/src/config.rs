use std::{fs::File, io::Read};

use serde::Deserialize;

#[derive(Deserialize)]
pub(crate) struct ChannelConfig {
    pub(crate) name: String,
    pub(crate) key: Option<String>,
}

#[derive(Deserialize)]
pub(crate) struct IrcConfig {
    pub(crate) host: String,
    pub(crate) port: u16,
    pub(crate) ssl: bool,

    pub(crate) channels: Vec<ChannelConfig>,

    pub(crate) nick: String,
    pub(crate) user: String,
    pub(crate) real: String,

    pub(crate) cmdkey: String
}

impl IrcConfig {
    pub fn from_file(path: &str) -> std::io::Result<Self> {
        let mut file = File::open(path)?;
        let mut contents = String::new();
        file.read_to_string(&mut contents)?;

        let config: IrcConfig = serde_yaml::from_str(&contents).unwrap();
        Ok(config)
    }
}
