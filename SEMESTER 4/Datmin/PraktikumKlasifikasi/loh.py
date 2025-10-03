import numpy as np
import pandas as pd
from collections import Counter

# Fungsi untuk menghitung entropi
def entropy(y):
    value, counts = np.unique(y, return_counts=True)
    prob = counts / counts.sum()
    prob = prob[prob > 0]  # Hindari log(0)
    return -np.sum(prob * np.log2(prob))

# Fungsi untuk menghitung gain informasi
def information_gain(X, y, feature_index):
    total_entropy = entropy(y)
    
    values, counts = np.unique(X[:, feature_index], return_counts=True)
    weighted_entropy = sum((counts[i] / len(y)) * entropy(y[X[:, feature_index] == values[i]]) for i in range(len(values)))
    
    return total_entropy - weighted_entropy

# Fungsi untuk membangun pohon keputusan
def build_tree(X, y, feature_indices, depth=0, max_depth=None):
    if len(np.unique(y)) == 1:
        return y[0]
    
    if len(feature_indices) == 0 or (max_depth is not None and depth >= max_depth):
        return Counter(y).most_common(1)[0][0]  # Kembalikan nilai mayoritas
    
    gains = [information_gain(X, y, i) for i in feature_indices]
    best_feature_index = feature_indices[np.argmax(gains)]
    
    tree = {best_feature_index: {}}
    values = np.unique(X[:, best_feature_index])
    
    for value in values:
        subset_indices = X[:, best_feature_index] == value
        if np.any(subset_indices):
            subtree = build_tree(X[subset_indices], y[subset_indices], 
                                 [i for i in feature_indices if i != best_feature_index],
                                 depth + 1, max_depth)
            tree[best_feature_index][value] = subtree
    
    return tree

# Fungsi untuk melakukan prediksi
def predict(tree, sample, default=1):  # Default ke nilai mayoritas
    if not isinstance(tree, dict):
        return tree

    feature_index = next(iter(tree))
    feature_value = sample[feature_index]

    if feature_value in tree[feature_index]:
        return predict(tree[feature_index][feature_value], sample, default)
    else:
        return default  # Jika nilai fitur tidak ditemukan, kembalikan nilai mayoritas

# Import dataset
data_latih = pd.read_csv('Data_Latih.csv', delimiter=',', header=0)
data_uji = pd.read_csv('Data_Uji.csv', delimiter=',', header=0)

# Encoding label kategorikal (Manis → 1, Asam → 0)
data_latih['Rasa'] = data_latih['Rasa'].map({'Manis': 1, 'Asam': 0})
data_uji['Rasa'] = data_uji['Rasa'].map({'Manis': 1, 'Asam': 0})

# Persiapkan input dan label untuk pelatihan
X_train = data_latih.iloc[:, 0:3].values  # Kolom R, G, B
y_train = data_latih.iloc[:, 3].values    # Kolom Rasa

# Bangun pohon keputusan dengan kedalaman lebih besar
feature_indices = list(range(X_train.shape[1]))
decision_tree = build_tree(X_train, y_train, feature_indices, max_depth=5)

# Persiapkan input untuk pengujian
X_test = data_uji.iloc[:, 0:3].values
y_test = data_uji.iloc[:, 3].values

# Cari label mayoritas untuk handling unknown values
default_label = Counter(y_train).most_common(1)[0][0]

# Prediksi menggunakan pohon keputusan
predictions = [predict(decision_tree, sample, default_label) for sample in X_test]

# Evaluasi model
correct_predictions = sum(pred == true for pred, true in zip(predictions, y_test))
total_predictions = len(y_test)
accuracy = correct_predictions / total_predictions * 100

print("Hasil Prediksi Decision Tree:", predictions)
print("Prediksi Benar:", correct_predictions, "data")
print("Prediksi Salah:", total_predictions - correct_predictions, "data")
print("Akurasi Decision Tree:", accuracy, "%")
