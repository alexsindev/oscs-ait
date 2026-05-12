from sklearn.preprocessing import OneHotEncoder
import joblib, os

cat_cols   = ['primary_fuel', 'ownership_type', 'status', 'region']
num_cols   = ['capacity_mw', 'latitude', 'longitude', 'plant_age', 'is_renewable']
target_col = 'estimated_generation_gwh'

encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
encoder.fit(train_df[cat_cols])

def build_matrix(dataframe, enc, cat_cols, num_cols, target_col):
    target  = dataframe[target_col].values.reshape(-1, 1)
    numeric = dataframe[num_cols].values
    encoded = enc.transform(dataframe[cat_cols])
    return np.concatenate([target, numeric, encoded], axis=1)

train_matrix = build_matrix(train_df, encoder, cat_cols, num_cols, target_col)
val_matrix   = build_matrix(val_df,   encoder, cat_cols, num_cols, target_col)
test_matrix  = build_matrix(test_df,  encoder, cat_cols, num_cols, target_col)

print(f"Train: {train_matrix.shape}  |  Val: {val_matrix.shape}  |  Test: {test_matrix.shape}")
print(f"Features per row: {train_matrix.shape[1] - 1}")

os.makedirs('artifacts', exist_ok=True)
joblib.dump(impute_vals, 'artifacts/impute_vals.joblib')
joblib.dump(encoder,     'artifacts/encoder.joblib')
print("Saved: artifacts/impute_vals.joblib, artifacts/encoder.joblib")