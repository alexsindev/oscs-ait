from sklearn.metrics import root_mean_squared_error, mean_absolute_error, r2_score

rmse = root_mean_squared_error(test_labels, predictions)
mae  = mean_absolute_error(test_labels, predictions)
r2   = r2_score(test_labels, predictions)

baseline_pred = test_df['capacity_mw'].values * 0.40 * 8.76
baseline_rmse = root_mean_squared_error(test_labels, baseline_pred)

print(f"===== TEST SET RESULTS =====")
print(f"XGBoost RMSE:    {rmse:.2f} GWh")
print(f"XGBoost MAE:     {mae:.2f} GWh")
print(f"XGBoost R²:      {r2:.4f}")
print(f"")
print(f"Baseline RMSE:   {baseline_rmse:.2f} GWh")
print(f"Improvement:     {((baseline_rmse - rmse) / baseline_rmse * 100):.1f}%")

# DELETE ENDPOINT IMMEDIATELY
predictor.delete_endpoint()
print(f"\nEndpoint DELETED: {predictor.endpoint_name}")