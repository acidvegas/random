use std::{f32::consts::PI, str};

use crate::definitions::Location;

pub fn truncate_string(original: &str, max: usize) -> String {
    assert!(max > 3);

    if original.chars().count() <= max {
        return original.to_owned();
    }

    format!("{}...", &original[..(max - 3)])
}

pub fn pretty_print_money(money: u128) -> String {
    let unit_money = money / 10000;
    let float_money = money as f32 / 10000.;
    let dec = (float_money.fract() * 100.).floor() as u32;

    let pretty_money = unit_money
        .to_string()
        .as_bytes()
        .rchunks(3)
        .rev()
        .map(str::from_utf8)
        .collect::<Result<Vec<&str>, _>>()
        .unwrap()
        .join(",");

    format!("${}.{:0>2}", pretty_money, dec)
}

pub fn get_flight_price(origin: &Location, other: &Location) -> u128 {
    let cur_lat = origin.lat * (PI / 180.);
    let cur_long = origin.long * (PI / 180.);

    let other_lat = other.lat * (PI / 180.);
    let other_long = other.long * (PI / 180.);

    let float_price = (cur_lat.sin() * other_lat.sin()
        + cur_lat.cos() * other_lat.cos() * (other_long - cur_long).cos())
    .acos()
        * 10000.;

    (float_price * 10000.) as u128
}

pub fn capacity_price(current_capacity: usize, to_add: usize) -> Option<u128> {
    let mut price: u128 = 1000 * 10000;

    for _ in 0..current_capacity {
        price += price / 1000000;
    }

    let mut accumulated_price: u128 = 0;

    for _ in current_capacity..(current_capacity + to_add) {
        price += price / 1000000;
        accumulated_price = match accumulated_price.checked_add(price) {
            Some(v) => v,
            None => return None,
        }
    }

    Some(accumulated_price)
}
