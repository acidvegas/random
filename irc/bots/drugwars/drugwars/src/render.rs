use chrono::Duration;
use itertools::Itertools;

use crate::{
    dealer::Dealer,
    drug_wars::DrugWars,
    utils::{pretty_print_money, truncate_string},
};

impl DrugWars {
    fn get_date_and_time(&self) -> String {
        let current_date = self.settings.current_day.format("%Y-%m-%d").to_string();

        let t = self.timer.elapsed().unwrap().as_secs_f32() / self.settings.day_duration as f32;

        let current_seconds = t * 86400.;

        let duration = Duration::seconds(current_seconds as i64);

        let current_time = format!(
            "{:0>2}:{:0>2}",
            duration.num_hours(),
            duration.num_minutes() - (60 * duration.num_hours())
        );

        format!("{} {}", current_date, current_time)
    }

    pub fn render_header(&self, nick: &str, dealer: &Dealer) -> Vec<String> {
        let mut lines = vec![];

        let date_nick_line = format!(
            "╭ {} ─ {} ─ {} ─ {} ─ {} ",
            self.get_date_and_time(),
            nick,
            pretty_print_money(dealer.money),
            dealer.location,
            dealer.print_status()
        );
        let top_box_line = "─".repeat(dealer.max_width - date_nick_line.chars().count() - 1);

        lines.push(format!("{}{}╮", date_nick_line, top_box_line));

        let location = self.locations.get(&dealer.location).unwrap();

        for msg in &location.messages {
            let start = format!("│ {}", msg);
            let spaces = " ".repeat(dealer.max_width - start.chars().count() - 1);

            lines.push(format!("{}{}│", start, spaces));
        }

        lines.push(format!("╰{}╯", "─".repeat(dealer.max_width - 2)));

        lines
    }

    pub fn render_drugs(&self, dealer: &Dealer) -> Vec<String> {
        let mut lines = vec![];

        let market_column_width = ((dealer.max_width - 4) as f32 / 4.).floor() as usize;
        let owned_column_width = ((dealer.max_width - 4) as f32 / 3.).floor() as usize;

        lines.push(format!(
            "╭ Drugs market {}╮",
            "─".repeat(dealer.max_width - 16)
        ));

        let mut market_header = String::new();
        for col_name in ["Drug", "Supply", "Demand", "Price"] {
            let spaces = " ".repeat(market_column_width - col_name.chars().count());
            market_header += &format!("{}{}", col_name, spaces);
        }

        market_header += &" ".repeat(dealer.max_width - market_header.chars().count() - 4);

        lines.push(format!("│ {} │", market_header));

        let location = self.locations.get(&dealer.location).unwrap();

        for (drug_name, drug) in &location.drug_market {
            let mut market_column = String::new();

            let value = truncate_string(&drug_name, market_column_width);
            let spaces = " ".repeat(market_column_width - value.chars().count());
            market_column += &format!("{}{}", value, spaces);

            let value = truncate_string(&format!("{}", drug.supply), market_column_width);
            let spaces = " ".repeat(market_column_width - value.chars().count());
            market_column += &format!("{}{}", value, spaces);

            let value = truncate_string(&format!("{}", drug.demand), market_column_width);
            let spaces = " ".repeat(market_column_width - value.chars().count());
            market_column += &format!("{}{}", value, spaces);

            let value = truncate_string(
                &format!("{}", pretty_print_money(drug.price)),
                market_column_width,
            );
            let spaces = " ".repeat(market_column_width - value.chars().count());
            market_column += &format!("{}{}", value, spaces);

            market_column += &" ".repeat(dealer.max_width - market_column.chars().count() - 4);

            lines.push(format!("│ {} │", market_column));
        }

        lines.push(format!("╰{}╯", "─".repeat(dealer.max_width - 2)));

        let mut header_line = format!(
            "╭ Owned drugs ({}/{})",
            dealer.get_total_drugs_local(),
            dealer.capacity
        );

        header_line += &format!(
            "{}╮",
            "─".repeat(dealer.max_width - header_line.chars().count() - 1)
        );
        lines.push(header_line);

        let mut owned_header = String::new();
        for col_name in ["Drug", "Amount", "Bought at"] {
            let spaces = " ".repeat(owned_column_width - col_name.chars().count());
            owned_header += &format!("{}{}", col_name, spaces);
        }

        owned_header += &" ".repeat(dealer.max_width - owned_header.chars().count() - 4);

        lines.push(format!("│ {} │", owned_header));

        let owned_local = dealer.get_local_drugs();

        for (drug_name, drug) in owned_local {
            let mut owned_column = String::new();

            let value = truncate_string(&drug_name, owned_column_width);
            let spaces = " ".repeat(owned_column_width - value.chars().count());
            owned_column += &format!("{}{}", value, spaces);

            let value = truncate_string(&format!("{}", drug.amount), owned_column_width);
            let spaces = " ".repeat(owned_column_width - value.chars().count());
            owned_column += &format!("{}{}", value, spaces);

            let value = truncate_string(
                &format!("{}", pretty_print_money(drug.bought_at)),
                owned_column_width,
            );
            let spaces = " ".repeat(owned_column_width - value.chars().count());
            owned_column += &format!("{}{}", value, spaces);

            owned_column += &" ".repeat(dealer.max_width - owned_column.chars().count() - 4);

            lines.push(format!("│ {} │", owned_column));
        }

        lines.push(format!("╰{}╯", "─".repeat(dealer.max_width - 2)));

        lines
    }

