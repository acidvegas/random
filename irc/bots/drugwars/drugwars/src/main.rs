pub mod config;
pub mod drug_wars;
pub mod utils;
pub mod render;
pub mod definitions;
pub mod dealer;
pub mod api;

use std::{
    sync::{Arc, RwLock},
    time::Duration,
};

use drug_wars::DrugWars;
use irc::{typemap::TypeMapKey, Irc, IrcPrefix};

struct GameManager;

impl TypeMapKey for GameManager {
    type Value = Arc<RwLock<DrugWars>>;
}

fn main() {
    let drug_wars_arc = Arc::new(RwLock::new(DrugWars::load_config("drugwars_config.yaml")));

    {
        let mut drug_wars = drug_wars_arc.write().unwrap();
        drug_wars.init();
    }

    let mut irc = Irc::from_config("irc_config.yaml")
        .add_resource::<Arc<RwLock<DrugWars>>, GameManager>(drug_wars_arc.clone())
        .add_default_system(melp)
        .add_system("register", register)
        .add_system("todo", todo)
        .add_system("p", show_page)
        .add_system("mw", set_max_width)
        .add_system("gm", give_money)
        .add_system("gd", give_drug)
        .add_system("gi", give_item)
        .add_system("bd", buy_drug)
        .add_system("sd", sell_drug)
        .add_system("bi", buy_item)
        .add_system("bc", buy_capacity)
        .add_system("cc", check_capacity_price)
        .add_system("si", sell_item)
        .add_system("fp", check_flight_prices)
        .add_system("f", flight)
        .build();

    irc.connect().unwrap();
    irc.register();

    loop {
        {
            let mut drug_wars = drug_wars_arc.write().unwrap();
            drug_wars.new_day(&mut irc);
        }
        irc.update();
        std::thread::sleep(Duration::from_millis(50));
    }
}

fn register(irc: &mut Irc, prefix: &IrcPrefix, _arguments: Vec<&str>) -> Option<Vec<String>> {
    let data = irc.data().get::<GameManager>().unwrap();
    let mut drug_wars = data.write().unwrap();
    Some(drug_wars.register_dealer(prefix.nick))
}

fn show_page(irc: &mut Irc, prefix: &IrcPrefix, _arguments: Vec<&str>) -> Option<Vec<String>> {
    let data = irc.data().get::<GameManager>().unwrap();
    let drug_wars = data.read().unwrap();
    Some(drug_wars.show_page_for_nick(prefix.nick))
}

fn melp(_irc: &mut Irc, _prefix: &IrcPrefix, _arguments: Vec<&str>) -> Option<Vec<String>> {
    Some(vec!["melp?".to_owned()])
}

fn set_max_width(irc: &mut Irc, prefix: &IrcPrefix, arguments: Vec<&str>) -> Option<Vec<String>> {
    let data = irc.data().get::<GameManager>().unwrap();

    let Ok(size) = arguments[0].parse::<usize>() else { 
        return Some(vec![
            format!(
                "{}: Unable to parse {} as usize",
                prefix.nick, arguments[1]
            )
        ]);
    };
    
    if size < 75 || size > 130 {
        return Some(vec![
            format!("{}: Size must be between 75 and 130", prefix.nick)
        ])
    }

    let mut drug_wars = data.write().unwrap();
    Some(drug_wars.set_dealer_max_width(prefix.nick, size))
}

fn todo(_irc: &mut Irc, prefix: &IrcPrefix, _arguments: Vec<&str>) -> Option<Vec<String>> {
    Some(vec![
        format!("{}: list of things to add:", prefix.nick),
        "- encounters".to_owned(),
        "- usage of items".to_owned(),
        "- messages / rumors, the fun stuff".to_owned(),
        "- save / load game".to_owned(),
        "- shipping".to_owned(),
        "- attack blokes @ same city".to_owned(),
        "- some kind of flood protection".to_owned(),
        "- some kind of spam protection".to_owned(),
        "- single rng shared everywher".to_owned(),
        "- refactor all this shit".to_owned(),
        "- colors ^-^".to_owned(),
    ])
}

fn buy_drug(irc: &mut Irc, prefix: &IrcPrefix, arguments: Vec<&str>) -> Option<Vec<String>> {
    let data = irc.data().get::<GameManager>().unwrap();
    let Ok(amount) = arguments[1].parse::<usize>() else {
        return Some(vec![
            format!(
                "{}: Unable to parse {} as usize",
                prefix.nick, arguments[1]
            )
        ]);
    };
    
    let mut drug_wars = data.write().unwrap();
    Some(drug_wars.buy_drug(prefix.nick, arguments[0], amount))
}

fn sell_drug(irc: &mut Irc, prefix: &IrcPrefix, arguments: Vec<&str>) -> Option<Vec<String>> {
    let data = irc.data().get::<GameManager>().unwrap();

    let Ok(amount) = arguments[1].parse::<usize>() else {
        return Some(vec![
            format!(
                "{}: Unable to parse {} as usize",
                prefix.nick, arguments[1]
            )
        ]);
    };
    
    let mut drug_wars = data.write().unwrap();
    Some(drug_wars.sell_drug(prefix.nick, arguments[0], amount))
}

