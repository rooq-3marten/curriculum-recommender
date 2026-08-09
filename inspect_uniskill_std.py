from pathlib import Path
import csv

p = Path('c:/Users/user/Desktop/python pj/curriculum-recommender/data/uniskill.csv')
print('exists', p.exists())
with p.open('r', encoding='utf-16', newline='') as f:
    rows = list(csv.reader(f))
print('row_count', len(rows))
for i, row in enumerate(rows[:10]):
    print(i, row)
