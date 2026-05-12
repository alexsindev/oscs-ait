CREATE TABLE fleet_reliability_report AS
SELECT
    f.aircraft_model,
    f.engine_type,
    f.airline,
    m.ata_chapter,
    m.ata_system_name,
    SUM(m.critical_event_count) AS total_events,
    ROUND(AVG(m.avg_downtime_hrs), 1) AS avg_downtime_hrs,
    ROUND(SUM(m.total_labor_hrs), 1) AS total_labor_hrs,
    ROUND(SUM(m.total_cost), 2) AS total_cost,
    ROUND(AVG(m.avg_cost_per_event), 2) AS avg_cost_per_event,
    COUNT(DISTINCT m.aircraft_id) AS fleet_size
FROM maintenance_event_summary m
INNER JOIN fleet_registry f ON m.aircraft_id = f.aircraft_id
GROUP BY
    f.aircraft_model,
    f.engine_type,
    f.airline,
    m.ata_chapter,
    m.ata_system_name;