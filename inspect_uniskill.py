from pathlib import Path
import pandas as pd

p = Path('c:/Users/user/Desktop/python pj/curriculum-recommender/data/uniskill.csv')
print('exists', p.exists())
df = pd.read_csv(p, encoding='utf-16')
print(df.head(10).to_string())
print('\nCOLUMNS:', list(df.columns))
print('\nSHAPE:', df.shape)
print('\nDTYPES:')
print(df.dtypes)
