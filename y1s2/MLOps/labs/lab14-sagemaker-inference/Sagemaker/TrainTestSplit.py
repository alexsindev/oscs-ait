from sklearn.model_selection import train_test_split

train_df, temp_df = train_test_split(
    df_clean, test_size=0.2, random_state=42, stratify=df_clean['primary_fuel']
)
val_df, test_df = train_test_split(
    temp_df, test_size=0.5, random_state=42, stratify=temp_df['primary_fuel']
)

print(f"Train: {train_df.shape[0]} rows (80%)")
print(f"Val:   {val_df.shape[0]} rows (10%)")
print(f"Test:  {test_df.shape[0]} rows (10%)")