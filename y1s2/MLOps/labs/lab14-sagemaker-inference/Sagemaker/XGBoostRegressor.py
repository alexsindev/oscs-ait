import sagemaker
from sagemaker import image_uris
from sagemaker.inputs import TrainingInput

container = image_uris.retrieve('xgboost', region, '1.5-1')
print(f"XGBoost container: {container}")

train_s3_uri = f's3://{source_bucket}/{prefix}/train/train.csv'
val_s3_uri   = f's3://{source_bucket}/{prefix}/validation/val.csv'
test_s3_uri  = f's3://{source_bucket}/{prefix}/test/test.csv'

xgb = sagemaker.estimator.Estimator(
    image_uri=container,
    role=role,
    instance_count=1,
    instance_type='ml.m5.xlarge',
    output_path=f's3://{source_bucket}/{prefix}/model',
    sagemaker_session=session
)

xgb.set_hyperparameters(
    objective='reg:squarederror',
    eval_metric='rmse',
    max_depth=6,
    eta=0.1,
    num_round=300,
    subsample=0.8,
    colsample_bytree=0.8,
    early_stopping_rounds=20
)

xgb.fit({
    'train':      TrainingInput(train_s3_uri, content_type='text/csv'),
    'validation': TrainingInput(val_s3_uri,   content_type='text/csv')
})