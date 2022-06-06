import pandas as pd
import numpy as np
import statsmodels.api as sm
from sqlalchemy import create_engine
import os
from decimal import *

# df = pd.read_csv(
#     r'C:\Users\PC-01\Desktop\m2_project\app\data\mid_data_cal.csv')
# raw = pd.read_csv(
#     'https://raw.githubusercontent.com/newsitt/m2-showcase/main/all.csv')
# !get records from database
# path = os.path.dirname(os.path.abspath(__file__))
# db_path = os.path.join(path, 'database.db')
# engine = create_engine('sqlite:///'+db_path).connect()
# raw = pd.read_sql_table('info', con=engine)
# print(raw)

# print(df.head())
# print(df.shape)
# print(raw.columns)


# prepare columns for regression
# df = raw.drop(['sector_name', 'lat', 'long', 'address', 'housing', 'income',
#               'housing_size', 'amount_waste_kg', 'waste_rate', 'edit_date', 'id', 'created_at', 'user_id'], axis=1)
df = raw.copy()
df = df.drop(['sector_name', 'lat', 'long', 'address', 'housing', 'income',
              'housing_size', 'amount_waste_kg', 'waste_rate', 'edit_date', 'id', 'created_at', 'user_id'], axis=1)
# print(df.head())
# print(df.columns)

# print(df)
# print(dff)


# create function to get a statistical model


def regress(x_col, y_col):
    results = sm.OLS(y_col, x_col).fit()
    return results
    # print(results.summary())

# conversion function


def sortedZoneVal(text):
    if text == 'ภาคเหนือ':
        return [1, 0, 0, 0, 0]
    if text == 'ภาคกลาง':
        return [0, 1, 0, 0, 0]
    if text == 'ภาคตะวันออกเฉียงเหนือ':
        return [0, 0, 1, 0, 0]
    if text == 'ภาคตะวันออก':
        return [0, 0, 0, 1, 0]
    if text == 'ภาคใต้':
        return [0, 0, 0, 0, 1]


def convertSectorVal(text):
    if text == 'เขตการปกครองพิเศษ':
        return [1, 0, 0, 0]
    if text == 'เทศบาลนคร (ทน.)':
        return [0, 1, 0, 0]
    if text == 'เทศบาลเมือง (ทม.)':
        return [0, 0, 1, 0]
    if text == 'เทศบาลตำบล (ทต.)':
        return [0, 0, 0, 1]
    if text == 'องค์การบริหารส่วนตำบล (อบต.)':
        return [0, 0, 0, 0]


# * replace thai word with eng word for dropdrop_id ----------
# * ----------------------------------------------------------
df = df.replace('ภาคเหนือ', 'north')
df = df.replace('ภาคกลาง', 'middle')
df = df.replace('ภาคตะวันออกเฉียงเหนือ', 'north-east')
df = df.replace('ภาคตะวันออก', 'east')
df = df.replace('ภาคใต้', 'south')
# * ----------------------------------------------------------

df = df.loc[df['zone'] == 'middle']
# print(df.head())

# df = df.query('zone=="middle"', inplace=True)
# df = df[df['zone'].str.contains('middle')]
# print(df)


# # classify sector_type
# sectorList = df['sector_type'].tolist()
# # print(sectorList)
# sectorParam = []

# for i in sectorList:
#     sectorParam.append(convertSectorVal(i))


# # create dataframe used in calculation
# dfCalculation = pd.DataFrame(columns=['a1', 'a2', 'a3', 'a4'])
# for i in range(len(sectorParam)):
#     dfCalculation.loc[len(dfCalculation)] = sectorParam[i]
# dfCalculation['y'] = df['amount_waste']
# dfCalculation['x'] = df['population']
# dfCalculation['cons'] = 1
# dfCalculation['y'] = pd.to_numeric(dfCalculation['y'], errors='coerce')
# dfCalculation['x'] = pd.to_numeric(dfCalculation['x'], errors='coerce')
# dfCalculation = dfCalculation.dropna()
# # print(dfCalculation.head())
# # print(dfCalculation.dtypes)


# # # get x columns
# x = dfCalculation.drop('y', axis=1)
# # print(x.head())
# # print(x)

# # # get y column
# y = dfCalculation['y']
# # print(y.head())
# # print(y)

# create function for return next calculation
# * regression functions -------------------------------------
# * ----------------------------------------------------------

