UNLOAD ('SELECT * FROM unnested_telemetry_vw')
TO 's3://st126112-s3-15032026/telemetry_output/'
IAM_ROLE 'arn:aws:iam::321502925342:role/LabRole'
FORMAT AS CSV
HEADER
PARALLEL OFF;