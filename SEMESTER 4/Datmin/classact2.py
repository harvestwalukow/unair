import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, accuracy_score
from sklearn.impute import SimpleImputer

data = pd.read_csv('data_cancer.csv')

# memisahkan features and target
X = data.drop('diagnosis', axis=1)  # Assuming 'diagnosis' is the target column
y = data['diagnosis']

# handle missing values
imputer = SimpleImputer(strategy='mean')
X = imputer.fit_transform(X)

# split the data
x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LogisticRegression()

# modeling
model.fit(x_train, y_train)
y_pred = model.predict(x_test)

mylist = []

# confusion Matrix
cm = confusion_matrix(y_test, y_pred)

# accuracy score
acc_logreg = accuracy_score(y_test, y_pred)

mylist.append(acc_logreg)
print(cm)
print(acc_logreg, '%')
