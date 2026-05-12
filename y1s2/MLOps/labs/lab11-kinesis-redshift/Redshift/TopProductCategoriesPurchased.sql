SELECT
    product_category,
    COUNT(*) AS purchases
FROM unnested_telemetry_vw
WHERE business_event_type = 'purchase'
GROUP BY product_category
ORDER BY purchases DESC;