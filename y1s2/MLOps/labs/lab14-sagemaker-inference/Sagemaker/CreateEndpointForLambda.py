from sagemaker.serializers import CSVSerializer

predictor = xgb.deploy(
    initial_instance_count=1,
    instance_type='ml.m5.large',
    serializer=CSVSerializer(),
    endpoint_name='power-plant-endpoint'
)

print(f"Production endpoint live: {predictor.endpoint_name}")