import numpy as np

def relu(x):
    return np.maximum(0, x)

def mean_squared_error(y_pred, y_true):
    return 0.5 * (y_pred - y_true) ** 2

def forward_pass(X, W1, b1, W2, b2):   
    # Hitung input ke hidden layer
    hidden_input = np.dot(W1, X) + b1
    # Terapkan fungsi aktivasi ReLU
    hidden_output = relu(hidden_input)
    # Hitung input ke output layer
    final_input = np.dot(W2, hidden_output) + b2
    # Ambil nilai prediksi (output layer linear)
    y_pred = final_input[0]

    return y_pred, hidden_output, hidden_input, final_input

def backward_pass(X, y_true, W1, b1, W2, b2, hidden_output, hidden_input, output_input, y_pred):
    """
    Parameters:
    X      : numpy array shape (3,)
    y_true : nilai target (0 atau 1)
    W1     : bobot input -> hidden (4, 3)
    b1     : bias hidden (4,)
    W2     : bobot hidden -> output (1, 4)
    b2     : bias output (1,)

    Returns:
    Tuple: (dW2, db2, dW1, db1) semua dalam bentuk numpy array
    """
    # 1. Hitung error prediksi
    error = y_pred - y_true
    
    # 2. Hitung gradien untuk output layer
    dW2 = error * hidden_output.reshape(1, -1)
    db2 = error
    
    # 3. Hitung gradien untuk hidden layer
    d_hidden = error * W2.reshape(-1)
    d_hidden[hidden_input <= 0] = 0  # Turunan ReLU
    
    # 4. Hitung gradien untuk input layer
    dW1 = np.outer(d_hidden, X)
    db1 = d_hidden

    return dW2, db2, dW1, db1

def train_regression_3epoch():
    # Inisialisasi seed random untuk reproduktibilitas
    np.random.seed(100)
    
    # Data input
    X = np.array([1.0, 2.0, -1.0])
    y_true = 3.5
    
    # Learning rate
    learning_rate = 0.1
    
    # Inisialisasi bobot dan bias
    W1 = np.random.randn(4, 3)  # (4, 3)
    b1 = np.random.randn(4)     # (4,)
    W2 = np.random.randn(1, 4)  # (1, 4)
    b2 = np.random.randn(1)     # (1,)
    
    # Cetak bobot awal
    print("Bobot awal:")
    print("W1:", W1)
    print("b1:", b1)
    print("W2:", W2)
    print("b2:", b2)
    print("-" * 50)
    
    # Loop training
    for epoch in range(3):
        # Forward pass
        y_pred, hidden_output, hidden_input, final_input = forward_pass(X, W1, b1, W2, b2)
        
        # Backward pass
        dW2, db2, dW1, db1 = backward_pass(X, y_true, W1, b1, W2, b2, 
                                          hidden_output, hidden_input, final_input, y_pred)
        
        # Update parameter
        W2 -= learning_rate * dW2
        b2 -= learning_rate * db2
        W1 -= learning_rate * dW1
        b1 -= learning_rate * db1
        
        # Hitung loss
        loss = mean_squared_error(y_pred, y_true)
        
        # Cetak progress dengan format yang lebih ringkas
        print(f"\nEpoch {epoch+1}:")
        print("Gradien:")
        print("dW1:", np.round(dW1, 6))
        print("db1:", np.round(db1, 6))
        print("dW2:", np.round(dW2, 6))
        print("db2:", np.round(db2, 6))
        print("\nBobot yang diupdate:")
        print("W1:", np.round(W1, 6))
        print("b1:", np.round(b1, 6))
        print("W2:", np.round(W2, 6))
        print("b2:", np.round(b2, 6))
        print(f"\nEpoch {epoch+1}, Loss: {loss:.6f}, Prediksi: {y_pred:.6f}")
        print("-" * 50)
        print("\n")  # Tambahkan baris kosong untuk memisahkan epoch

if __name__ == "__main__":
    train_regression_3epoch() 