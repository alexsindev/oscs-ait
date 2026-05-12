CREATE TABLE fleet_registry (
    aircraft_id       VARCHAR(10),
    tail_number       VARCHAR(12),
    aircraft_model    VARCHAR(30),
    airline           VARCHAR(40),
    manufacture_year  INT,
    engine_type       VARCHAR(20),
    seat_capacity     INT,
    PRIMARY KEY (aircraft_id)
)