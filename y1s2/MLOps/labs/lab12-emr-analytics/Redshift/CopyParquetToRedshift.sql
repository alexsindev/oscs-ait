COPY maintenance_event_summary
FROM 's3://st126112-s3-26032026/output/'
IAM_ROLE 'arn:aws:iam::321502925342:role/LabRole'
FORMAT AS PARQUET;