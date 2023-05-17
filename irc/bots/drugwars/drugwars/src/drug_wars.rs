use std::{
    collections::{HashMap, HashSet},
    str::FromStr,
    time::SystemTime,
};

use chrono::{Duration, NaiveDate};
use irc::Irc;
use rand::{Rng, RngCore};
use rand_distr::{Distribution, Normal};

use crate::{
    config::DrugWarsConfig,
    dealer::Dealer,
    definitions::{
        Ammo, Armor, DealerStatus, Drug, Item, Location, MarketDrug, MarketItem, MessageKind,
        NoScent, Settings, Weapon,
    },
    utils::{capacity_price, get_flight_price, pretty_print_money},
};

pub struct DrugWars {
    pub settings: Settings,
    pub timer: SystemTime,
    pub dealers: HashMap<String, Dealer>,
    pub locations: HashMap<String, Location>,
    pub flights: HashMap<String, String>,
    pub drugs: HashMap<String, Drug>,
    pub items: HashMap<String, Item>,
    pub messages: HashMap<MessageKind, Vec<String>>,
}

impl From<DrugWarsConfig> for DrugWars {
    fn from(config: DrugWarsConfig) -> Self {
        let mut locations = HashMap::default();
        let mut drugs = HashMap::default();
        let mut items = HashMap::default();
        let mut messages = HashMap::default();

        for drug in config.drugs {
            let name = drug.as_mapping().unwrap()["name"].as_str().unwrap();
            let price = drug.as_mapping().unwrap()["price"].as_f64().unwrap();
            drugs.insert(
                name.to_owned(),
                Drug {
                    nominal_price: (price * 10000.) as u128,
                },
            );
        }

        let weapons = config.items["weapons"]
            .as_sequence()
            .unwrap()
            .iter()
            .map(|value| value.as_mapping().unwrap())
            .collect::<Vec<_>>();

        for weapon in weapons {
            let name = weapon["name"].as_str().unwrap();
            let price = weapon["price"].as_f64().unwrap();
            let damage = weapon["damage"].as_f64().unwrap() as f32;

            let mut ammo = None;

            if weapon.contains_key("ammo") {
                ammo = Some(weapon["ammo"].as_str().unwrap().to_owned())
            }

            items.insert(
                name.to_owned(),
                Item::Weapon(Weapon {
                    nominal_price: (price * 10000.) as u128,
                    ammo,
                    damage,
                }),
            );
        }

        let ammos = config.items["ammos"]
            .as_sequence()
            .unwrap()
            .iter()
            .map(|value| value.as_mapping().unwrap())
            .collect::<Vec<_>>();

        for ammo in ammos {
            let name = ammo["name"].as_str().unwrap();
            let price = ammo["price"].as_f64().unwrap();

            items.insert(
                name.to_owned(),
                Item::Ammo(Ammo {
                    nominal_price: (price * 10000.) as u128,
                }),
            );
        }

        let armors = config.items["armors"]
            .as_sequence()
            .unwrap()
            .iter()
            .map(|value| value.as_mapping().unwrap())
            .collect::<Vec<_>>();

        for armor in armors {
            let name = armor["name"].as_str().unwrap();
            let price = armor["price"].as_f64().unwrap();
            let block = armor["block"].as_f64().unwrap() as f32;

            items.insert(
                name.to_owned(),
                Item::Armor(Armor {
                    nominal_price: (price * 10000.) as u128,
                    block,
                }),
            );
        }

        let no_scents = config.items["no_scents"]
            .as_sequence()
            .unwrap()
            .iter()
            .map(|value| value.as_mapping().unwrap())
            .collect::<Vec<_>>();

        for no_scent in no_scents {
            let name = no_scent["name"].as_str().unwrap();
            let price = no_scent["price"].as_f64().unwrap();
            let capacity = no_scent["capacity"].as_u64().unwrap() as usize;

            items.insert(
                name.to_owned(),
                Item::NoScent(NoScent {
                    nominal_price: (price * 10000.) as u128,
                    capacity,
                }),
            );
        }

        for location in config.locations {
            let name = location.as_mapping().unwrap()["name"].as_str().unwrap();
            let lat = location.as_mapping().unwrap()["position"]
                .as_mapping()
                .unwrap()["lat"]
                .as_f64()
                .unwrap() as f32;
            let long = location.as_mapping().unwrap()["position"]
                .as_mapping()
                .unwrap()["long"]
                .as_f64()
                .unwrap() as f32;

            locations.insert(
                name.to_owned(),
                Location {
                    lat,
                    long,
                    drug_market: HashMap::default(),
                    item_market: HashMap::default(),
                    messages: vec![],
                    blokes: HashSet::default(),
                },
            );
        }

        // OH LOOK ! I'M FUCKING SLEEP DEPRIVATED !
        for (val_str, enum_variant) in [
            ("rumor_up_here", MessageKind::RumorUpHere),
            ("rumor_down_here", MessageKind::RumorDownHere),
            ("rumor_up_at", MessageKind::RumorUpAt),
            ("rumor_down_at", MessageKind::RumorDownAt),
            ("welcome", MessageKind::Welcome),
            ("price_up", MessageKind::PriceUp),
            ("price_up_end", MessageKind::PriceUpEnd),
            ("price_down", MessageKind::PriceDown),
            ("price_down_end", MessageKind::PriceDownEnd),
        ] {
            let msgs = &config.messages[val_str].as_sequence().unwrap();
            for msg in *msgs {
                let message_vec = messages.entry(enum_variant).or_insert_with(|| vec![]);
                message_vec.push(msg.as_str().unwrap().to_owned());
            }
        }

        let day_duration = config.settings["day_duration"].as_u64().unwrap() as u32;
        let current_day_str = config.settings["start_day"].as_str().unwrap();

        Self {
            settings: Settings {
                day_duration,
                current_day: NaiveDate::from_str(current_day_str).unwrap(),
            },
            timer: SystemTime::now(),
            dealers: HashMap::default(),
            locations,
            flights: HashMap::default(),
            drugs,
            items,
            messages,
        }
    }
}

