CREATE TABLE maintenance_event_summary (
    aircraft_id          VARCHAR(10),
    ata_chapter          VARCHAR(4),
    ata_system_name      VARCHAR(40),
    critical_event_count BIGINT,
    total_downtime_hrs   DOUBLE PRECISION,
    avg_downtime_hrs     DOUBLE PRECISION,
    total_labor_hrs      DOUBLE PRECISION,
    total_cost           DOUBLE PRECISION,
    avg_cost_per_event   DOUBLE PRECISION
)