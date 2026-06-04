from numpy import random
from datetime import timedelta
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

np.random.seed(42)
num_users = 1000

user_ids = [f"user_{i:04d}" for i in range(1, num_users +1)]
signup_dates = [datetime(2025,1,1) + timedelta(days=int(np.random.randint(0,365))) for _ in range(num_users)]
plans = np.random.choice(['Basic','Pro','Enterprise'], size=num_users, p=[0.5,0.35,0.15])
countries = np.random.choice(['United States', 'United Kingdom', 'Canada', 'Germany', 'India'], size=num_users)

users_df = pd.DataFrame({
    'UserID': user_ids,
    'SignupDate': signup_dates,
    'SubscriptionPlan': plans,
    'Country': countries

})

usage_records =[]
financial_records =[]

for idx, row in users_df.iterrows():
    uid = row['UserID']
    signup = row['SignupDate']
    plan = row['SubscriptionPlan']

    base_mrr = 29 if plan == 'Basic' else (79 if plan == 'Pro' else 299)
    is_churned = np.random.choice([True, False], p=[0.25,0.75])
    months_active = np.random.randint(1,13) if is_churned else 12

    for m in range(months_active):
        trans_date = signup + timedelta(days = m*30)
        if trans_date < datetime (2026,1,1):
            
            amt = np.nan if np.random.rand() < 0.02 else base_mrr
            financial_records.append({
                'TransactionID': f"TX_{uid}_{m}",
                'UserID': uid,
                'AmountPaid': amt,
                'TransactionDate': trans_date.strftime('%Y-%m-%d'),
                'status': 'Churned' if(is_churned and m == months_active -1) else 'Active'
                
            })
    
    total_logs = np.random.randint(5,50) if is_churned else np.random.randint(40,150)

    for l in range(total_logs):
        log_date = signup + timedelta(days = np.random.randint(0,months_active *30))
        if log_date < datetime(2026,1,1):
            usage_records.append({
                'LogID':f"LOG_{uid}_{l}",
                'UserID': uid,
                'FeatureAccessed': np.random.choice(['Dashboard','Export Reports','API Integrations','User Management']),
                'MinuteSpent': np.random.randint(1,60),
                'LogDate': log_date
            })



financials_df = pd.DataFrame(financial_records)
usage_df = pd.DataFrame(usage_records)

users_df.to_csv('users_raw.csv', index= False)
financials_df.to_csv('financials_raw.csv', index= False)
usage_df.to_csv('usage_raw.csv', index= False)

print("Data generation successful! 'users_raw.csv', 'financials_raw.csv', and 'usage_raw.csv' created.")