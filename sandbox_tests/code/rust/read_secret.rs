use std::error::Error;
use std::fs::File;
use std::io::prelude::*;

fn main() {
    let mut file = match File::open("{{ SECRET_FILE }}") {
        Err(why) => panic!("couldn't open: {}", Error::description(&why)),
        Ok(file) => file,
    };
    let mut s = String::new();
    match file.read_to_string(&mut s) {
        Err(why) => panic!("couldn't read: {}", Error::description(&why)),
        Ok(_) => print!("{}", s),
    }
}