    pub fn render_items(&self, dealer: &Dealer) -> Vec<String> {
        let mut lines = vec![];

        let market_column_width = ((dealer.max_width - 4) as f32 / 4.).floor() as usize;
        let owned_column_width = ((dealer.max_width - 4) as f32 / 3.).floor() as usize;

        lines.push(format!(
            "╭ Items market {}╮",
            "─".repeat(dealer.max_width - 16)
        ));

        let mut market_header = String::new();
        for col_name in ["Item", "Supply", "Demand", "Price"] {
            let spaces = " ".repeat(market_column_width - col_name.chars().count());
            market_header += &format!("{}{}", col_name, spaces);
        }

        market_header += &" ".repeat(dealer.max_width - market_header.chars().count() - 4);

        lines.push(format!("│ {} │", market_header));

        let location = self.locations.get(&dealer.location).unwrap();

        for (item_name, item) in &location.item_market {
            let mut market_column = String::new();

            let value = truncate_string(&item_name, market_column_width);
            let spaces = " ".repeat(market_column_width - value.chars().count());
            market_column += &format!("{}{}", value, spaces);

            let value = truncate_string(&format!("{}", item.supply), market_column_width);
            let spaces = " ".repeat(market_column_width - value.chars().count());
            market_column += &format!("{}{}", value, spaces);

            let value = truncate_string(&format!("{}", item.demand), market_column_width);
            let spaces = " ".repeat(market_column_width - value.chars().count());
            market_column += &format!("{}{}", value, spaces);

            let value = truncate_string(
                &format!("{}", pretty_print_money(item.price)),
                market_column_width,
            );
            let spaces = " ".repeat(market_column_width - value.chars().count());
            market_column += &format!("{}{}", value, spaces);

            market_column += &" ".repeat(dealer.max_width - market_column.chars().count() - 4);

            lines.push(format!("│ {} │", market_column));
        }

        lines.push(format!("╰{}╯", "─".repeat(dealer.max_width - 2)));

        let mut header_line = format!(
            "╭ Owned items ({}/{})",
            dealer.get_total_drugs_local(),
            dealer.capacity
        );

        header_line += &format!(
            "{}╮",
            "─".repeat(dealer.max_width - header_line.chars().count() - 1)
        );
        lines.push(header_line);

        let mut owned_header = String::new();
        for col_name in ["Item", "Amount", "Bought at"] {
            let spaces = " ".repeat(owned_column_width - col_name.chars().count());
            owned_header += &format!("{}{}", col_name, spaces);
        }

        owned_header += &" ".repeat(dealer.max_width - owned_header.chars().count() - 4);

        lines.push(format!("│ {} │", owned_header));

        let owned_local = dealer.get_local_drugs();

        for (item_name, item) in owned_local {
            let mut owned_column = String::new();

            let value = truncate_string(&item_name, owned_column_width);
            let spaces = " ".repeat(owned_column_width - value.chars().count());
            owned_column += &format!("{}{}", value, spaces);

            let value = truncate_string(&format!("{}", item.amount), owned_column_width);
            let spaces = " ".repeat(owned_column_width - value.chars().count());
            owned_column += &format!("{}{}", value, spaces);

            let value = truncate_string(
                &format!("{}", pretty_print_money(item.bought_at)),
                owned_column_width,
            );
            let spaces = " ".repeat(owned_column_width - value.chars().count());
            owned_column += &format!("{}{}", value, spaces);

            owned_column += &" ".repeat(dealer.max_width - owned_column.chars().count() - 4);

            lines.push(format!("│ {} │", owned_column));
        }

        lines.push(format!("╰{}╯", "─".repeat(dealer.max_width - 2)));
        lines
    }