fn buy_item(irc: &mut Irc, prefix: &IrcPrefix, arguments: Vec<&str>) -> Option<Vec<String>> {
    let data = irc.data().get::<GameManager>().unwrap();

    let Ok(amount) = arguments[1].parse::<usize>() else {
        return Some(vec![
            format!(
                "{}: Unable to parse {} as usize",
                prefix.nick, arguments[1]
            )
        ]);
    };
    
    let mut drug_wars = data.write().unwrap();
    Some(drug_wars.buy_item(prefix.nick, arguments[0], amount))
}

fn sell_item(irc: &mut Irc, prefix: &IrcPrefix, arguments: Vec<&str>) -> Option<Vec<String>> {
    let data = irc.data().get::<GameManager>().unwrap();
    let Ok(amount) = arguments[1].parse::<usize>() else {
        return Some(vec![
            format!(
                "{}: Unable to parse {} as usize",
                prefix.nick, arguments[1]
            )
        ]);
    };
    
    let mut drug_wars = data.write().unwrap();
    Some(drug_wars.sell_item(prefix.nick, arguments[0], amount))
}

fn check_flight_prices(irc: &mut Irc, prefix: &IrcPrefix, _arguments: Vec<&str>) -> Option<Vec<String>> {
    let data = irc.data().get::<GameManager>().unwrap();
    let drug_wars = data.write().unwrap();
    Some(drug_wars.check_flight_prices(prefix.nick))
}

fn flight(irc: &mut Irc, prefix: &IrcPrefix, arguments: Vec<&str>) -> Option<Vec<String>> {
    let data = irc.data().get::<GameManager>().unwrap();
    let mut drug_wars = data.write().unwrap();
    Some(drug_wars.fly_to(prefix.nick, arguments[0]))
}

fn give_money(irc: &mut Irc, prefix: &IrcPrefix, arguments: Vec<&str>) -> Option<Vec<String>> {
    let data = irc.data().get::<GameManager>().unwrap();
    let Ok(amount) = arguments[1].parse::<f64>() else {
        return Some(vec![
            format!(
                "{}: Unable to parse `{}` as f64",
                prefix.nick, arguments[1]
            )
        ]);
    };

    if amount < 0. {
        return Some(vec![
            format!(
                "{}: Can't give negative money",
                prefix.nick
            )
        ]);
    }

    let mut drug_wars = data.write().unwrap();
    Some(drug_wars.give_money(prefix.nick, amount, arguments[0]))
}

fn give_drug(irc: &mut Irc, prefix: &IrcPrefix, arguments: Vec<&str>) -> Option<Vec<String>> {
    let data = irc.data().get::<GameManager>().unwrap();
    let Ok(amount) = arguments[2].parse::<usize>() else {
        return Some(vec![
            format!(
                "{}: Unable to parse {} as usize",
                prefix.nick, arguments[2]
            )
        ]);
    };

    let mut drug_wars = data.write().unwrap();
    Some(drug_wars.give_drug(prefix.nick, arguments[1], amount, arguments[0]))
}

fn give_item(irc: &mut Irc, prefix: &IrcPrefix, arguments: Vec<&str>) -> Option<Vec<String>> {
    let data = irc.data().get::<GameManager>().unwrap();
    let Ok(amount) = arguments[2].parse::<usize>() else {
        return Some(vec![
            format!(
                "{}: Unable to parse {} as usize",
                prefix.nick, arguments[2]
            )
        ]);
    };

    let mut drug_wars = data.write().unwrap();
    Some(drug_wars.give_item(prefix.nick, arguments[1], amount, arguments[0]))
}

fn buy_capacity(irc: &mut Irc, prefix: &IrcPrefix, arguments: Vec<&str>) -> Option<Vec<String>> {
    let data = irc.data().get::<GameManager>().unwrap();
    let Ok(amount) = arguments[0].parse::<usize>() else {
        return Some(vec![
            format!(
                "{}: Unable to parse {} as usize",
                prefix.nick, arguments[0]
            )
        ]);
    };

    let mut drug_wars = data.write().unwrap();
    Some(drug_wars.buy_capacity(prefix.nick, amount))
}

fn check_capacity_price(irc: &mut Irc, prefix: &IrcPrefix, arguments: Vec<&str>) -> Option<Vec<String>> {
    let data = irc.data().get::<GameManager>().unwrap();

    let Ok(amount) = arguments[0].parse::<usize>() else {
        return Some(vec![
            format!(
                "{}: Unable to parse {} as usize",
                prefix.nick, arguments[0]
            )
        ]);
    };

    let mut drug_wars = data.write().unwrap();
    Some(drug_wars.check_capacity_price(prefix.nick, amount))
}