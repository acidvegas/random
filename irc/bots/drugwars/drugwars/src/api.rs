use crate::{drug_wars::DrugWars, dealer::Dealer, utils::{get_flight_price, capacity_price, pretty_print_money}};

impl DrugWars {
    pub fn register_dealer(&mut self, nick: &str) -> Vec<String> {
        if self.dealers.contains_key(nick) {
            return vec![format!(
                "{}: you're already registered you bloot clot donkey",
                nick
            )];
        }

        self.dealers.insert(nick.to_owned(), Dealer::random(self));

        let dealer = self.dealers.get(nick).unwrap();
        let location = self.locations.get_mut(&dealer.location).unwrap();

        location.blokes.insert(nick.to_owned());

        vec![format!("{}: get rich or die tryin", nick)]
    }


    pub fn show_page_for_nick(&self, nick: &str) -> Vec<String> {
        let Some(dealer) = self.get_dealer(nick) else {
            return self.dealer_not_registered(nick);
        };

        let mut lines = vec![];

        lines.append(&mut self.render_header(nick, dealer));
        if dealer.max_width >= 110 {
            lines.append(&mut self.render_drugs_dual_columns(dealer));
            lines.append(&mut self.render_items_dual_columns(dealer));    
        } else {
            lines.append(&mut self.render_drugs(dealer));
            lines.append(&mut self.render_items(dealer));
        }

        lines.append(&mut self.render_people(dealer));
        lines.append(&mut self.render_command_list(dealer));

        lines
    }

    pub fn set_dealer_max_width(&mut self, nick: &str, size: usize) -> Vec<String> {
        let Some(dealer) = self.get_dealer_mut(nick) else { return vec![
            format!("{}: You aren't playing yet you donkey", nick)
        ]; };

        dealer.max_width = size;
        vec![
            format!("{}: Changed your max width to {}", nick, size),
            "Your max width is now:".to_owned(),
            format!("├{}┤", "─".repeat(size - 2))
        ]
    }

    pub fn buy_drug(&mut self, nick: &str, drug_str: &str, amount: usize) -> Vec<String> {
        let drug_str = drug_str.to_lowercase();

        let Some(dealer) = self.get_dealer(nick) else { 
            return self.dealer_not_registered(nick);
        };

        if !dealer.available() {
            return self.dealer_not_available(nick);
        }

        let matching_drugs = self
            .drugs
            .iter()
            .filter(|(name, _)| name.to_lowercase().contains(&drug_str))
            .collect::<Vec<_>>();

        let len = matching_drugs.len();

        if len < 1 {
            return vec![format!("{}: Couldn't find your requested drug", nick)];
        }
        if len > 1 {
            return vec![format!("{}: The drug you requested is too ambiguous.", nick)];
        }

        let (drug_name, _) = matching_drugs[0];

        let location = self.locations.get(&dealer.location).unwrap();

        if !location.drug_market.contains_key(drug_name) {
            return vec![format!(
                "{}: There isn't any {} on the market today.",
                nick,
                drug_name
            )];
        }

        if dealer.get_total_drugs_local() + amount > dealer.capacity {
            return vec![
                format!("{}: You don't have enough capacity", nick)
            ]
        }

        let drug_at_market = location.drug_market.get(drug_name).unwrap();
        if drug_at_market.supply < amount {
            return vec![format!(
                "{}: There isn't enough supply of {} today.",
                nick,
                drug_name
            )];
        }

        let total_price = drug_at_market.price * amount as u128;

        if total_price > dealer.money {
            return vec![format!("{}: Not enough money you broke ass punk", nick)];
        }

        self._buy_drug(nick, &drug_name.clone(), amount, drug_at_market.price)
    }

