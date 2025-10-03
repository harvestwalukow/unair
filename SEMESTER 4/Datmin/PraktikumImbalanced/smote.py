import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from collections import Counter
from sklearn.preprocessing import LabelEncoder

def smote_implementation(X, y, minority_class=1, k_neighbors=5, n_samples=500):
    # ambil sampel kelas minoritas
    minority_indices = np.where(y == minority_class)[0]
    X_minority = X[minority_indices]
    
    # mencari k-nearest neighbors untuk setiap sampel minoritas
    nn = NearestNeighbors(n_neighbors=k_neighbors+1)  # +1 karena termasuk dirinya sendiri
    nn.fit(X_minority)
    distances, indices = nn.kneighbors(X_minority)
    
    # sampel sintetis
    synthetic_samples = []
    num_minority = len(X_minority)
    
    for i in range(n_samples):
        # pilih sampel minoritas secara acak
        random_idx = np.random.randint(0, num_minority)
        # pilih tetangga secara acak
        random_neighbor_idx = np.random.choice(indices[random_idx][1:])  # [1:] untuk menghindari dirinya sendiri
        
        # ambil sampel dan tetangganya
        sample = X_minority[random_idx]
        neighbor = X_minority[random_neighbor_idx]
        
        # buat sampel sintetis
        diff = neighbor - sample
        gap = np.random.random()
        synthetic_sample = sample + gap * diff
        
        synthetic_samples.append(synthetic_sample)
    
    # gabungkan data asli dengan sampel sintetis
    X_synthetic = np.array(synthetic_samples)
    y_synthetic = np.array([minority_class] * n_samples)
    
    X_new = np.vstack([X, X_synthetic])
    y_new = np.hstack([y, y_synthetic])
    
    return X_new, y_new

# penggunaan pada dataset fraud
def apply_smote_to_fraud_data():
    # baca dataset
    train_data = pd.read_csv('fraudTrain.csv')
    test_data = pd.read_csv('fraudTest.csv')
    
    # preprocessing
    columns_to_drop = ['trans_date_trans_time', 'cc_num', 'merchant', 'category', 'first', 'last', 'street', 'city', 'state', 'zip', 'job', 'dob', 'trans_num']
    train_data = train_data.drop(columns=columns_to_drop)
    test_data = test_data.drop(columns=columns_to_drop)
    
    # encode variabel kategorik
    le = LabelEncoder()
    train_data['gender'] = le.fit_transform(train_data['gender'])
    test_data['gender'] = le.transform(test_data['gender'])
    
    # konversi boolean ke numeric
    train_data['is_fraud'] = train_data['is_fraud'].astype(int)
    test_data['is_fraud'] = test_data['is_fraud'].astype(int)
    
    # pisahkan feature dan target
    X_train = train_data.drop('is_fraud', axis=1).values
    y_train = train_data['is_fraud'].values
    
    # hitung distribusi kelas sebelum SMOTE
    print("Distribusi kelas sebelum SMOTE:", Counter(y_train))
    
    # terapkan SMOTE
    # hitung jumlah sampel yang dibutuhkan untuk menyeimbangkan kelas
    n_minority = Counter(y_train)[1]
    n_majority = Counter(y_train)[0]
    n_synthetic = n_majority - n_minority
    
    X_resampled, y_resampled = smote_implementation(
        X_train, 
        y_train,
        minority_class=1,
        k_neighbors=5,
        n_samples=n_synthetic
    )
    
    # hitung distribusi kelas setelah SMOTE
    print("Distribusi kelas setelah SMOTE:", Counter(y_resampled))
    
    # simpan hasil SMOTE ke file CSV
    columns = train_data.drop('is_fraud', axis=1).columns
    balanced_df = pd.DataFrame(X_resampled, columns=columns)
    balanced_df['is_fraud'] = y_resampled
    
    balanced_df.to_csv('balanced_fraud_data.csv', index=False)
    print("Data setelah SMOTE telah disimpan ke 'balanced_fraud_data.csv'")
    
    return X_resampled, y_resampled

# jalankan SMOTE pada dataset
if __name__ == "__main__":
    X_balanced, y_balanced = apply_smote_to_fraud_data()

balanced_data = pd.read_csv('balanced_fraud_data.csv')
balanced_data.head()