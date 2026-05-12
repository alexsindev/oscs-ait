import numpy as np

drop_cols = [
    'plant_id', 'plant_name', 'plant_id_wri', 'wepp_id',
    'source', 'generation_data_source',
    'secondary_fuel', 'tertiary_fuel',
    'country_code', 'country_long',
    'generation_gwh_2019', 'generation_gwh_2020',
    'generation_gwh_2021', 'generation_gwh_2022', 'generation_gwh_2023',
    'capacity_factor_est'
]
df_clean = df.drop(columns=drop_cols)
df_clean = df_clean.dropna(subset=['estimated_generation_gwh'])

print(f"Remaining: {df_clean.shape[0]} rows x {df_clean.shape[1]} columns")
print(f"Columns kept: {list(df_clean.columns)}")