import numpy as np
from sklearn import preprocessing, cross_validation, neighbors
import pandas as pd

df_xlsx = pd.read_csv("tracks.csv")
df.drop('id', 1, inplace=True)

X = np.array(df.drop(['name'],1))
y = np.array(df['class'])

X_train, X_test, y_train, y_test = cross_validation.train_test_split(X,y,test_size=0.4)

clf = neighbors.KNeighborsClassifier()
clf.fit(X_train, y_train)


accuracy = clf.score(X_test, y_test)
print(accuracy)
