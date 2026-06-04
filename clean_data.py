import pandas as pd
import numpy as np

print("--- Starting Corporate Data Cleaning Pipeline ---")

# 1. Load the raw files
users = pd.read_csv('users_raw.csv')
financials = pd.read_csv('financials_raw.csv')
usage = pd.read_csv('usage_raw.csv')

# [Added Safety] Strip any hidden white spaces from all column names
users.columns = [col.strip() for col in users.columns]
financials.columns = [col.strip() for col in financials.columns]
usage.columns = [col.strip() for col in usage.columns]

# 2. Audit and fix the Financials data (Handling Missing Revenue)
# [Added Safety] Handle case-sensitivity issues for the 'status' or 'Status' column
if 'status' in financials.columns:
    financials = financials.rename(columns={'status': 'Status'})

print(f"Initial missing values in Financials:\n{financials.isnull().sum()}\n")

# Business Rule: If AmountPaid is missing, check the subscription plan to fill it
financials = financials.merge(users[['UserID', 'SubscriptionPlan']], on='UserID', how='left')

# Map plans to their respective monthly costs
plan_costs = {'Basic': 29.0, 'Pro': 79.0, 'Enterprise': 299.0}
financials['AmountPaid'] = financials['AmountPaid'].fillna(financials['SubscriptionPlan'].map(plan_costs))

# Drop the extra column we used for the calculation
financials = financials.drop(columns=['SubscriptionPlan'])

# 3. Handle structural consistency in dates
users['SignupDate'] = pd.to_datetime(users['SignupDate'])
financials['TransactionDate'] = pd.to_datetime(financials['TransactionDate'])
usage['LogDate'] = pd.to_datetime(usage['LogDate'])

# 4. Aggregating Usage Logs for Feature Analysis
print("Aggregating usage logs per individual user profile...")

# Force map columns by their physical position to bypass naming bugs completely
# Positions: 0=LogID, 1=UserID, 2=FeatureAccessed, 3=MinutesSpent, 4=LogDate
usage = usage.rename(columns={
    usage.columns[0]: 'LogID',
    usage.columns[1]: 'UserID',
    usage.columns[3]: 'MinutesSpent'
})

user_usage_summary = usage.groupby('UserID').agg(
    TotalMinutesSpent=('MinutesSpent', 'sum'),
    TotalInteractions=('LogID', 'count')
).reset_index()

# 5. Export clean datasets for the next analysis/dashboard phase
users.to_csv('users_clean.csv', index=False)
financials.to_csv('financials_clean.csv', index=False)
user_usage_summary.to_csv('usage_summary_clean.csv', index=False)

print("--- Data Cleaning Pipeline Complete! ---")
print("Saved cleaned files: 'users_clean.csv', 'financials_clean.csv', and 'usage_summary_clean.csv'.")