def regressWithFilter(x_col, y_col):
    '''GO REGRESSION AND THEN RETURN DATAFRAME CONTAINING VARIAABLES, PVALUES, AND PARAMS '''
    # do the regression for 1st commit
    results = sm.OLS(y_col, x_col).fit()
    # pVal = results.pvalues.fillna(1)
    # create DataFrame for filering
    dfResults = pd.DataFrame()
    dfResults['pValues'] = results.pvalues.fillna(1)
    dfResults['params'] = results.params
    dfResults = dfResults.reset_index(drop=False)
    dfResults.columns = dfResults.columns.str.replace('index', 'variables')
    # filter candidates
    dfResults = dfResults.loc[dfResults['pValues'] < 0.05]
    # # create lists of varibles, pvalues, params
    # pvaluesList = dfResults['pValues'].tolist()
    # paramsList = dfResults['params'].tolist()
    # vabList = dfResults['variables'].tolist()

    return dfResults


def regressStop(x_col, y_col):
    '''WHEN TO STOP REGRESSION!!!'''
    results = sm.OLS(y_col, x_col).fit()
    # create DataFrame for filering
    dfResults = pd.DataFrame()
    dfResults['pValues'] = results.pvalues.fillna(1)
    dfResults['params'] = results.params
    dfResults = dfResults.reset_index(drop=False)
    dfResults.columns = dfResults.columns.str.replace('index', 'variables')
    pvalList = dfResults['pValues'].tolist()
    # return pvalList
    return all(Decimal(i) < 0.05 for i in pvalList)

# * ----------------------------------------------------------

    # print(regressAndNext(x, y))

    # if regressAndNext(x, y) == []:
    #     print('enough')
    # else:
    #     print('more')

    # # create pValues dataframe: cols = variables, pvalues, and parameters
    # df_test = pd.DataFrame()
    # df_test['pValues'] = regress(x, y).pvalues
    # df_test['params'] = regress(x, y).params
    # df_test = df_test.reset_index(drop=False)
    # df_test.columns = df_test.columns.str.replace('index', 'variables')

    # df_test = df_test.loc[df_test['pValues'] < 0.05]

    # df_test = df_test.round(3)
    # # print(df_test)

    # pvaluesList = df_test['pValues'].tolist()
    # paramsList = df_test['params'].tolist()
    # vabList = df_test['variables'].tolist()
    # print(pvaluesList, paramsList, vabList)
    # # print(pvaluesList)
    # for i in pvaluesList:
    #     if i > 0.05:
    #         print('REGRESSION IS DONE!')
    #         break
    # # create params*varibles
    # eqtStrList = []
    # for i in range(len(paramsList)):
    #     val = eqtStrList.append(str(paramsList[i]))
    #     var = eqtStrList.append(str(vabList[i]))
    # eqtStrList.remove('cons')
    # print(eqtStrList)
    # print('y = ' + ' '.join(eqtStrList))

    # ---develop calculation for embedding---

    # include behind dropdown conditions
    # convert sectors to variables


# * turn sector type to variables (a)
# * ----------------------------------------------------------
sectorList = df['sector_type'].tolist()
# print(sectorList)
sectorParam = []
for i in sectorList:
    sectorParam.append(convertSectorVal(i))
# print(sectorParam)
dfCalculation = pd.DataFrame(columns=['a1', 'a2', 'a3', 'a4'])
for i in range(len(sectorParam)):
    dfCalculation.loc[len(dfCalculation)] = sectorParam[i]
# print(dfCalculation.shape)
# * ----------------------------------------------------------

# * create DataFrame for 1st regression
# * ----------------------------------------------------------
# create DataFrame for regression
# dfCalculation['y'] = df['amount_waste']
# dfCalculation['x'] = df['population']
dfCalculation[['x', 'y']] = df[['population', 'amount_waste']].values
dfCalculation['cons'] = 1
# print(dfCalculation)
dfCalculation['y'] = pd.to_numeric(dfCalculation['y'], errors='coerce')
dfCalculation['x'] = pd.to_numeric(dfCalculation['x'], errors='coerce')
dfCalculation = dfCalculation.dropna()
X = dfCalculation.drop('y', axis=1)
X = sm.add_constant(X)
y = dfCalculation['y']
# print(dfCalculation)
# print(dfCalculation.isnull().values.any())
# dfCalculation.to_csv(r'C:\Users\PC-01\Desktop\check.csv', index=False)
# * ----------------------------------------------------------

# * regression
# * ----------------------------------------------------------
# ! Is this the first regression?
# ! This has been done regression for the first time (sm.OLS(y,x).fit()).
results = sm.OLS(y, X).fit()
# create DataFrame for filering
dfResults = pd.DataFrame()
dfResults['pValues'] = results.pvalues.fillna(1)
dfResults['params'] = results.params
dfResults = dfResults.reset_index(drop=False)
dfResults.columns = dfResults.columns.str.replace('index', 'variables')


dfResults = dfResults.loc[dfResults['pValues'] < 0.05]
# print(dfResults)
# print(dfResults.head())
# print(dfResults.loc[::, ['variables', 'params']])


