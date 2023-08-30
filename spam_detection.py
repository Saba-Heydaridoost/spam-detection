# -*- coding: utf-8 -*-
"""spam detection.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1fxl7KHndZAkKoH7ViG8b8cXUVddcECQP
"""

"""
Packages
"""

import pandas as pd
import numpy as np
import pickle

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB


"""
Data
"""
# Reading data
df = pd.read_csv('data.csv', encoding='utf-8', encoding_errors='ignore')
data_df = df.drop(['Unnamed: 0'], axis=1)

# print(data_df.groupby('category').describe())

# Adding an extra column for tokenized labels
data_df['spam'] = data_df['category'].apply(lambda x: 1 if x == 'spam' else 0)

# Splitting data
x_train, x_test, y_train, y_test = train_test_split(data_df.context, data_df.spam, test_size=0.25)

# print('Describing x_train:')
# print(x_train, x_train.describe())

# print('Describing x_test:')
# print(x_test, x_test.describe())

# print('Describing y_train:')
# print(y_train, y_train.describe())

# print('Describing y_test:')
# print(y_test, y_test.describe())

# Creating a CountVectorizer
count_vectorized = CountVectorizer()
x_train_count = count_vectorized.fit_transform(x_train.values.astype(str))

"""
Training model
"""
model = MultinomialNB()
model.fit(x_train_count, y_train)

"""
Saving the model
"""
with open('data/model.pkl', 'wb') as f:
    pickle.dump(model, f)

"""
Testing model
"""

x_test_count = count_vectorized.transform(x_test.values.astype(str))

# Predicting test set with our model
predictions = model.predict(x_test_count)

# Calculating the mean accuracy on the given test data and labels
model.score(x_test_count, y_test)

"""
Saving results to a file
"""
# Encoding tokenized results
pred_str = []
for pred in predictions:
    if pred == 1:
        pred_str.append('spam')
    else:
        pred_str.append('ham')

ref_str = []
for ref in y_test:
    if ref == 1:
        ref_str.append('spam')
    else:
        ref_str.append('ham')

test_result_df = pd.DataFrame()

test_result_df['Reference'] = ref_str
test_result_df['Prediction'] = pred_str

# Saving to csv file
test_result_df.to_csv('results.csv')