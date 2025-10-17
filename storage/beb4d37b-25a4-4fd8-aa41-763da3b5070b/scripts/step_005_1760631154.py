import pandas as pd
import matplotlib.pyplot as plt

# Load the dataset
df = pd.read_csv('storage/beb4d37b-25a4-4fd8-aa41-763da3b5070b/datasets/sample_sales_data.csv')

# Convert 'Date' column to datetime objects (CoTAS Step 1)
df['Date'] = pd.to_datetime(df['Date'])

# Extract year and month, then aggregate sales data to a monthly level (CoTAS Step 2)
df['YearMonth'] = df['Date'].dt.to_period('M')
monthly_sales = df.groupby('YearMonth').agg(
    Total_Revenue=('Revenue', 'sum'),
    Total_Units_Sold=('Units_Sold', 'sum')
).reset_index()

# Convert 'YearMonth' back to datetime for plotting compatibility
monthly_sales['YearMonth'] = monthly_sales['YearMonth'].dt.to_timestamp()

# Visualize monthly trends for Total Revenue and Total Units Sold (CoTAS Step 3/4)
fig, axes = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

# Plot Total Revenue
axes[0].plot(monthly_sales['YearMonth'], monthly_sales['Total_Revenue'], marker='o', linestyle='-')
axes[0].set_title('Monthly Total Revenue Over Time')
axes[0].set_ylabel('Total Revenue')
axes[0].grid(True)

# Plot Total Units Sold
axes[1].plot(monthly_sales['YearMonth'], monthly_sales['Total_Units_Sold'], marker='o', linestyle='-', color='orange')
axes[1].set_title('Monthly Total Units Sold Over Time')
axes[1].set_xlabel('Month')
axes[1].set_ylabel('Total Units Sold')
axes[1].grid(True)

plt.tight_layout()
plt.show()