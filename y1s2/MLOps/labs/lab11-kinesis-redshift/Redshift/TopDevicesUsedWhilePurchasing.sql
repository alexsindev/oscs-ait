SELECT
    device_type,
    COUNT(*) AS usage_count
FROM unnested_telemetry_vw
WHERE business_event_type = 'purchase'
GROUP BY device_type
ORDER BY usage_count DESC;