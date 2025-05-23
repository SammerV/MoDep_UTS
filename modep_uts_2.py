# -*- coding: utf-8 -*-
"""MODEP - UTS - 2.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1ScRuU7JJ_FQ6lJF9UnOF0YFmMooCs3_z

#MODEL DEPLOYMENT MID EXAM
Nama : Sammer Violeta Liu  
NIM : 2702244611

##**Studi Kasus**
1. Buatlah model machine learning yang berisi proses pre-processing machine
learning, training, dan hasil dari perbadingan 2 algoritma machine learning yaitu Random Forest dan
Xgboost. Ambil algoritma terbaik dan simpan dengan menggunakan pickle. Seluruh proses disimpan
dengan extension .ipynb ✅
2. Seluruh proses training dari algoritma machine learning yang terbaik dibubah
dalam format OOP
3. Membuat code inference/prediction untuk proses deployment
4. Lakukan proses deployment dengan menggunakan Streamlit
dan berikan 2 test case pada Streamlit
5. Berikan penjelasan dari semua langkah-langkah yang telah Anda kerjakan
dalam sebuah video.

##**Load Library**
"""

!pip install category_encoders

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from category_encoders import TargetEncoder
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder, StandardScaler
import xgboost as xgb
from xgboost import XGBClassifier
import pickle
import warnings
warnings.filterwarnings('ignore')

"""##**Class for Data Handling**"""

class DataHandler:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None

    def load_data(self):
        """Load dataset from CSV file"""
        self.df = pd.read_csv(self.file_path)
        return self.df

"""##**Class for Data Preprocessing**"""

import numpy as np
from sklearn.preprocessing import StandardScaler
from category_encoders import TargetEncoder
from sklearn.model_selection import train_test_split

class DataPreprocessor:
    def __init__(self, df, random_state=42, test_size=0.2):
        self.random_state = random_state
        self.test_size = test_size
        self.median_pi = None
        self.outlier_bounds = {}
        self.encoders = {
            'person_gender_encoder': {'female': 0, 'male': 1},
            'person_education_encoder': {v: k for k, v in enumerate(['High School', 'Associate', 'Bachelor', 'Master', 'Doctorate'])},
            'person_home_ownership_encoder': {'RENT': 0, 'OWN': 1, 'MORTGAGE': 2, 'OTHER': 3},
            'previous_loan_defaults_encoder': {'No': 0, 'Yes': 1},
            'target_encoder': TargetEncoder(cols=['loan_intent'])
        }
        self.scaler = StandardScaler()
        self.var_num_x = [
            'person_age', 'person_income', 'person_emp_exp', 'loan_amnt',
            'loan_int_rate', 'loan_percent_income', 'cb_person_cred_hist_length',
            'credit_score'
        ]

    def split_data(self, df, target_col='loan_status'):
        X = df.drop(target_col, axis=1)
        y = df[target_col]

        return train_test_split(
            X, y,
            test_size=self.test_size,
            random_state=self.random_state
        )

    def handle_missing_values(self, X_train, X_test, col='person_income'):
        self.median_pi = X_train[col].median()
        X_train[col] = X_train[col].fillna(self.median_pi)
        X_test[col] = X_test[col].fillna(self.median_pi)
        return X_train, X_test

    def calculate_outlier_bounds(self, train_data, column):
        q1 = train_data[column].quantile(0.25)
        q3 = train_data[column].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        return lower_bound, upper_bound

    def handle_outliers(self, X_train, X_test):
        for col in self.var_num_x:
            lower_bound, upper_bound = self.calculate_outlier_bounds(X_train, col)
            self.outlier_bounds[col] = (lower_bound, upper_bound)

            # Process train set
            X_train[col] = np.where(
                X_train[col] > upper_bound,
                upper_bound,
                np.where(
                    X_train[col] < lower_bound,
                    lower_bound,
                    X_train[col]
                )
            )

            # Process test set with same bounds
            X_test[col] = np.where(
                X_test[col] > upper_bound,
                upper_bound,
                np.where(
                    X_test[col] < lower_bound,
                    lower_bound,
                    X_test[col]
                )
            )

        return X_train, X_test

    def encode_categorical(self, X_train, X_test, y_train):
        # 1. Label Encoding untuk person_gender
        X_train['person_gender'] = X_train['person_gender'].map(
            self.encoders['person_gender_encoder'])
        X_test['person_gender'] = X_test['person_gender'].map(
            self.encoders['person_gender_encoder'])

        # 2. Label (Ordinal) Encoding untuk person_education
        X_train['person_education'] = X_train['person_education'].map(
            self.encoders['person_education_encoder'])
        X_test['person_education'] = X_test['person_education'].map(
            self.encoders['person_education_encoder'])

        # 3. Label Encoding untuk person_home_ownership
        X_train['person_home_ownership'] = X_train['person_home_ownership'].map(
            self.encoders['person_home_ownership_encoder'])
        X_test['person_home_ownership'] = X_test['person_home_ownership'].map(
            self.encoders['person_home_ownership_encoder'])

        # 4. Target Encoding untuk loan_intent
        self.encoders['target_encoder'].fit(X_train[['loan_intent']], y_train)
        X_train['loan_intent'] = self.encoders['target_encoder'].transform(
            X_train[['loan_intent']])
        X_test['loan_intent'] = self.encoders['target_encoder'].transform(
            X_test[['loan_intent']])

        # 5. Label Encoding untuk previous_loan_defaults_on_file
        X_train['previous_loan_defaults_on_file'] = X_train['previous_loan_defaults_on_file'].map(
            self.encoders['previous_loan_defaults_encoder'])
        X_test['previous_loan_defaults_on_file'] = X_test['previous_loan_defaults_on_file'].map(
            self.encoders['previous_loan_defaults_encoder'])

        return X_train, X_test

    def scale_features(self, X_train, X_test):
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        return X_train_scaled, X_test_scaled

    def preprocess_data(self, df):
        X_train, X_test, y_train, y_test = self.split_data(df)
        X_train, X_test = self.handle_missing_values(X_train, X_test)
        X_train, X_test = self.handle_outliers(X_train, X_test)
        X_train, X_test = self.encode_categorical(X_train, X_test, y_train)
        X_train_scaled, X_test_scaled = self.scale_features(X_train, X_test)
        return X_train_scaled, X_test_scaled, y_train, y_test

