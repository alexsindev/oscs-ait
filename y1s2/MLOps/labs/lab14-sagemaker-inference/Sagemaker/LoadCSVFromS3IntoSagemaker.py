import boto3
import pandas as pd

s3 = boto3.client('s3')
source_bucket = 'st126112-s3-04042026'
source_key = 'global_power_plants.csv'

obj = s3.get_object(Bucket=source_bucket, Key=source_key)
df = pd.read_csv(obj['Body'])

print(f"Dataset: {df.shape[0]} rows x {df.shape[1]} columns")
df.head(3)