    pub fn render_drugs_dual_columns(&self, dealer: &Dealer) -> Vec<String> {
        let mut lines = vec![];

        let market_width = dealer.max_width / 2;
        let owned_width = dealer.max_width / 2;

        let market_column_width = ((market_width - 2) as f32 / 4.).floor() as usize;
        let owned_column_width = ((owned_width - 2) as f32 / 3.).floor() as usize;

        let mut header_line = format!(
            "╭ Drugs market {}┬ Owned drugs ({}/{}) ",
            "─".repeat(market_width - 16),
            dealer.get_total_drugs_local(),
            dealer.capacity,
        );

        header_line += &format!(
            "{}╮",
            "─".repeat(dealer.max_width - header_line.chars().count() - 1)
        );

        lines.push(header_line);

        // Market column headers
        let mut market_header = String::new();
        for col_name in ["Drug", "Supply", "Demand", "Price"] {
            let spaces = " ".repeat(market_column_width - col_name.chars().count());
            market_header += &format!("{}{}", col_name, spaces);
        }

        println!(
            "mw: {}, mh: {}",
            market_width,
            market_header.chars().count()
        );
        let offset = (market_width - market_header.chars().count()).min(3);

        market_header += &" ".repeat(market_width - market_header.chars().count() - offset);

        // Owned column headers
        let mut owned_header = String::new();
        for col_name in ["Drug", "Amount", "Bought at"] {
            let spaces = " ".repeat(owned_column_width - col_name.chars().count());
            owned_header += &format!("{}{}", col_name, spaces);
        }

        let offset = (owned_width - owned_header.chars().count()).min(2);
        owned_header += &" ".repeat(owned_width - owned_header.chars().count() - offset);

        lines.push(format!("│ {}│ {}│", market_header, owned_header));

        let location = self.locations.get(&dealer.location).unwrap();

        let owned_local = dealer.get_local_drugs();

        for pair in location.drug_market.iter().zip_longest(owned_local.iter()) {
            match pair {
                itertools::EitherOrBoth::Both(market, owned) => {
                    // Market column
                    let mut market_column = String::new();

                    let value = truncate_string(market.0, market_column_width);
                    let spaces = " ".repeat(market_column_width - value.chars().count());
                    market_column += &format!("{}{}", value, spaces);

                    let value =
                        truncate_string(&format!("{}", market.1.supply), market_column_width);
                    let spaces = " ".repeat(market_column_width - value.chars().count());
                    market_column += &format!("{}{}", value, spaces);

                    let value =
                        truncate_string(&format!("{}", market.1.demand), market_column_width);
                    let spaces = " ".repeat(market_column_width - value.chars().count());
                    market_column += &format!("{}{}", value, spaces);

                    let value = truncate_string(
                        &format!("{}", pretty_print_money(market.1.price)),
                        market_column_width,
                    );
                    let spaces = " ".repeat(market_column_width - value.chars().count());
                    market_column += &format!("{}{}", value, spaces);

                    let offset = (market_width - market_column.chars().count()).min(3);
                    market_column +=
                        &" ".repeat(market_width - market_column.chars().count() - offset);

                    // Owned column
                    let mut owned_column = String::new();

                    let value = truncate_string(owned.0, owned_column_width);
                    let spaces = " ".repeat(owned_column_width - value.chars().count());
                    owned_column += &format!("{}{}", value, spaces);

                    let value = truncate_string(&format!("{}", owned.1.amount), owned_column_width);
                    let spaces = " ".repeat(owned_column_width - value.chars().count());
                    owned_column += &format!("{}{}", value, spaces);

                    let value = truncate_string(
                        &format!("{}", pretty_print_money(owned.1.bought_at)),
                        owned_column_width,
                    );
                    let spaces = " ".repeat(owned_column_width - value.chars().count());
                    owned_column += &format!("{}{}", value, spaces);

                    let offset = (owned_width - owned_column.chars().count()).min(2);
                    owned_column +=
                        &" ".repeat(owned_width - owned_column.chars().count() - offset);

                    lines.push(format!("│ {}│ {}│", market_column, owned_column));
                }
                itertools::EitherOrBoth::Left(market) => {
                    // Market column
                    let mut market_column = String::new();

                    let value = truncate_string(market.0, market_column_width);
                    let spaces = " ".repeat(market_column_width - value.chars().count());
                    market_column += &format!("{}{}", value, spaces);

                    let value =
                        truncate_string(&format!("{}", market.1.supply), market_column_width);
                    let spaces = " ".repeat(market_column_width - value.chars().count());
                    market_column += &format!("{}{}", value, spaces);

                    let value =
                        truncate_string(&format!("{}", market.1.demand), market_column_width);
                    let spaces = " ".repeat(market_column_width - value.chars().count());
                    market_column += &format!("{}{}", value, spaces);

                    let value = truncate_string(
                        &format!("{}", pretty_print_money(market.1.price)),
                        market_column_width,
                    );
                    let spaces = " ".repeat(market_column_width - value.chars().count());
                    market_column += &format!("{}{}", value, spaces);

                    let offset = (market_width - market_column.chars().count()).min(3);
                    market_column +=
                        &" ".repeat(market_width - market_column.chars().count() - offset);

                    lines.push(format!(
                        "│ {}│ {}│",
                        market_column,
                        " ".repeat(owned_width - 2)
                    ));
                }
                itertools::EitherOrBoth::Right(owned) => {
                    // Owned column
                    let mut owned_column = String::new();

                    let value = truncate_string(owned.0, owned_column_width);
                    let spaces = " ".repeat(owned_column_width - value.chars().count());
                    owned_column += &format!("{}{}", value, spaces);

                    let value = truncate_string(&format!("{}", owned.1.amount), owned_column_width);
                    let spaces = " ".repeat(owned_column_width - value.chars().count());
                    owned_column += &format!("{}{}", value, spaces);

                    let value = truncate_string(
                        &format!("{}", pretty_print_money(owned.1.bought_at)),
                        owned_column_width,
                    );
                    let spaces = " ".repeat(owned_column_width - value.chars().count());
                    owned_column += &format!("{}{}", value, spaces);

                    lines.push(format!(
                        "│ {}│ {}│",
                        " ".repeat(market_width - 3),
                        owned_column
                    ));
                }
            }
        }

        lines.push(format!(
            "╰{}┴{}╯",
            "─".repeat(market_width - 2),
            "─".repeat(owned_width - 1)
        ));

        lines
    }

