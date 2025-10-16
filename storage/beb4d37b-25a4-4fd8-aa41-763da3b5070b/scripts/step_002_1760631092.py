import pandas as pd

# Load the dataset (assuming the DataFrame is not already loaded in the current environment)
df = pd.read_csv('storage/beb4d37b-25a4-4fd8-aa41-763da3b5070b/datasets/sample_sales_data.csv')

# Convert 'Date' column to datetime objects (re-applying as previous execution state is not guaranteed)
df['Date'] = pd.to_datetime(df['Date'])

# Extract Year and Month for time-series analysis
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month

# Aggregate data by Month to analyze monthly trends in Revenue and Units_Sold
monthly_trends = df.groupby(['Year', 'Month']).agg(
    Total_Revenue=('Revenue', 'sum'),
    Total_Units_Sold=('Units_Sold', 'sum')
).reset_index()

# Display the monthly trends
print(monthly_trends.head())
print(monthly_trends.info())