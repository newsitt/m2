import pandas as pd
# import numpy as np
import statsmodels.api as sm
from patsy import dmatrices


df = pd.read_csv(
    r'C:\Users\PC-01\Desktop\m2_project\app\data\mid_data_cal.csv')


def regress(x_col, y_col):
    results = sm.OLS(y_col, x_col).fit()
    return results
    # print(results.summary())


# # after drop nan values from DataFrame
# x = df.drop('y1', axis=1)
# y = df['y1']

# print(regress(x, y).summary())

y, X = dmatrices('y1 ~ a1 + a2 + a3 + a4 + cons + x',
                 data=df, return_type='dataframe')
print(y[:3])
print(X[:3])
model = sm.OLS(y, X)
results = model.fit()
print(results.summary())