"""##Class for Model Training"""

from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report

class XGBoostModel:
    def __init__(self, param=None, random_state=42):
        self.param = {
            'colsample_bytree': 1.0,
            'learning_rate': 0.1,
            'max_depth': 6,
            'n_estimators': 300,
            'subsample': 1.0,
            'random_state': random_state
        }
        self.model = XGBClassifier(**self.param)

    def train(self, X_train, y_train):
        self.model.fit(X_train, y_train)

    def evaluate(self, X_test, y_test):
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred)

        print(f"XGBoost Accuracy: {accuracy*100:.2f}%")
        print("XGBoost Classification Report:\n", report)

        return {
            'accuracy': accuracy,
            'classification_report': report,
            'predictions': y_pred
        }

    def predict(self, X):
        return self.model.predict(X)

"""##Example Usage"""

if __name__ == "__main__":
    #    Load data
    data_handler = DataHandler('Dataset_A_loan.csv')
    df = data_handler.load_data()

    #    Preprocessing
    preprocessor = DataPreprocessor(df)
    X_train, X_test, y_train, y_test = preprocessor.preprocess_data(df)

    #    Training Model with XGBoost
    xgb_model = XGBoostModel(random_state=42)
    xgb_model.train(X_train, y_train)

    #    Evaluating Model
    predictions = xgb_model.evaluate(X_test, y_test)

    #    Predicting Example using first row of X_test
    new_sample = X_test[:1]
    sample_pred = xgb_model.predict(new_sample)
    print(f"\nSample prediction: {sample_pred[0]}, Actual: {y_test.iloc[0]}")

    #    Saving in Pickle
    with open('xgb_model.pickle', 'wb') as f:
      pickle.dump({'model': xgb_model.model,
        'scaler': preprocessor.scaler,
        'encoders': {
            'target_encoder': preprocessor.encoders['target_encoder'],
            'person_gender_encoder': preprocessor.encoders['person_gender_encoder'],
            'education_encoder': preprocessor.encoders['person_education_encoder'],
            'home_ownership_encoder': preprocessor.encoders['person_home_ownership_encoder'],
            'loan_defaults_encoder': preprocessor.encoders['previous_loan_defaults_encoder']},
        'outlier_bounds': preprocessor.outlier_bounds,
        'median_income': preprocessor.median_pi}, f)

    #    Loading from Pickle
    with open('xgb_model.pickle', 'rb') as f:
      saved_data = pickle.load(f)
      loaded_model = saved_data['model']
      loaded_scaler=saved_data['scaler']
      loaded_encoders=saved_data['encoders']
      loaded_outlier_bounds=saved_data['outlier_bounds']
      loaded_median_income=saved_data['median_income']

    # Preprocess the new sample and predict using the loaded model
    new_sample2 = pd.DataFrame([{
        'person_age': 21.0,
        'person_gender': 'female',
        'person_education': 'High School',
        'person_income': 12282.0,
        'person_emp_exp': 0,
        'person_home_ownership': 'OWN',
        'loan_amnt': 1000.0,
        'loan_intent': 'EDUCATION',
        'loan_int_rate': 11.14,
        'loan_percent_income': 0.08,
        'cb_person_cred_hist_length': 2.0,
        'credit_score': 504,
        'previous_loan_defaults_on_file': 'Yes'
        }])

    if pd.isnull(new_sample2['person_income'].iloc[0]):
      new_sample2['person_income'] = loaded_median_income

    new_sample2['person_gender'] = new_sample2['person_gender'].map(loaded_encoders['person_gender_encoder'])
    new_sample2['person_education'] = new_sample2['person_education'].map(loaded_encoders['education_encoder'])
    new_sample2['person_home_ownership'] = new_sample2['person_home_ownership'].map(loaded_encoders['home_ownership_encoder'])
    new_sample2['loan_intent'] = loaded_encoders['target_encoder'].transform(new_sample2[['loan_intent']])
    new_sample2['previous_loan_defaults_on_file'] = new_sample2['previous_loan_defaults_on_file'].map(loaded_encoders['loan_defaults_encoder'])

    for col, (low, high) in loaded_outlier_bounds.items():
      new_sample2[col] = np.clip(new_sample2[col], low, high)

    new_sample2_scaled = loaded_scaler.transform(new_sample2)
    prediction = loaded_model.predict(new_sample2_scaled)
    status = [0, 1]
    print(f"Predicted loan_status using the loaded model: {status[prediction[0]]}")