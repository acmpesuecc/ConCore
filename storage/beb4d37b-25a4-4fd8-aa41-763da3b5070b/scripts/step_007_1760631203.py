import pandas as pd
import matplotlib.pyplot as plt
import subprocess
import sys
import os

# Ensure matplotlib is installed
try:
    import matplotlib.pyplot as plt
except ImportError:
    print("matplotlib not found. Installing...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib"])
        print("matplotlib installed successfully.")
        import matplotlib.pyplot as plt # Try importing again after installation
    except Exception as e:
        print(f"Error installing matplotlib: {e}")
        # If matplotlib still can't be installed, the subsequent visualization steps will fail.
        # For this autonomous agent, it's best to proceed and let the user know if visualization fails.

# Define the file path
file_path = "storage/beb4d37b-25a4-4fd8-aa41-763da3b5070b/datasets/sample_sales_data.csv"

# Load the dataset
df = pd.read_csv(file_path)

# Convert 'Date' column to datetime objects
df['Date'] = pd.to_datetime(df['Date'])

# Extract Year and Month for aggregation
df['YearMonth'] = df['Date'].dt.to_period('M')

# Aggregate sales data to a monthly level
monthly_sales = df.groupby('YearMonth').agg(
    Total_Revenue=('Revenue', 'sum'),
    Total_Units_Sold=('Units_Sold', 'sum')
).reset_index()

# Convert YearMonth back to datetime for plotting compatibility if needed, or keep as Period for x-axis
monthly_sales['YearMonth_dt'] = monthly_sales['YearMonth'].dt.to_timestamp()

# Visualize monthly trends for Total Revenue and Total Units Sold
fig, axes = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

# Plot Total Revenue
axes[0].plot(monthly_sales['YearMonth_dt'], monthly_sales['Total_Revenue'], marker='o', linestyle='-')
axes[0].set_title('Monthly Total Revenue Trend')
axes[0].set_ylabel('Total Revenue')
axes[0].grid(True)

# Plot Total Units Sold
axes[1].plot(monthly_sales['YearMonth_dt'], monthly_sales['Total_Units_Sold'], marker='o', linestyle='-', color='orange')
axes[1].set_title('Monthly Total Units Sold Trend')
axes[1].set_xlabel('Date')
axes[1].set_ylabel('Total Units Sold')
axes[1].grid(True)

plt.tight_layout()
plt.show()

print("Monthly trends for Total Revenue and Total Units Sold visualized successfully.")