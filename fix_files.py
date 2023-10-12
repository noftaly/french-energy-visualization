import pandas as pd

df_full = pd.read_csv('eco2mix-regional-full.csv', sep=';')
df_recent = pd.read_csv('eco2mix-regional-tr.csv', sep=';')

print('Loaded')

cols = ['nature', 'heure', 'column_68', 'pompage', 'stockage_batterie', 'destockage_batterie', 'eolien_terrestre', 'eolien_offshore', 'tco_thermique', 'tch_thermique', 'tco_nucleaire', 'tch_nucleaire', 'tco_eolien', 'tch_eolien', 'tco_solaire', 'tch_solaire', 'tco_hydraulique', 'tch_hydraulique', 'tco_bioenergies', 'tch_bioenergies', 'column_30']
df_full = df_full.drop(cols, axis=1, errors='ignore')
df_recent = df_recent.drop(cols, axis=1, errors='ignore')

print('Dropped columns')

df_full.to_csv('eco2mix-regional-full.csv', index=False)
print('Saved full')

df_recent.to_csv('eco2mix-regional-tr.csv', index=False)
print('Saved recent')

merged = pd.concat([df_full, df_recent])
print('Merged')

merged.to_csv('eco2mix-regional.csv', index=False)
print('Saved merged')

print('\n\nDone!')
