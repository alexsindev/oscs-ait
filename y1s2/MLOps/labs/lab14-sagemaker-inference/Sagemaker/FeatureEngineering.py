RENEWABLES = {'Solar', 'Wind', 'Hydro', 'Geothermal', 'Tidal', 'Biomass'}

for split_df in [train_df, val_df, test_df]:
    split_df['plant_age']    = 2026 - split_df['commissioning_year']
    split_df['is_renewable'] = split_df['primary_fuel'].isin(RENEWABLES).astype(int)
    split_df.drop(columns=['commissioning_year'], inplace=True)

print(f"New columns added: plant_age, is_renewable")
print(f"Columns now: {list(train_df.columns)}")