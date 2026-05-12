# Machine Learning Operations (MLOps)

## Course Overview

Covers the engineering practices required to build, deploy, and operate ML
systems at scale. Labs are cloud-first (AWS), working with managed services
for data ingestion, batch processing, and model serving.

## Topics

- Data pipelines: batch vs streaming, event-driven architectures
- AWS streaming: Kinesis Data Streams, Kinesis Data Firehose
- Data warehousing: Amazon Redshift, external schemas, materialised views
- Distributed compute: Amazon EMR, Apache Spark (PySpark)
- Model training & serving: Amazon SageMaker
  - Training jobs, model artifacts, endpoints
  - XGBoost on SageMaker
  - Lambda + API Gateway inference
- Feature engineering: imputation, encoding, feature selection
- ML pipeline security considerations

## Contents

```
MLOps/
├── notes/
│   └── mlops-fundamentals.md
└── labs/
    ├── lab11-kinesis-redshift/   Streaming data → Kinesis → Redshift
    ├── lab12-emr-analytics/      EMR (PySpark) → Redshift analytics
    └── lab14-sagemaker-inference/ SageMaker XGBoost → Lambda → API Gateway
```

## Labs

### Lab 11 — Real-Time Streaming with Kinesis + Redshift

Producer Lambda generates e-commerce events → Kinesis Data Stream →
Kinesis Data Firehose → S3 → Redshift External Schema → Materialised Views.

Key files:
- `Lambda/producer.py` — event producer
- `Redshift/` — DDL + query scripts
- `EC2/bootstrap.sh` — Kinesis consumer on EC2

### Lab 12 — Fleet Analytics with EMR + Redshift

PySpark jobs on EMR process a fleet registry dataset, then write results
to Redshift for reporting.

Key files:
- `EMR/fleet_reliability_analysis.py` — PySpark analytics job
- `EMR/load_fleet_registry.ipynb` — notebook for loading data
- `Redshift/` — table creation + reporting SQL

### Lab 14 — SageMaker XGBoost Endpoint + Lambda Inference

Full ML pipeline:
1. Load CSV from S3 into SageMaker
2. Feature engineering (imputation, encoding, selection)
3. Train XGBoost model
4. Deploy to SageMaker endpoint
5. Lambda function calls endpoint for inference
6. API Gateway exposes inference as REST endpoint

Key files in `Sagemaker/`:
- `DataImputation.py`, `EncodeCategoricalData.py`, `FeatureEngineering.py`
- `CreateXGBoostModelEndpoint.py`, `CreateEndpointForLambda.py`
- `PerformInferenceFromSagemakerEndpoint.py`
