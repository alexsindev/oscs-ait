from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sagemaker.serializers import CSVSerializer

predictor = xgb.deploy(
    initial_instance_count=1,
    instance_type='ml.m5.large',
    serializer=CSVSerializer()
)
print(f"Endpoint deployed: {predictor.endpoint_name}")