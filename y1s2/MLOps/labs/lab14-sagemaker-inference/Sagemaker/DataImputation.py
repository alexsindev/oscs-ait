impute_vals = {
    'commissioning_year': train_df['commissioning_year'].median(),
    'ownership_type':     train_df['ownership_type'].mode()[0],
    'region':             train_df['region'].mode()[0]
}

train_df = train_df.fillna(impute_vals)
val_df   = val_df.fillna(impute_vals)
test_df  = test_df.fillna(impute_vals)

print(f"Fill values (from training set only):")
for k, v in impute_vals.items():
    print(f"  {k}: {v}")