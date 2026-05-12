SELECT
    approximate_arrival_timestamp,
    partition_key,
    shard_id,
    sequence_number,

    json_extract_path_text(json_serialize(payload), 'eventID') AS event_id,
    json_extract_path_text(json_serialize(payload), 'eventName') AS event_name,
    json_extract_path_text(json_serialize(payload), 'awsRegion') AS aws_region,
    json_extract_path_text(json_serialize(payload), 'tableName') AS table_name,
    json_extract_path_text(json_serialize(payload), 'eventSource') AS event_source,

    json_extract_path_text(json_serialize(payload), 'dynamodb', 'Keys', 'user_id', 'S') AS user_id,
    json_extract_path_text(json_serialize(payload), 'dynamodb', 'Keys', 'timestamp', 'S') AS record_timestamp,

    json_extract_path_text(json_serialize(payload), 'dynamodb', 'NewImage', 'event_id', 'S') AS event_id_value,
    json_extract_path_text(json_serialize(payload), 'dynamodb', 'NewImage', 'session_id', 'S') AS session_id,
    json_extract_path_text(json_serialize(payload), 'dynamodb', 'NewImage', 'product_id', 'S') AS product_id,
    json_extract_path_text(json_serialize(payload), 'dynamodb', 'NewImage', 'product_category', 'S') AS product_category,
    json_extract_path_text(json_serialize(payload), 'dynamodb', 'NewImage', 'event_type', 'S') AS event_type,
    json_extract_path_text(json_serialize(payload), 'dynamodb', 'NewImage', 'browser', 'S') AS browser,
    json_extract_path_text(json_serialize(payload), 'dynamodb', 'NewImage', 'device_os', 'S') AS device_os,
    json_extract_path_text(json_serialize(payload), 'dynamodb', 'NewImage', 'device_type', 'S') AS device_type,
    json_extract_path_text(json_serialize(payload), 'dynamodb', 'NewImage', 'city', 'S') AS city,
    json_extract_path_text(json_serialize(payload), 'dynamodb', 'NewImage', 'country', 'S') AS country,
    json_extract_path_text(json_serialize(payload), 'dynamodb', 'NewImage', 'currency', 'S') AS currency,
    json_extract_path_text(json_serialize(payload), 'dynamodb', 'NewImage', 'campaign', 'S') AS campaign,
    json_extract_path_text(json_serialize(payload), 'dynamodb', 'NewImage', 'payment_method', 'NULL') AS payment_method_null,

    json_extract_path_text(json_serialize(payload), 'dynamodb', 'NewImage', 'quantity', 'N')::INT AS quantity,
    json_extract_path_text(json_serialize(payload), 'dynamodb', 'NewImage', 'unit_price', 'N')::FLOAT AS unit_price

FROM telemetry_mv;