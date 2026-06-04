import pandas as pd 
print("--- Running SaaS Revenue & Churn Analysis --- \n")

financials = pd.read_csv('financials_clean.csv')
usage_summary = pd.read_csv('usage_summary_clean.csv')
users = pd.read_csv('users_clean.csv')


total_customers = financials['UserID'].nunique()
churned_customers = financials[financials['Status']== 'Churned']['UserID'].nunique()
churn_rate = (churned_customers / total_customers) * 100

print(f"🔹 Total Unique Customers Evaluated: {total_customers}")
print(f"🔹 Total Customers Lost (Churned): {churned_customers}")
print(f"🔹 Overall Customer Churn Rate: {churn_rate:.2f}%\n")

total_revenue_collected = financials['AmountPaid'].sum()
lost_revenue = financials[financials['Status']=='Churned']['AmountPaid'].sum()

print(f"💵 Total Revenue Collected: ${total_revenue_collected:,.2f}")
print(f"🚨 Revenue Lost to Churn: ${lost_revenue:,.2f}\n")

user_status = financials.drop_duplicates(subset=['UserID'], keep ='last')[['UserID','Status']]
users_with_status = users.merge(user_status, on ='UserID', how='left')

print("--- Churn Analysis by Subscription Plan ---")

plan_breakdown = users_with_status.groupby('SubscriptionPlan').agg(
    TotalUsers = ('UserID', 'count'),
    ChurnedUsers = ('Status', lambda x: (x=='Churned').sum())
).reset_index()

plan_breakdown['PlanChurnRate(%)'] = (plan_breakdown['ChurnedUsers'] / plan_breakdown['TotalUsers'])* 100
print(plan_breakdown.to_string(index=False))
print("\n")
usage_with_staus = usage_summary.merge(user_status, on='UserID', how= 'left')
engagement_breakdown = usage_with_staus.groupby('Status').agg(
    AvgMinutesSpent=('TotalMinutesSpent', 'mean'),
    AvgInteractions=('TotalInteractions', 'mean')
).reset_index()



print("--- Product Engagement Breakdown ---")
print(engagement_breakdown.to_string(index=False))