    pub fn sell_drug(&mut self, nick: &str, drug_str: &str, amount: usize) -> Vec<String> {
        let drug_str = drug_str.to_lowercase();

        let Some(dealer) = self.get_dealer(nick) else { 
            return self.dealer_not_registered(nick);
        };

        if !dealer.available() {
            return self.dealer_not_available(nick);
        }

        let matching_drugs = self
            .drugs
            .iter()
            .filter(|(name, _)| name.to_lowercase().contains(&drug_str))
            .collect::<Vec<_>>();

        let len = matching_drugs.len();

        if len < 1 {
            return vec![format!("{}: Couldn't find your requested drug", nick)];
        }
        if len > 1 {
            return vec![format!("{}: The drug you requested is too ambiguous.", nick)];
        }

        let (drug_name, _) = matching_drugs[0];

        let location = self.locations.get(&dealer.location).unwrap();

        if !location.drug_market.contains_key(drug_name) {
            return vec![format!(
                "{}: There isn't any {} needed on the market today.",
                nick,
                drug_name
            )];
        }

        let drug_at_market = location.drug_market.get(drug_name).unwrap();
        if drug_at_market.demand < amount {
            return vec![format!(
                "{}: There isn't enough demand of {} today.",
                nick,
                drug_name
            )];
        }

        let owned_drugs_local = dealer.owned_drugs.get(&dealer.location).unwrap();

        if !owned_drugs_local.contains_key(drug_name) {
            return vec![format!(
                "{}: You don't have any {} here.",
                nick,
                drug_name
            )];
        }

        let owned_drug = owned_drugs_local.get(drug_name).unwrap();

        if owned_drug.amount < amount {
            return vec![format!(
                "{}: You don't have enough {} to sell.",
                nick,
                drug_name
            )];
        }

        self._sell_drug(nick, &drug_name.clone(), amount, drug_at_market.price)
    }


    pub fn buy_item(&mut self, nick: &str, item_str: &str, amount: usize) -> Vec<String> {
        let item_str = item_str.to_lowercase();

        let Some(dealer) = self.get_dealer(nick) else { 
            return self.dealer_not_registered(nick);
        };

        if !dealer.available() {
            return self.dealer_not_available(nick);
        }

        let matching_items = self
            .items
            .iter()
            .filter(|(name, _)| name.to_lowercase().contains(&item_str))
            .collect::<Vec<_>>();

        let len = matching_items.len();

        if len < 1 {
            return vec![format!("{}: Couldn't find your requested item", nick)];
        }
        if len > 1 {
            return vec![format!("{}: The item you requested is too ambiguous.", nick)];
        }

        let (item_name, _) = matching_items[0];

        let location = self.locations.get(&dealer.location).unwrap();

        if !location.item_market.contains_key(item_name) {
            return vec![format!(
                "{}: There isn't any {} on the market today.",
                nick,
                item_name
            )];
        }

        if dealer.get_total_items_local() + amount > dealer.capacity {
            return vec![
                format!("{}: You don't have enough capacity", nick)
            ]
        }

        let item_at_market = location.item_market.get(item_name).unwrap();
        if item_at_market.supply < amount {
            return vec![format!(
                "{}: There isn't enough supply of {} today.",
                nick,
                item_name
            )];
        }

        let total_price = item_at_market.price * amount as u128;

        if total_price > dealer.money {
            return vec![format!("{}: Not enough money you broke ass punk", nick)];
        }

        self._buy_item(nick, &item_name.clone(), amount, item_at_market.price)
    }

