import pandas as pd
import matplotlib.pyplot as plt

# Load the dataset
df = pd.read_csv('storage/beb4d37b-25a4-4fd8-aa41-763da3b5070b/datasets/sample_sales_data.csv')

# Convert 'Date' column to datetime objects
df['Date'] = pd.to_datetime(df['Date'])

# Extract Year and Month for aggregation
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month

# Aggregate sales data to a monthly level
monthly_sales = df.groupby(['Year', 'Month']).agg(
    Total_Revenue=('Revenue', 'sum'),
    Total_Units_Sold=('Units_Sold', 'sum')
).reset_index()

# Create a 'Month_Year' column for plotting if needed, or sort by Year and Month
monthly_sales['Month_Year'] = monthly_sales['Year'].astype(str) + '-' + monthly_sales['Month'].astype(str).str.zfill(2)
monthly_sales = monthly_sales.sort_values(by=['Year', 'Month'])

# Plotting Monthly Total Revenue
plt.figure(figsize=(12, 6))
plt.plot(monthly_sales['Month_Year'], monthly_sales['Total_Revenue'], marker='o', linestyle='-')
plt.title('Monthly Total Revenue Over Time')
plt.xlabel('Month-Year')
plt.ylabel('Total Revenue')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.show()

# Plotting Monthly Total Units Sold
plt.figure(figsize=(12, 6))
plt.plot(monthly_sales['Month_Year'], monthly_sales['Total_Units_Sold'], marker='o', linestyle='-', color='orange')
plt.title('Monthly Total Units Sold Over Time')
plt.xlabel('Month-Year')
plt.ylabel('Total Units Sold')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.show()