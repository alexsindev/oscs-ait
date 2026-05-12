# MLOps Fundamentals

## What is MLOps?

MLOps (Machine Learning Operations) applies DevOps principles to the ML lifecycle:
building, testing, deploying, monitoring, and retraining ML systems reliably at scale.

**Key concerns:**
- Reproducibility of training runs
- Data versioning and lineage
- Model versioning and registry
- Serving infrastructure (latency, throughput, cost)
- Monitoring: data drift, model degradation, infrastructure health
- Feedback loops for continuous improvement

---

## Data Pipelines

### Batch vs Streaming

| | Batch | Streaming |
|---|---|---|
| Latency | Hours to days | Milliseconds to seconds |
| Throughput | Very high | High |
| Complexity | Lower | Higher |
| Use cases | Daily reports, model training | Fraud detection, recommendations, IoT |

### Lambda Architecture

Combines batch and streaming:
- **Batch layer:** Processes historical data periodically; slow but accurate
- **Speed layer:** Processes recent data in real-time; fast but approximate
- **Serving layer:** Merges both to answer queries

### Kappa Architecture

Simpler alternative: everything is a stream. Historical reprocessing done by
replaying the same stream through the same pipeline.

---

## AWS Streaming: Kinesis

### Kinesis Data Streams

- Ordered, partitioned stream of records
- **Shards:** Each shard handles 1 MB/s write, 2 MB/s read
- **Retention:** 24 hours (default) up to 7 days
- Records keyed by **partition key** → consistent hash → shard assignment

```python
import boto3
kinesis = boto3.client('kinesis', region_name='us-east-1')

kinesis.put_record(
    StreamName='my-stream',
    Data=json.dumps({'event': 'purchase', 'amount': 99.99}),
    PartitionKey='user_123'
)
```

### Kinesis Data Firehose

Managed delivery service: Kinesis Streams → S3 / Redshift / OpenSearch.
- No consumer code needed
- Buffering: by size (1–128 MB) or time (60–900 s)
- Optional Lambda transform before delivery
- Automatic retry + dead-letter to S3

---

## Amazon Redshift

Columnar data warehouse optimised for analytical queries (OLAP).

### External Schema (Spectrum)

Query data in S3 directly without loading:

```sql
CREATE EXTERNAL SCHEMA kinesis_schema
FROM KINESIS
IAM_ROLE 'arn:aws:iam::123456789:role/MyRedshiftRole';
```

### Materialised Views

Pre-computed result sets refreshed on demand:

```sql
CREATE MATERIALIZED VIEW top_products AS
SELECT product_id, SUM(quantity) AS total_sold
FROM sales_events
GROUP BY product_id;

REFRESH MATERIALIZED VIEW top_products;
```

### Key SQL Patterns

```sql
-- Unnest JSON array from Kinesis
SELECT json_extract_array_element_text(payload, 0) AS first_item
FROM kinesis_schema.events;

-- Unload query results to S3
UNLOAD ('SELECT * FROM top_products')
TO 's3://my-bucket/reports/'
IAM_ROLE 'arn:...'
FORMAT AS PARQUET;
```

---

## Amazon EMR (Elastic MapReduce)

Managed Hadoop/Spark cluster.

### PySpark Job Structure

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, count

spark = SparkSession.builder.appName("FleetAnalysis").getOrCreate()

# Load data from S3
df = spark.read.parquet("s3://my-bucket/fleet-data/")

# Transformations
result = (df
    .filter(col("status") == "active")
    .groupBy("vehicle_type")
    .agg(
        count("*").alias("count"),
        avg("mileage").alias("avg_mileage")
    )
    .orderBy("count", ascending=False))

# Write back to S3 / Redshift
result.write.mode("overwrite").parquet("s3://my-bucket/output/")

spark.stop()
```

### Submitting a Job

```bash
aws emr add-steps \
  --cluster-id j-XXXXX \
  --steps Type=spark,Name="Fleet Analysis",\
    Args=[--deploy-mode,cluster,s3://my-bucket/fleet_analysis.py]
```

---

## Amazon SageMaker

Managed ML platform for the full ML lifecycle.

### Pipeline Overview

```
S3 (raw data)
  → SageMaker Processing Job (feature engineering)
  → SageMaker Training Job (model training)
  → Model Registry
  → SageMaker Endpoint (real-time inference)
  → Lambda + API Gateway (REST API wrapper)
```

### Training with Built-in XGBoost

```python
from sagemaker.estimator import Estimator

estimator = Estimator(
    image_uri=sagemaker.image_uris.retrieve('xgboost', region, '1.5-1'),
    role=role,
    instance_count=1,
    instance_type='ml.m5.xlarge',
    output_path=f's3://{bucket}/models/'
)

estimator.set_hyperparameters(
    objective='binary:logistic',
    num_round=100,
    max_depth=5,
    eta=0.1
)

estimator.fit({'train': train_input, 'validation': val_input})
```

### Deploying an Endpoint

```python
predictor = estimator.deploy(
    initial_instance_count=1,
    instance_type='ml.t2.medium',
    serializer=sagemaker.serializers.CSVSerializer()
)

result = predictor.predict(test_data)

# Clean up (avoid unnecessary costs)
predictor.delete_endpoint()
```

### Lambda Inference Function

```python
import boto3
import json

runtime = boto3.client('sagemaker-runtime')

def lambda_handler(event, context):
    body = json.loads(event['body'])
    payload = ','.join(str(v) for v in body['features'])

    response = runtime.invoke_endpoint(
        EndpointName='my-xgboost-endpoint',
        ContentType='text/csv',
        Body=payload
    )

    result = json.loads(response['Body'].read())
    return {
        'statusCode': 200,
        'body': json.dumps({'prediction': result})
    }
```

---

## Feature Engineering

### Imputation

```python
from sklearn.impute import SimpleImputer
import pandas as pd

df['age'].fillna(df['age'].median(), inplace=True)
# Or
imputer = SimpleImputer(strategy='median')
df[['age', 'fare']] = imputer.fit_transform(df[['age', 'fare']])
```

### Encoding Categorical Variables

```python
# One-hot encoding
df = pd.get_dummies(df, columns=['sex', 'embarked'])

# Label encoding (ordinal)
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
df['class_encoded'] = le.fit_transform(df['pclass'])
```

### Feature Scaling

```python
from sklearn.preprocessing import StandardScaler, MinMaxScaler

# Standardise (mean=0, std=1) — important for models using distances
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Min-max scale to [0,1]
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)
```

---

## ML Pipeline Security

**Key risk areas:**
- Data poisoning: adversarial manipulation of training data
- Model inversion / extraction attacks
- Insecure endpoints: open inference APIs
- Credential exposure in notebooks / code

**Mitigations:**
- Encrypt data at rest (S3 SSE-S3, SSE-KMS) and in transit (TLS)
- IAM least-privilege roles for each pipeline stage
- VPC endpoints — keep traffic off public internet
- Input validation before inference (schema checks, anomaly detection)
- Audit logging (CloudTrail for API calls, S3 access logs)
- Rotate secrets; use AWS Secrets Manager rather than environment variables