    pub fn sell_item(&mut self, nick: &str, item_str: &str, amount: usize) -> Vec<String> {
        let item_str = item_str.to_lowercase();

        let Some(dealer) = self.get_dealer(nick) else { 
            return self.dealer_not_registered(nick);
        };

        if !dealer.available() {
            return self.dealer_not_available(nick);
        }

        let matching_items = self
            .items
            .iter()
            .filter(|(name, _)| name.to_lowercase().contains(&item_str))
            .collect::<Vec<_>>();

        let len = matching_items.len();

        if len < 1 {
            return vec![format!("{}: Couldn't find your requested item", nick)];
        }
        if len > 1 {
            return vec![format!("{}: The item you requested is too ambiguous.", nick)];
        }

        let (item_name, _) = matching_items[0];

        let location = self.locations.get(&dealer.location).unwrap();

        if !location.item_market.contains_key(item_name) {
            return vec![format!(
                "{}: There isn't any {} needed on the market today.",
                nick,
                item_name
            )];
        }

        let item_at_market = location.item_market.get(item_name).unwrap();
        if item_at_market.demand < amount {
            return vec![format!(
                "{}: There isn't enough demand of {} today.",
                nick,
                item_name
            )];
        }

        let owned_items_local = dealer.owned_items.get(&dealer.location).unwrap();

        if !owned_items_local.contains_key(item_name) {
            return vec![format!(
                "{}: You don't have any {} here.",
                nick,
                item_name
            )];
        }

        let owned_item = owned_items_local.get(item_name).unwrap();

        if owned_item.amount < amount {
            return vec![format!(
                "{}: You don't have enough {} to sell.",
                nick,
                item_name
            )];
        }

        self._sell_item(nick, &item_name.clone(), amount, item_at_market.price)
    }

    pub fn give_money(&mut self, nick: &str, amount: f64, bloke_nick: &str) -> Vec<String> {
        let Some(dealer) = self.get_dealer(nick) else { 
            return self.dealer_not_registered(nick);
        };

        if !dealer.available() {
            return self.dealer_not_available(nick);
        }

        let Some(_) = self.get_dealer(bloke_nick) else { 
            return self.dealer_not_registered(nick);
        };

        let money = (amount * 10000.) as u128;

        if dealer.money < money {
            return vec![format!("{}: Not enough money you broke ass punk", nick)];   
        }

        self._give_money(nick, bloke_nick, money)
        
    }

    pub fn give_drug(&mut self, nick: &str, drug_str: &str, amount: usize, bloke_nick: &str) -> Vec<String> {
        let drug_str = drug_str.to_lowercase();

        let Some(dealer) = self.get_dealer(nick) else { 
            return self.dealer_not_registered(nick);
        };

        if !dealer.available() {
            return self.dealer_not_available(nick);
        }

        let Some(bloke) = self.get_dealer(bloke_nick) else { 
            return self.dealer_not_registered(nick);
        };

        if dealer.location != bloke.location {
            return vec![format!("{}: {} is not in {} currently.", nick, bloke_nick, dealer.location)];
        }

        let matching_drugs = self
            .drugs
            .iter()
            .filter(|(name, _)| name.to_lowercase().contains(&drug_str))
            .collect::<Vec<_>>();

        let len = matching_drugs.len();

        if len < 1 {
            return vec![format!("{}: Couldn't find your requested drug", nick)];
        }
        if len > 1 {
            return vec![format!("{}: The drug you requested is too ambiguous.", nick)];
        }

        let (drug_name, _) = matching_drugs[0];

        let owned_drugs_local = dealer.owned_drugs.get(&dealer.location).unwrap();

        if !owned_drugs_local.contains_key(drug_name) {
            return vec![format!(
                "{}: You don't have any {} here.",
                nick,
                drug_name
            )];
        }

        let owned_drug = owned_drugs_local.get(drug_name).unwrap();

        if owned_drug.amount < amount {
            return vec![format!(
                "{}: You don't have enough {} to sell.",
                nick,
                drug_name
            )];
        }

        if bloke.get_total_drugs_local() + amount > bloke.capacity {
            return vec![format!(
                "{}: {} don't have enough capacity",
                nick,
                bloke_nick
            )];
        }

        self._give_drug(nick, bloke_nick, &drug_name.clone(), amount)

    }

