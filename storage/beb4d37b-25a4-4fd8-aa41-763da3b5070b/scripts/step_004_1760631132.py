import pandas as pd
import matplotlib.pyplot as plt

# Load the dataset
file_path = "storage/beb4d37b-25a4-4fd8-aa41-763da3b5070b/datasets/sample_sales_data.csv"
df = pd.read_csv(file_path)

# Convert 'Date' column to datetime objects (CoTAS Step 1)
df['Date'] = pd.to_datetime(df['Date'])

# Extract year and month and aggregate sales data (CoTAS Step 2)
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month

monthly_sales = df.groupby(['Year', 'Month']).agg(
    Total_Revenue=('Revenue', 'sum'),
    Total_Units_Sold=('Units_Sold', 'sum')
).reset_index()

# Create a combined 'YearMonth' for plotting
monthly_sales['YearMonth'] = monthly_sales['Year'].astype(str) + '-' + monthly_sales['Month'].astype(str).str.zfill(2)
monthly_sales = monthly_sales.sort_values(by=['Year', 'Month'])

# Visualize monthly trends (CoTAS Step 3 - re-attempting after matplotlib issue)
plt.figure(figsize=(12, 6))
plt.plot(monthly_sales['YearMonth'], monthly_sales['Total_Revenue'], marker='o', label='Total Revenue')
plt.title('Monthly Total Revenue Trend')
plt.xlabel('Month')
plt.ylabel('Total Revenue')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.show()

plt.figure(figsize=(12, 6))
plt.plot(monthly_sales['YearMonth'], monthly_sales['Total_Units_Sold'], marker='o', color='orange', label='Total Units Sold')
plt.title('Monthly Total Units Sold Trend')
plt.xlabel('Month')
plt.ylabel('Total Units Sold')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.show()