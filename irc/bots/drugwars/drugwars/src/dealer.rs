use std::collections::HashMap;

use rand::seq::IteratorRandom;

use crate::{
    definitions::{DealerStatus, OwnedDrug, OwnedItem},
    drug_wars::DrugWars,
};

pub struct Dealer {
    pub money: u128,
    pub location: String,
    pub capacity: usize,
    pub owned_drugs: HashMap<String, HashMap<String, OwnedDrug>>,
    pub owned_items: HashMap<String, HashMap<String, OwnedItem>>,
    pub max_width: usize,
    pub status: DealerStatus,
}

impl Dealer {
    pub fn random(drug_wars: &DrugWars) -> Self {
        let mut rng = rand::thread_rng();

        let mut owned_drugs = HashMap::default();
        let mut owned_items = HashMap::default();

        for (name, _) in &drug_wars.locations {
            owned_drugs.insert(name.clone(), HashMap::default());
            owned_items.insert(name.clone(), HashMap::default());
        }

        let location_name = drug_wars.locations.keys().choose(&mut rng).unwrap();

        Self {
            money: 100000000000,
            location: location_name.clone(),
            capacity: 10,
            owned_drugs,
            owned_items,
            max_width: 110,
            status: DealerStatus::Available,
        }
    }

    pub fn available(&self) -> bool {
        self.status == DealerStatus::Available
    }

    pub fn get_local_drugs(&self) -> &HashMap<String, OwnedDrug> {
        self.owned_drugs.get(&self.location).unwrap()
    }

    pub fn get_local_items(&self) -> &HashMap<String, OwnedItem> {
        self.owned_items.get(&self.location).unwrap()
    }

    pub fn get_total_drugs_local(&self) -> usize {
        self.get_total_drugs_at(&self.location)
    }

    pub fn get_total_drugs_at(&self, location: &str) -> usize {
        self.owned_drugs
            .get(location)
            .unwrap()
            .iter()
            .map(|(_, drug)| drug.amount)
            .sum()
    }

    pub fn get_total_items_local(&self) -> usize {
        self.get_total_items_at(&self.location)
    }

    pub fn get_total_items_at(&self, location: &str) -> usize {
        self.owned_items
            .get(location)
            .unwrap()
            .iter()
            .map(|(_, drug)| drug.amount)
            .sum()
    }

    pub fn print_status(&self) -> &str {
        match self.status {
            DealerStatus::Available => "Available",
            DealerStatus::Flying => "Flying",
        }
    }

    pub fn add_drug_local(&mut self, drug_name: &str, amount: usize, bought_at: u128) {
        let location = self.location.clone();
        self.add_drug_at(&location, drug_name, amount, bought_at)
    }

    pub fn add_drug_at(&mut self, location: &str, drug_name: &str, amount: usize, bought_at: u128) {
        let owned_drugs = self.owned_drugs.get_mut(location).unwrap();

        let owned_drug = match owned_drugs.entry(drug_name.to_owned()) {
            std::collections::hash_map::Entry::Occupied(o) => o.into_mut(),
            std::collections::hash_map::Entry::Vacant(v) => v.insert(OwnedDrug {
                amount: 0,
                bought_at: 0,
            }),
        };

        let average_price = (owned_drug.amount as u128 * owned_drug.bought_at
            + amount as u128 * bought_at)
            / (owned_drug.amount as u128 + amount as u128);

        owned_drug.amount += amount;
        owned_drug.bought_at = average_price;
    }

    pub fn sub_drug_local(&mut self, drug_name: &str, amount: usize) {
        let location = self.location.clone();
        self.sub_drug_at(&location, drug_name, amount);
    }

    pub fn sub_drug_at(&mut self, location: &str, drug_name: &str, amount: usize) {
        let owned_drugs = self.owned_drugs.get_mut(location).unwrap();

        let owned_drug = match owned_drugs.entry(drug_name.to_owned()) {
            std::collections::hash_map::Entry::Occupied(o) => o.into_mut(),
            std::collections::hash_map::Entry::Vacant(v) => v.insert(OwnedDrug {
                amount: 0,
                bought_at: 0,
            }),
        };

        owned_drug.amount -= amount;
    }

    pub fn add_item_local(&mut self, item_name: &str, amount: usize, bought_at: u128) {
        let location = self.location.clone();
        self.add_item_at(&location, item_name, amount, bought_at)
    }

    pub fn add_item_at(&mut self, location: &str, item_name: &str, amount: usize, bought_at: u128) {
        let owned_items = self.owned_items.get_mut(location).unwrap();

        let owned_item = match owned_items.entry(item_name.to_owned()) {
            std::collections::hash_map::Entry::Occupied(o) => o.into_mut(),
            std::collections::hash_map::Entry::Vacant(v) => v.insert(OwnedItem {
                amount: 0,
                bought_at: 0,
            }),
        };

        let average_price = (owned_item.amount as u128 * owned_item.bought_at
            + amount as u128 * bought_at)
            / (owned_item.amount as u128 + amount as u128);

        owned_item.amount += amount;
        owned_item.bought_at = average_price;
    }

    pub fn sub_item_local(&mut self, item_name: &str, amount: usize) {
        let location = self.location.clone();
        self.sub_item_at(&location, item_name, amount);
    }

    pub fn sub_item_at(&mut self, location: &str, item_name: &str, amount: usize) {
        let owned_items = self.owned_items.get_mut(location).unwrap();

        let owned_item = match owned_items.entry(item_name.to_owned()) {
            std::collections::hash_map::Entry::Occupied(o) => o.into_mut(),
            std::collections::hash_map::Entry::Vacant(v) => v.insert(OwnedItem {
                amount: 0,
                bought_at: 0,
            }),
        };

        owned_item.amount -= amount;
    }
}
