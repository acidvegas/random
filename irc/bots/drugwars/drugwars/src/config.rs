use std::{fs::File, io::Read};

use serde::Deserialize;
use serde_yaml::{Mapping, Sequence};

#[derive(Deserialize)]
pub struct DrugWarsConfig {
    pub settings: Mapping,
    pub locations: Sequence,
    pub drugs: Sequence,
    pub items: Mapping,
    pub messages: Mapping,
}

impl DrugWarsConfig {
    pub fn from_file(path: &str) -> std::io::Result<Self> {
        let mut file = File::open(path)?;
        let mut contents = String::new();
        file.read_to_string(&mut contents)?;

        let config: DrugWarsConfig = serde_yaml::from_str(&contents).unwrap();
        Ok(config)
    }
}