# # do the regression
# results = regress(x, y)
# pVal = results.pvalues.fillna(1)
# # create DataFrame for comparison
# dfResults = pd.DataFrame()
# dfResults['pValues'] = regress(x, y).pvalues
# dfResults['params'] = regress(x, y).params
# dfResults = dfResults.reset_index(drop=False)
# dfResults.columns = dfResults.columns.str.replace('index', 'variables')
# dfResults = dfResults.loc[dfResults['pValues'] < 0.05]
# pvaluesList = dfResults['pValues'].tolist()
# # print(dfResults)
# paramsList = dfResults['params'].tolist()
# vabList = dfResults['variables'].tolist()

while True:
    # 1st commit
    # print(dfCalculation.head())
    x = dfCalculation.drop('y', axis=1)
    y = dfCalculation['y']
    res_df = regressWithFilter(x_col=x, y_col=y)
    stopCal = regressStop(x_col=x, y_col=y)
    # print(res_df)
    # print(stopCal)
    if stopCal is True:
        print('DONE!!')
        break
    else:
        # 2nd commit
        # prepare DataFrame
        dfCalculation = dfCalculation[res_df['variables'].tolist()]
        dfCalculation['y'] = df['amount_waste']
        # reassign x and y columns
        x = dfCalculation.drop('y', axis=1)
        y = dfCalculation['y']
        # print(dfCalculation.head())
        res_df = regressWithFilter(x_col=x, y_col=y)
        stopCal = regressStop(x_col=x, y_col=y)
        # print(res_df)
        # print(stopCal)
# get params and variables to waste calculation
population = 10000
# print(res_df)


# * return equation for calculation and showing
# * ----------------------------------------------------------
varsList = res_df['variables'].tolist()
paramsList = res_df['params'].tolist()
# create list which has only varibles' paramas
dropconsx = res_df[res_df['variables'].str.contains('x|cons') == False]
# print(dropconsx_vars)

onlyVars = dropconsx['variables'].tolist()
onlyPars = dropconsx['params'].tolist()
# print(onlyVars)
# print(onlyPars)
# if same section found
z = 'a2'
resFromVars = 0
showEquation = ''
for var in onlyVars:
    for par in onlyPars:
        if varsList.count(z) != 0:
            b = 1
            resFromVars += (par*b)
            # print(b)
        else:
            resFromVars += 0
            # print(b)

waste = resFromVars+(population*paramsList[-2])+paramsList[-1]
print(waste)
wasteRate = waste*1000/population
print(wasteRate)
# ------------------------------------------------------------------------


# create show equation to show -------------------------------------------
toEquation = res_df[res_df['variables'].str.contains('cons') == False]
toEquation = toEquation.drop('pValues', axis=1).round(3)
cons = res_df.loc[res_df['variables'] == 'cons'].round(3)
# print(cons)
# print(toEquation)
stringList = []
# print(toEquation['params'].tolist())
# print(toEquation['variables'].tolist())
varIndex = 0
for par in toEquation['params'].tolist():
    appendedPar = toEquation['variables'].tolist()[varIndex]
    stringList.append(f'{str(par)}({appendedPar})')
    varIndex += 1
# print(stringList)
equat = 'y = ' + '+'.join(stringList) + ''.join(str(c)
                                                for c in cons['params'].tolist())
print(equat)

# * ----------------------------------------------------------

# eqtStrList = []
# for i in range(len(paramsList)):
#     val = eqtStrList.append(str(paramsList[i]))
#     var = eqtStrList.append(str(vabList[i]))
# eqtStrList.remove('cons')
# print(eqtStrList)
# print('y = ' + ' '.join(eqtStrList))

# --- (1) ---
# do calculation and fill 'NaN' by 1 to get rid of it
# res_pvalues = regress(x, y).pvalues.fillna(1)
# res_pvalues.index.name = 'var'
# res_pvalues = res_pvalues.loc[res_pvalues < 0.05]
# next_lst = []
# for row in res_pvalues.index:
#     next_lst.append(row)


# print(res_pvalues)


# delete the parameters which have pValues > 0.05
# col_lst = ['a1', 'a2', 'a3', 'a4', 'x', 'cons']
# print(type(col_lst))
# next_lst = []
# print(type(next_lst))
# for col in col_lst:
#     if res_pvalues.loc[col] < 0.05:
#         next_lst.append(col)
# # print(next_lst)
# # print(col_lst)
# # prepare DataFrame for next calculation
# for col in next_lst:
#     # dfCalculation = dfCalculation.drop(col, axis=1)
#     dfCalculation = dfCalculation[next_lst]
# dfCalculation['y'] = df['amount_waste']
# # print(dfCalculation.head())

# # ---(2)---
# # do calculation
# x = dfCalculation.drop('y', axis=1)
# y = dfCalculation['y']
# res_pvalues = regress(x, y).pvalues.fillna(1)
# print(res_pvalues)
# for col in next_lst:
#     if res_pvalues.loc[col] < 0.05:

# print(col_lst)