impl DrugWars {
    pub fn load_config(path: &str) -> Self {
        let config = DrugWarsConfig::from_file(path).unwrap();

        config.into()
    }

    pub fn init(&mut self) {
        println!("initializing.");
        let mut rng = rand::thread_rng();

        self.update_markets(&mut rng);
    }

    fn update_markets(&mut self, rng: &mut dyn RngCore) {
        for (_, location) in &mut self.locations {
            location.drug_market.clear();
            location.item_market.clear();

            for (drug_name, drug) in &self.drugs {
                if rng.gen_bool(4. / 5.) {
                    continue;
                };

                let float_price = (drug.nominal_price as f32) / 10000.;

                let normal = Normal::new(float_price, float_price / 2.).unwrap();

                location.drug_market.insert(
                    drug_name.clone(),
                    MarketDrug {
                        supply: rng.gen_range(0..1000),
                        demand: rng.gen_range(0..1000),
                        price: (normal.sample(rng) * 10000.) as u128,
                    },
                );
            }

            for (item_name, item) in &self.items {
                if rng.gen_bool(4. / 5.) {
                    continue;
                };

                let float_price = (item.nominal_price() as f32) / 10000.;

                let normal = Normal::new(float_price, float_price / 2.).unwrap();

                location.item_market.insert(
                    item_name.clone(),
                    MarketItem {
                        supply: rng.gen_range(0..1000),
                        demand: rng.gen_range(0..1000),
                        price: (normal.sample(rng) * 10000.) as u128,
                    },
                );
            }
        }
    }