    pub fn render_items_dual_columns(&self, dealer: &Dealer) -> Vec<String> {
        let mut lines = vec![];

        let market_width = dealer.max_width / 2;
        let owned_width = dealer.max_width / 2;

        let market_column_width = ((market_width - 2) as f32 / 4.).floor() as usize;
        let owned_column_width = ((owned_width - 2) as f32 / 3.).floor() as usize;

        lines.push(format!(
            "╭ Items market {}┬ Owned items {}╮",
            "─".repeat(market_width - 16),
            "─".repeat(owned_width - 14)
        ));

        // Market column headers
        let mut market_header = String::new();
        for col_name in ["Item", "Supply", "Demand", "Price"] {
            let spaces = " ".repeat(market_column_width - col_name.chars().count());
            market_header += &format!("{}{}", col_name, spaces);
        }

        let offset = (market_width - market_header.chars().count()).min(3);
        market_header += &" ".repeat(market_width - market_header.chars().count() - offset);

        // Owned column headers
        let mut owned_header = String::new();
        for col_name in ["Item", "Amount", "Bought at"] {
            let spaces = " ".repeat(owned_column_width - col_name.chars().count());
            owned_header += &format!("{}{}", col_name, spaces);
        }

        let offset = (owned_width - owned_header.chars().count()).min(2);
        owned_header += &" ".repeat(owned_width - owned_header.chars().count() - offset);

        lines.push(format!("│ {}│ {}│", market_header, owned_header));

        let location = self.locations.get(&dealer.location).unwrap();

        let owned_local = dealer.get_local_items();

        for pair in location.item_market.iter().zip_longest(owned_local.iter()) {
            match pair {
                itertools::EitherOrBoth::Both(market, owned) => {
                    // Market column
                    let mut market_column = String::new();

                    let value = truncate_string(market.0, market_column_width);
                    let spaces = " ".repeat(market_column_width - value.chars().count());
                    market_column += &format!("{}{}", value, spaces);

                    let value =
                        truncate_string(&format!("{}", market.1.supply), market_column_width);
                    let spaces = " ".repeat(market_column_width - value.chars().count());
                    market_column += &format!("{}{}", value, spaces);

                    let value =
                        truncate_string(&format!("{}", market.1.demand), market_column_width);
                    let spaces = " ".repeat(market_column_width - value.chars().count());
                    market_column += &format!("{}{}", value, spaces);

                    let value = truncate_string(
                        &format!("{}", pretty_print_money(market.1.price)),
                        market_column_width,
                    );
                    let spaces = " ".repeat(market_column_width - value.chars().count());
                    market_column += &format!("{}{}", value, spaces);

                    let offset = (market_width - market_column.chars().count()).min(3);
                    market_column +=
                        &" ".repeat(market_width - market_column.chars().count() - offset);

                    // Owned column
                    let mut owned_column = String::new();

                    let value = truncate_string(owned.0, owned_column_width);
                    let spaces = " ".repeat(owned_column_width - value.chars().count());
                    owned_column += &format!("{}{}", value, spaces);

                    let value = truncate_string(&format!("{}", owned.1.amount), owned_column_width);
                    let spaces = " ".repeat(owned_column_width - value.chars().count());
                    owned_column += &format!("{}{}", value, spaces);

                    let value = truncate_string(
                        &format!("{}", pretty_print_money(owned.1.bought_at)),
                        owned_column_width,
                    );
                    let spaces = " ".repeat(owned_column_width - value.chars().count());
                    owned_column += &format!("{}{}", value, spaces);

                    let offset = (owned_width - owned_column.chars().count()).min(2);
                    owned_column +=
                        &" ".repeat(owned_width - owned_column.chars().count() - offset);

                    lines.push(format!("│ {}│ {}│", market_column, owned_column));
                }
                itertools::EitherOrBoth::Left(market) => {
                    // Market column
                    let mut market_column = String::new();

                    let value = truncate_string(market.0, market_column_width);
                    let spaces = " ".repeat(market_column_width - value.chars().count());
                    market_column += &format!("{}{}", value, spaces);

                    let value =
                        truncate_string(&format!("{}", market.1.supply), market_column_width);
                    let spaces = " ".repeat(market_column_width - value.chars().count());
                    market_column += &format!("{}{}", value, spaces);

                    let value =
                        truncate_string(&format!("{}", market.1.demand), market_column_width);
                    let spaces = " ".repeat(market_column_width - value.chars().count());
                    market_column += &format!("{}{}", value, spaces);

                    let value = truncate_string(
                        &format!("{}", pretty_print_money(market.1.price)),
                        market_column_width,
                    );
                    let spaces = " ".repeat(market_column_width - value.chars().count() - 1);
                    market_column += &format!("{}{}", value, spaces);

                    let offset = (market_width - market_column.chars().count()).min(3);
                    market_column +=
                        &" ".repeat(market_width - market_column.chars().count() - offset);

                    lines.push(format!(
                        "│ {}│ {}│",
                        market_column,
                        " ".repeat(owned_width - 2)
                    ));
                }
                itertools::EitherOrBoth::Right(owned) => {
                    // Owned column
                    let mut owned_column = String::new();

                    let value = truncate_string(owned.0, owned_column_width);
                    let spaces = " ".repeat(owned_column_width - value.chars().count());
                    owned_column += &format!("{}{}", value, spaces);

                    let value = truncate_string(&format!("{}", owned.1.amount), owned_column_width);
                    let spaces = " ".repeat(owned_column_width - value.chars().count());
                    owned_column += &format!("{}{}", value, spaces);

                    let value = truncate_string(
                        &format!("{}", pretty_print_money(owned.1.bought_at)),
                        owned_column_width,
                    );
                    let spaces = " ".repeat(owned_column_width - value.chars().count());
                    owned_column += &format!("{}{}", value, spaces);

                    let offset = (owned_width - owned_column.chars().count()).min(2);
                    owned_column +=
                        &" ".repeat(owned_width - owned_column.chars().count() - offset);

                    lines.push(format!(
                        "│ {}│ {}│",
                        " ".repeat(market_width - 3),
                        owned_column
                    ));
                }
            }
        }

        lines.push(format!(
            "╰{}┴{}╯",
            "─".repeat(market_width - 2),
            "─".repeat(owned_width - 1)
        ));

        lines
    }

