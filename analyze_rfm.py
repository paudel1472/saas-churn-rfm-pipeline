import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

print("🎯 Step 3 Initialized: Compiling SaaS Behavioral RFM Matrix...")

# 1. Direct Ingestion of production-ready tables
df_users = pd.read_csv('users_clean.csv')
df_usage_summary = pd.read_csv('usage_summary_clean.csv')
df_financials = pd.read_csv('financials_clean.csv')
df_usage_raw = pd.read_csv('usage_raw.csv')

# Ensure dates are parsed correctly
df_usage_raw['LogDate'] = pd.to_datetime(df_usage_raw['LogDate'])
df_financials['TransactionDate'] = pd.to_datetime(df_financials['TransactionDate'])

# 2. Establish snapshot evaluation date (1 day after the absolute last log)
snapshot_date = df_usage_raw['LogDate'].max() + pd.Timedelta(days=1)

# 3. Aggregation Layer (Engineers Recency, Frequency, and Monetary Values)
recency_df = df_usage_raw.groupby('UserID').agg(
    LatestSession=('LogDate', 'max')
).reset_index()
recency_df['Recency'] = (snapshot_date - recency_df['LatestSession']).dt.days

financial_metrics = df_financials.groupby('UserID')['AmountPaid'].sum().reset_index()
financial_metrics.rename(columns={'AmountPaid': 'Monetary'}, inplace=True)

# 4. Structural Merge into a Unified RFM Lifecycle Table
user_status = df_financials.drop_duplicates(subset=['UserID'], keep='last')[['UserID', 'Status']]
rfm_table = df_users[['UserID', 'SubscriptionPlan']].merge(user_status, on='UserID', how='left')

rfm_table = rfm_table.merge(recency_df[['UserID', 'Recency']], on='UserID', how='left')
rfm_table = rfm_table.merge(df_usage_summary[['UserID', 'TotalInteractions']], on='UserID', how='left')
rfm_table = rfm_table.merge(financial_metrics, on='UserID', how='left')

rfm_table.rename(columns={'TotalInteractions': 'Frequency'}, inplace=True)

# Fill any missing metrics with logical baselines
rfm_table.fillna({
    'Recency': rfm_table['Recency'].max(), 
    'Frequency': 0, 
    'Monetary': 0
}, inplace=True)

# 5. Quantile Binning (Rank-based scoring from 1 to 4)
rfm_table['R_Score'] = pd.qcut(rfm_table['Recency'].rank(method='first'), q=4, labels=[4, 3, 2, 1]).astype(int)
rfm_table['F_Score'] = pd.qcut(rfm_table['Frequency'].rank(method='first'), q=4, labels=[1, 2, 3, 4]).astype(int)
rfm_table['M_Score'] = pd.qcut(rfm_table['Monetary'].rank(method='first'), q=4, labels=[1, 2, 3, 4]).astype(int)

# 6. Actionable SaaS Segment Mapping Logic
def map_saas_segment(row):
    r, f, m = row['R_Score'], row['F_Score'], row['M_Score']
    if r == 4 and f == 4 and m == 4:
        return 'SaaS Power Users (Champions)'
    elif r >= 3 and f >= 3:
        return 'Highly Engaged / Loyal'
    elif r >= 3 and f <= 2:
        return 'New Onboarded / Promising'
    elif r <= 2 and f >= 3:
        return 'High Churn Risk (Inactive Heavy Users)'
    else:
        return 'Deactivated / Hibernating'

rfm_table['User_Segment'] = rfm_table.apply(map_saas_segment, axis=1)

print("\n=== SaaS Behavioral RFM Master Ledger (Sample) ===")
print(rfm_table[['UserID', 'SubscriptionPlan', 'Recency', 'Frequency', 'Monetary', 'User_Segment']].head(10))

# 7. Validation Audit: Correlation between behavioral segments and real churn metrics
print("\n=== Risk Validation: Actual Churn Rate by Customer Segment ===")
segment_churn = rfm_table.groupby('User_Segment')['Status'].apply(lambda x: (x == 'Churned').mean()).round(4) * 100
print(segment_churn.apply(lambda x: f"{x:.2f}%"))

# 8. VISUALIZATION LAYER: Export to Dashboard Asset
plt.figure(figsize=(12, 6))
sns.barplot(
    x=segment_churn.values,
    y=segment_churn.index,
    palette='Reds_r'
)
plt.title('SaaS Attrition Risk Validation Matrix (Actual Churn % by RFM Segment)', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Realized Churn Rate (%)', fontsize=12)
plt.ylabel('Engineered Customer Segment', fontsize=12)
sns.despine()
plt.tight_layout()

plt.savefig('saas_rfm_risk_matrix.png', dpi=300)
print("\n🎯 Visual asset saved successfully as 'saas_rfm_risk_matrix.png'")
plt.show()