    pub fn new_day(&mut self, irc: &mut Irc) {
        let Ok(elapsed) = self.timer.elapsed() else { return; };

        if elapsed.as_secs_f32() > self.settings.day_duration as f32 {
            irc.privmsg_all("new day!");

            self.timer = SystemTime::now();
            self.settings.current_day += Duration::days(1);

            for (nick, destination) in &mut self.flights.clone() {
                let dealer = self.get_dealer_mut(nick).unwrap();

                // Should do mem trick at other places...
                irc.privmsg_all(&format!("{}: You landed at {}", nick, destination));
                dealer.location = std::mem::take(destination);
                dealer.status = DealerStatus::Available;

                let location = self.locations.get_mut(destination).unwrap();
                location.blokes.insert(nick.clone());
            }

            self.flights.clear();

            let mut rng = rand::thread_rng();
            self.update_markets(&mut rng);
        }
    }

    pub fn get_dealer(&self, nick: &str) -> Option<&Dealer> {
        self.dealers.get(nick)
    }

    pub fn get_dealer_mut(&mut self, nick: &str) -> Option<&mut Dealer> {
        self.dealers.get_mut(nick)
    }

    pub fn dealer_not_registered(&self, nick: &str) -> Vec<String> {
        vec![format!("{} is not registered.", nick)]
    }

    pub fn dealer_not_available(&self, nick: &str) -> Vec<String> {
        let dealer = self.get_dealer(nick).unwrap();

        match dealer.status {
            DealerStatus::Flying => vec![format!("{}: Can't do business while flying", nick)],
            _ => vec![],
        }
    }

    pub fn _buy_drug(
        &mut self,
        nick: &str,
        drug_name: &str,
        amount: usize,
        price: u128,
    ) -> Vec<String> {
        let total_price = price * amount as u128;

        let mut location = String::new();

        let dealer = self.get_dealer_mut(nick).unwrap();
        dealer.money -= total_price;
        dealer.add_drug_local(drug_name, amount, price);
        location += &dealer.location;

        let location = self.locations.get_mut(&location).unwrap();
        let market_drug = location.drug_market.get_mut(drug_name).unwrap();
        market_drug.supply -= amount;
        market_drug.demand += amount;

        vec![format!(
            "{}: you bought {} {} for {}",
            nick,
            amount,
            drug_name,
            pretty_print_money(total_price)
        )]
    }

    pub fn _sell_drug(
        &mut self,
        nick: &str,
        drug_name: &str,
        amount: usize,
        price: u128,
    ) -> Vec<String> {
        let total_price = price * amount as u128;

        let mut location = String::new();

        let dealer = self.get_dealer_mut(nick).unwrap();
        dealer.money += total_price;
        dealer.sub_drug_local(drug_name, amount);
        location += &dealer.location;

        let location = self.locations.get_mut(&location).unwrap();
        let market_drug = location.drug_market.get_mut(drug_name).unwrap();
        market_drug.supply += amount;
        market_drug.demand -= amount;

        vec![format!(
            "{}: you sold {} {} for {}",
            nick,
            amount,
            drug_name,
            pretty_print_money(total_price)
        )]
    }

    pub fn _buy_item(
        &mut self,
        nick: &str,
        item_name: &str,
        amount: usize,
        price: u128,
    ) -> Vec<String> {
        let total_price = price * amount as u128;

        let mut location = String::new();

        let dealer = self.get_dealer_mut(nick).unwrap();
        dealer.money -= total_price;
        dealer.add_item_local(item_name, amount, price);
        location += &dealer.location;

        let location = self.locations.get_mut(&location).unwrap();
        let market_item = location.item_market.get_mut(item_name).unwrap();
        market_item.supply -= amount;
        market_item.demand += amount;

        vec![format!(
            "{}: you bought {} {} for {}",
            nick,
            amount,
            item_name,
            pretty_print_money(total_price)
        )]
    }

