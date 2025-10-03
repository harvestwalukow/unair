import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors

df = pd.read_csv("fraudTest.csv")

def preprocess_data(df):
    target_col = "is_fraud"  # Target column untuk SMOTE
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if target_col not in numeric_cols:
        numeric_cols.append(target_col)
    
    df = df[numeric_cols]
    return df

def smote_synthetic_samples(X_minority, n_samples_needed, k=5):
    """Generates synthetic samples using SMOTE algorithm."""
    neigh = NearestNeighbors(n_neighbors=k)
    neigh.fit(X_minority)
    
    synthetic_samples = []
    
    for _ in range(n_samples_needed):
        i = np.random.randint(0, len(X_minority))  
        neighbors = neigh.kneighbors([X_minority[i]], return_distance=False)[0]
        neighbor = X_minority[np.random.choice(neighbors[1:])]  
        
        gap = np.random.rand()
        synthetic_sample = X_minority[i] + gap * (neighbor - X_minority[i])
        synthetic_samples.append(synthetic_sample)
    
    return np.array(synthetic_samples)

def balance_is_fraud_with_smote(df, k=5):
    """Balances 'is_fraud' column using SMOTE."""
    target_col = "is_fraud"
    
    df_majority = df[df[target_col] == 0]
    df_minority = df[df[target_col] == 1]
    
    n_samples_needed = len(df_majority) - len(df_minority)
    X_minority = df_minority.drop(columns=[target_col]).values
    
    synthetic_samples = smote_synthetic_samples(X_minority, n_samples_needed, k)
    
    synthetic_df = pd.DataFrame(synthetic_samples, columns=df_majority.columns[:-1])
    synthetic_df[target_col] = 1 
    
    balanced_df = pd.concat([df_majority, df_minority, synthetic_df], ignore_index=True)
    return balanced_df

df = preprocess_data(df)
balanced_df = balance_is_fraud_with_smote(df)

balanced_df.to_csv("balanced_training_data.csv", index=False)
print("Balanced data saved as 'balanced_training_data.csv'")