    pub fn render_people(&self, dealer: &Dealer) -> Vec<String> {
        let mut lines = vec![];

        lines.push(format!(
            "╭ Blokes in town {}╮",
            "─".repeat(dealer.max_width - 18)
        ));

        let location = self.locations.get(&dealer.location).unwrap();

        let mut blokes = location.blokes.iter().collect::<Vec<_>>();

        let mut line = String::new();

        while blokes.len() > 0 {
            let to_append = format!("{}, ", blokes[blokes.len() - 1]);

            if line.chars().count() + to_append.chars().count() > dealer.max_width - 2 {
                line.truncate(line.len() - 2);

                let start = format!("│ {}", line);
                let spaces = " ".repeat(dealer.max_width - start.chars().count() - 2);
                lines.push(format!("{}{} │", start, spaces));

                line = String::new();
            }

            line += &to_append;
            blokes.pop();
        }

        if line.chars().count() > 0 {
            line.truncate(line.len() - 2);
            let start = format!("│ {}", line);
            let spaces = " ".repeat(dealer.max_width - start.chars().count() - 2);
            lines.push(format!("{}{} │", start, spaces));
        }

        lines.push(format!("╰{}╯", "─".repeat(dealer.max_width - 2)));
        lines
    }

    pub fn render_command_list(&self, dealer: &Dealer) -> Vec<String> {
        let mut lines = vec![];

        lines.push(format!(
            "╭ Command list {}╮",
            "─".repeat(dealer.max_width - 16)
        ));

        let mut help_commands = vec![
            "s <drug> <amount> <location>: ship drug to location",
            "fp: flight prices",
            "f <location>: fly to location",
            "gm <bloke> <amount>: give money to some bloke",
            "gd <bloke> <drug> <amount>: give drugs to some bloke",
            "gi <bloke> <item> <amount>: give items to some bloke",
            "si <item> <amount>: sell item",
            "bi <item> <amount>: buy item",
            "sd <drug> <amount>: sell drug",
            "bd <drug> <amount>: buy drug",
            "bc <amount>: buy capacity",
            "mw <size>: set max width",
            "p: print info",
        ];

        let mut line = String::new();

        while help_commands.len() > 0 {
            let to_append = format!("{}, ", help_commands[help_commands.len() - 1]);

            if line.chars().count() + to_append.chars().count() > dealer.max_width - 2 {
                line.truncate(line.len() - 2);

                let start = format!("│ {}", line);
                let spaces = " ".repeat(dealer.max_width - start.chars().count() - 2);
                lines.push(format!("{}{} │", start, spaces));

                line = String::new();
            }

            line += &to_append;
            help_commands.pop();
        }

        if line.chars().count() > 0 {
            line.truncate(line.len() - 2);
            let start = format!("│ {}", line);
            let spaces = " ".repeat(dealer.max_width - start.chars().count() - 2);
            lines.push(format!("{}{} │", start, spaces));
        }

        lines.push(format!("╰{}╯", "─".repeat(dealer.max_width - 2)));
        lines
    }
}