    pub fn _sell_item(
        &mut self,
        nick: &str,
        item_name: &str,
        amount: usize,
        price: u128,
    ) -> Vec<String> {
        let total_price = price * amount as u128;

        let mut location = String::new();

        let dealer = self.get_dealer_mut(nick).unwrap();
        dealer.money += total_price;
        dealer.sub_item_local(item_name, amount);
        location += &dealer.location;

        let location = self.locations.get_mut(&location).unwrap();
        let market_item = location.item_market.get_mut(item_name).unwrap();
        market_item.supply += amount;
        market_item.demand -= amount;

        vec![format!(
            "{}: you sold {} {} for {}",
            nick,
            amount,
            item_name,
            pretty_print_money(total_price)
        )]
    }

    pub fn _give_money(&mut self, nick: &str, bloke_nick: &str, money: u128) -> Vec<String> {
        let dealer = self.get_dealer_mut(nick).unwrap();
        dealer.money -= money;

        let bloke = self.get_dealer_mut(bloke_nick).unwrap();
        bloke.money += money;

        vec![format!(
            "{}: you gave {} {}",
            nick,
            bloke_nick,
            pretty_print_money(money),
        )]
    }

    pub fn _give_drug(
        &mut self,
        nick: &str,
        bloke_nick: &str,
        drug_name: &str,
        amount: usize,
    ) -> Vec<String> {
        let dealer = self.get_dealer_mut(nick).unwrap();
        dealer.sub_drug_local(drug_name, amount);

        let bloke = self.get_dealer_mut(bloke_nick).unwrap();
        bloke.add_drug_local(drug_name, amount, 0);

        vec![format!(
            "{}: you gave {} {} to {}",
            nick, amount, drug_name, bloke_nick
        )]
    }

    pub fn _give_item(
        &mut self,
        nick: &str,
        bloke_nick: &str,
        item_name: &str,
        amount: usize,
    ) -> Vec<String> {
        let dealer = self.get_dealer_mut(nick).unwrap();
        dealer.sub_item_local(item_name, amount);

        let bloke = self.get_dealer_mut(bloke_nick).unwrap();
        bloke.add_item_local(item_name, amount, 0);

        vec![format!(
            "{}: you gave {} {} to {}",
            nick, amount, item_name, bloke_nick
        )]
    }

    pub fn _fly_to(&mut self, nick: &str, destination_name: &str) -> Vec<String> {
        let dealer = self.get_dealer(nick).unwrap();
        let current_location = self.locations.get(&dealer.location).unwrap();
        let destination = self.locations.get(destination_name).unwrap();

        let price = get_flight_price(current_location, destination);

        let current_location = self.locations.get_mut(&dealer.location.clone()).unwrap();
        current_location.blokes.remove(nick);

        let dealer = self.get_dealer_mut(nick).unwrap();

        dealer.money -= price;
        dealer.status = DealerStatus::Flying;

        self.flights
            .insert(nick.to_string(), destination_name.to_owned());

        vec![format!(
            "{}: you take a flight to {} for {}. You'll arrive tomorrow",
            nick,
            destination_name,
            pretty_print_money(price)
        )]
    }

    pub fn prices_from(&self, current_location_name: &str) -> Vec<String> {
        let mut lines = vec![];

        let current_location = self.locations.get(current_location_name).unwrap();

        for (location_name, location) in &self.locations {
            if location_name.as_str() == current_location_name {
                continue;
            }

            let price = get_flight_price(current_location, location);

            lines.push(format!(
                "From `{}` to `{}` -> {}",
                current_location_name,
                location_name,
                pretty_print_money(price)
            ));
        }

        lines
    }

    pub fn _buy_capacity(&mut self, nick: &str, amount: usize) -> Vec<String> {
        let dealer = self.get_dealer_mut(nick).unwrap();

        let Some(price) = capacity_price(dealer.capacity, amount) else {
            return vec![
                format!("{}: You won't ever need that much capacity. Will you?", nick)
            ];
        };

        dealer.money -= price;
        dealer.capacity += amount;

        return vec![format!(
            "{}: You bought {} slots for {}",
            nick,
            amount,
            pretty_print_money(price)
        )];
    }
}
