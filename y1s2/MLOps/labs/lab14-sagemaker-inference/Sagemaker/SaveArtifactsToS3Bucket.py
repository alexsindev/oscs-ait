np.savetxt('train.csv', train_matrix, delimiter=',', fmt='%.6f')
np.savetxt('val.csv',   val_matrix,   delimiter=',', fmt='%.6f')
np.savetxt('test.csv',  test_matrix,  delimiter=',', fmt='%.6f')

prefix = 'output'

s3.upload_file('train.csv', source_bucket, f'{prefix}/train/train.csv')
s3.upload_file('val.csv',   source_bucket, f'{prefix}/validation/val.csv')
s3.upload_file('test.csv',  source_bucket, f'{prefix}/test/test.csv')

s3.upload_file('artifacts/impute_vals.joblib', source_bucket, f'{prefix}/artifacts/impute_vals.joblib')
s3.upload_file('artifacts/encoder.joblib',     source_bucket, f'{prefix}/artifacts/encoder.joblib')

print(f"Uploaded to s3://{source_bucket}/{prefix}/")
print(f"  train/train.csv        ({train_matrix.shape[0]} rows)")
print(f"  validation/val.csv     ({val_matrix.shape[0]} rows)")
print(f"  test/test.csv          ({test_matrix.shape[0]} rows)")
print(f"  artifacts/impute_vals.joblib")
print(f"  artifacts/encoder.joblib")