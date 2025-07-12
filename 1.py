import pandas as pd

# Try reading with cp1252 or latin1 encoding if you had UnicodeDecodeError
df = pd.read_csv(r"C:\Users\vaish\Documents\STUDY\INTEL INTERNSHIP\Datasets\Students.csv", encoding='cp1252')

# Clean headers and data
df.columns = [col.strip().upper() for col in df.columns]
for col in df.columns:
    if df[col].dtype == object:
        df[col] = df[col].astype(str).str.strip().str.replace('\xa0', ' ')
if 'MAIL ID' in df.columns:
    df['MAIL ID'] = df['MAIL ID'].str.lower()
df = df.fillna('')

# Save as clean UTF-8 CSV
df.to_csv(r"C:\Users\vaish\Documents\STUDY\INTEL INTERNSHIP\Datasets\Students1.csv", index=False, encoding='utf-8')

