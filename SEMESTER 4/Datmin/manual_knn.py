import pandas as pd
import numpy as np
from collections import Counter

def euclidean_distance(x1, x2):
    """Calculate Euclidean distance between two points"""
    return np.sqrt(np.sum((x1 - x2) ** 2))

def knn_predict(X_train, y_train, X_test, k=3):
    """Manual implementation of KNN algorithm"""
    predictions = []
    
    for test_point in X_test:
        # Calculate distances between test point and all training points
        distances = [euclidean_distance(test_point, train_point) for train_point in X_train]
        
        # Get indices of k nearest neighbors
        k_indices = np.argsort(distances)[:k]
        
        # Get labels of k nearest neighbors
        k_nearest_labels = [y_train[i] for i in k_indices]
        
        # Get majority class
        most_common = Counter(k_nearest_labels).most_common(1)
        predictions.append(most_common[0][0])
    
    return predictions

# Load datasets
train_data = pd.read_csv('train_rgb_dataset.csv')
test_data = pd.read_csv('test_rgb_dataset.csv')

# Prepare features (R, G, B) and target (RASA)
X_train = train_data[['R', 'G', 'B']].values
y_train = train_data['RASA'].values
X_test = test_data[['R', 'G', 'B']].values
y_test = test_data['RASA'].values

# Make predictions using k=3
k = 3
predictions = knn_predict(X_train, y_train, X_test, k)

# Calculate accuracy
accuracy = np.mean(predictions == y_test) * 100

# Print results
print("\nKNN Manual Implementation Results:")
print(f"k = {k}")
print("\nPredictions vs Actual:")
for i, (pred, actual) in enumerate(zip(predictions, y_test)):
    print(f"Sample {i+1}: Predicted = {pred}, Actual = {actual}")
print(f"\nAccuracy: {accuracy:.2f}%") 
