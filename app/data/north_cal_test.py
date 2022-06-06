import pandas as pd
import numpy as np
import statsmodels.api as sm

df = pd.read_csv(
    r'C:\Users\PC-01\Desktop\m2_project\app\data\north_data_cal.csv')

# print(df.head())
# print(df.shape)
# print(df.columns)

# getting column names
x = df.drop('y1', axis=1)
# print(x)
y = df['y1']
# print(y)

# create function to get a statistical model


def regress(x_col, y_col):
    results = sm.OLS(y_col, x_col).fit()
    return results


res_pvalues = regress(x, y).pvalues.fillna(1)
# print(res)
# print(regress(x, y))
# print(res.fillna(100))
col_lst = ['a1', 'a2', 'a3', 'a4', 'x']
for x in col_lst:
    if res_pvalues.loc[x] > 0.05:
        col_lst.remove(x)
print(col_lst.append('cons'))
x = df[col_lst]
# print(x)
res_pvalues = regress(x, y).pvalues.fillna(1)
res_params = regress(x, y).params
print(res_pvalues)
print(res_params)

# print(results.params)
# print(type(results.pvalues))
# print(results.pvalues)
