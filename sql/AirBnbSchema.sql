/*******************

  Create the schema

********************/

CREATE TABLE users (
  user_id VARCHAR(50) PRIMARY KEY, 
  email VARCHAR(50) UNIQUE NOT NULL,
  first_name VARCHAR(50) NOT NULL,
  last_name VARCHAR(50) NOT NULL,
  password VARCHAR(50) NOT NULL);

CREATE TABLE hosts( 
  host_id VARCHAR(50) PRIMARY KEY REFERENCES users(user_id) ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED);

CREATE TABLE countries(
  country_code VARCHAR(10) UNIQUE NOT NULL, 
  name VARCHAR(50) PRIMARY KEY);

CREATE TABLE cities(
  name VARCHAR(50),
  country VARCHAR(50) REFERENCES countries(name) ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED,
  PRIMARY KEY(name,country)
);

CREATE TABLE place(
  host_id VARCHAR(50) REFERENCES hosts(host_id) ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED, 
  address VARCHAR(50) PRIMARY KEY, 
  city_id VARCHAR(50) NOT NULL,
  price_per_night DECIMAL (10,2) NOT NULL CHECK (price_per_night >= 0),
  country_id VARCHAR(50) NOT NULL,
  FOREIGN KEY (city_id,country_id) REFERENCES cities(name,country) ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED
);



CREATE TABLE bookings (
  booking_id VARCHAR(64) PRIMARY KEY, 
  user_id VARCHAR(50) REFERENCES users(user_id) ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED,
  place_id VARCHAR(50) REFERENCES place(address) ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED, 
  start_date date NOT NULL, 
  end_date date NOT NULL CHECK(end_date >= start_date));

CREATE TABLE reviews(
  booking_id VARCHAR(64) PRIMARY KEY REFERENCES bookings(booking_id) ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED, 
  rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
  review TEXT);


