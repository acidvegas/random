use std::collections::{HashMap, HashSet};

use chrono::NaiveDate;

#[derive(Clone, Copy, Debug, Hash, PartialEq, Eq)]
pub enum MessageKind {
    RumorUpHere,
    RumorDownHere,
    RumorUpAt,
    RumorDownAt,
    Welcome,
    PriceUp,
    PriceUpEnd,
    PriceDown,
    PriceDownEnd,
}

#[derive(Clone, Copy)]
pub struct Drug {
    pub nominal_price: u128,
}

pub struct Weapon {
    pub nominal_price: u128,
    pub ammo: Option<String>,
    pub damage: f32,
}

pub struct Ammo {
    pub nominal_price: u128,
}

pub struct Armor {
    pub nominal_price: u128,
    pub block: f32,
}

pub struct NoScent {
    pub nominal_price: u128,
    pub capacity: usize,
}

pub enum Item {
    Weapon(Weapon),
    Ammo(Ammo),
    Armor(Armor),
    NoScent(NoScent),
}

impl Item {
    pub fn nominal_price(&self) -> u128 {
        match self {
            Item::Weapon(w) => w.nominal_price,
            Item::Ammo(am) => am.nominal_price,
            Item::Armor(ar) => ar.nominal_price,
            Item::NoScent(n) => n.nominal_price,
        }
    }
}

pub struct OwnedDrug {
    pub amount: usize,
    pub bought_at: u128,
}

pub struct MarketDrug {
    pub supply: usize,
    pub demand: usize,
    pub price: u128,
}

pub struct OwnedItem {
    pub amount: usize,
    pub bought_at: u128,
}

pub struct MarketItem {
    pub supply: usize,
    pub demand: usize,
    pub price: u128,
}

pub struct Location {
    pub lat: f32,
    pub long: f32,
    pub drug_market: HashMap<String, MarketDrug>,
    pub item_market: HashMap<String, MarketItem>,
    pub messages: Vec<String>,
    pub blokes: HashSet<String>,
}

pub struct Settings {
    pub day_duration: u32,
    pub current_day: NaiveDate,
}



#[derive(PartialEq, Eq)]
pub enum DealerStatus {
    Available,
    Flying
}