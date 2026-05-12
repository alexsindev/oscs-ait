CREATE MATERIALIZED VIEW telemetry_mv AS
    SELECT approximate_arrival_timestamp,
    partition_key,
    shard_id,
    sequence_number,
    json_parse(kinesis_data) AS payload
    FROM kinesis_schema."st126112-kinesis-15032026";