    pub fn give_item(&mut self, nick: &str, item_str: &str, amount: usize, bloke_nick: &str) -> Vec<String> {
        let item_str = item_str.to_lowercase();

        let Some(dealer) = self.get_dealer(nick) else { 
            return self.dealer_not_registered(nick);
        };

        if !dealer.available() {
            return self.dealer_not_available(nick);
        }

        let Some(bloke) = self.get_dealer(bloke_nick) else { 
            return self.dealer_not_registered(nick);
        };

        if dealer.location != bloke.location {
            return vec![format!("{}: {} is not in {} currently.", nick, bloke_nick, dealer.location)];
        }

        let matching_items = self
            .items
            .iter()
            .filter(|(name, _)| name.to_lowercase().contains(&item_str))
            .collect::<Vec<_>>();

        let len = matching_items.len();

        if len < 1 {
            return vec![format!("{}: Couldn't find your requested item", nick)];
        }
        if len > 1 {
            return vec![format!("{}: The item you requested is too ambiguous.", nick)];
        }

        let (item_name, _) = matching_items[0];

        let owned_items_local = dealer.owned_items.get(&dealer.location).unwrap();

        if !owned_items_local.contains_key(item_name) {
            return vec![format!(
                "{}: You don't have any {} here.",
                nick,
                item_name
            )];
        }

        let owned_item = owned_items_local.get(item_name).unwrap();

        if owned_item.amount < amount {
            return vec![format!(
                "{}: You don't have enough {} to sell.",
                nick,
                item_name
            )];
        }

        if bloke.get_total_items_local() + amount > bloke.capacity {
            return vec![format!(
                "{}: {} don't have enough capacity",
                nick,
                bloke_nick
            )];
        }

        self._give_item(nick, bloke_nick, &item_name.clone(), amount)
    }

    pub fn check_flight_prices(&self, nick: &str) -> Vec<String> {

        let Some(dealer) = self.get_dealer(nick) else {
            return self.dealer_not_registered(nick);
        };

        if !dealer.available() {
            return self.dealer_not_available(nick);
        }

        let mut lines = vec![];
        lines.push(format!("{}: Here are the flight prices:", nick));

        lines.append(&mut self.prices_from(&dealer.location));

        lines
    }

    pub fn fly_to(&mut self, nick: &str, destination_str: &str) -> Vec<String> {

        let destination_str = destination_str.to_lowercase();

        let Some(dealer) = self.get_dealer(nick) else { 
            return self.dealer_not_registered(nick);
        };

        if !dealer.available() {
            return self.dealer_not_available(nick);
        }

        let matching_destinations = self
            .locations
            .iter()
            .filter(|(name, _)| name.to_lowercase().contains(&destination_str))
            .collect::<Vec<_>>();

        let len = matching_destinations.len();

        if len < 1 {
            return vec![format!("{}: Couldn't find your requested destination", nick)];
        }
        if len > 1 {
            return vec![format!("{}: The destination you requested is too ambiguous.", nick)];
        }

        let current_location = self.locations.get(&dealer.location).unwrap();

        let (destination_name, destination) = matching_destinations[0];

        let price = get_flight_price(current_location, destination);

        if dealer.money < price {
            return vec![format!("{}: Not enough money you broke ass punk", nick)];
        }


        self._fly_to(nick, &destination_name.clone())
    }

    pub fn check_capacity_price(&mut self, nick: &str, amount: usize) -> Vec<String> {
        let Some(dealer) = self.get_dealer(nick) else {
            return self.dealer_not_registered(nick);
        };

        if !dealer.available() {
            return self.dealer_not_available(nick);
        }

        let Some(price) = capacity_price(dealer.capacity, amount) else {
            return vec![
                format!("{}: You won't ever need that much capacity. Will you?", nick)
            ];
        };

        return vec![
            format!("{}: It will cost you {} to buy {} slots", nick, pretty_print_money(price), amount)
        ]

    }

    pub fn buy_capacity(&mut self, nick: &str, amount: usize) -> Vec<String> {
        
        let Some(dealer) = self.get_dealer(nick) else {
            return self.dealer_not_registered(nick);
        };

        if !dealer.available() {
            return self.dealer_not_available(nick);
        }

        let Some(price) = capacity_price(dealer.capacity, amount) else {
            return vec![
                format!("{}: You won't ever need that much capacity. Will you?", nick)
            ];
        };

        if dealer.money < price {
            return vec![format!("{}: Not enough money you broke ass punk", nick)];
        }

        self._buy_capacity(nick, amount)
    }

}
