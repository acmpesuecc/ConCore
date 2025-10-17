import pandas as pd

# Load the dataset
df = pd.read_csv('storage/beb4d37b-25a4-4fd8-aa41-763da3b5070b/datasets/sample_sales_data.csv')

# Convert 'Date' column to datetime objects
df['Date'] = pd.to_datetime(df['Date'])

# Display the first few rows with the updated 'Date' column and its datatype
print(df.head())
print(df.info())