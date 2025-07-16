import pandas as pd 
import matplotlib.pyplot as plt 
import numpy as np 
import statsmodels.api as sm
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Lasso
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import cross_val_score, GridSearchCV
import pickle

# Load and preprocess data
df = pd.read_csv('eda_data.csv')

# Choose relevant columns 
df_model = df[['avg_salary','Rating','Size','Type of ownership','Industry','Sector','Revenue','num_comp','hourly',
               'employer_provided', 'job_state','same_state','age','python_yn','spark','aws','excel',
               'job_simp','seniority','desc_len']]

# Get dummy variables
df_dum = pd.get_dummies(df_model, drop_first=True)

# Train-test split
X = df_dum.drop('avg_salary', axis=1)
y = df_dum.avg_salary.values
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Multiple Linear Regression using statsmodels
X_sm = sm.add_constant(X)  # Add intercept term
X_sm = X_sm.astype(float)
y = y.astype(float)

model = sm.OLS(y, X_sm)
results = model.fit()
print(results.summary())

# Multiple Linear Regression with sklearn
lm = LinearRegression()
lm.fit(X_train, y_train)
print("Linear Regression CV Score:", np.mean(cross_val_score(lm, X_train, y_train, scoring='neg_mean_absolute_error', cv=3)))

# Lasso Regression
lm_l = Lasso(alpha=0.13)
lm_l.fit(X_train, y_train)
print("Lasso Regression CV Score:", np.mean(cross_val_score(lm_l, X_train, y_train, scoring='neg_mean_absolute_error', cv=3)))

# Tune Lasso Alpha
alpha = []
error = []
for i in range(1, 100):
    a = i / 100
    alpha.append(a)
    lml = Lasso(alpha=a)
    error.append(np.mean(cross_val_score(lml, X_train, y_train, scoring='neg_mean_absolute_error', cv=3)))

plt.plot(alpha, error)
plt.xlabel("Alpha")
plt.ylabel("Negative MAE")

# Show best alpha
df_err = pd.DataFrame(list(zip(alpha, error)), columns=['alpha', 'error'])
print("Best alpha value from Lasso tuning:\n", df_err[df_err.error == max(df_err.error)])

# Random Forest
rf = RandomForestRegressor()
print("Random Forest CV Score:", np.mean(cross_val_score(rf, X_train, y_train, scoring='neg_mean_absolute_error', cv=3)))

# Grid Search on Random Forest
parameters = {
    'n_estimators': range(10, 300, 10),
    'criterion': ('squared_error', 'absolute_error'),  # updated names for sklearn >=1.2
    'max_features': ('auto', 'sqrt', 'log2')
}

gs = GridSearchCV(rf, parameters, scoring='neg_mean_absolute_error', cv=3)
gs.fit(X_train, y_train)

print("Best GridSearch Score:", gs.best_score_)
print("Best Estimator:", gs.best_estimator_)

# Test ensembles
tpred_lm = lm.predict(X_test)
tpred_lml = lm_l.predict(X_test)
tpred_rf = gs.best_estimator_.predict(X_test)

# Evaluate
print("MAE - Linear:", mean_absolute_error(y_test, tpred_lm))
print("MAE - Lasso:", mean_absolute_error(y_test, tpred_lml))
print("MAE - RF:", mean_absolute_error(y_test, tpred_rf))
print("MAE - Avg Ensemble:", mean_absolute_error(y_test, (tpred_lm + tpred_rf) / 2))

# Save the best model
best_model = gs.best_estimator_
pickle.dump({'model': best_model}, open("model_file.p", "wb"))

# Load and predict
with open("model_file.p", "rb") as pickled:
    model_data = pickle.load(pickled)
    model = model_data['model']

# Make a prediction
prediction = model.predict(np.array(list(X_test.iloc[1, :])).reshape(1, -1))[0]
print("Prediction for one test example:", prediction)
print("Actual:", y_test[1])
