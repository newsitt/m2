from ssl import OP_SINGLE_DH_USE
from tkinter import Y
import pandas as pd
import numpy as np
import statsmodels.api as sm
from sqlalchemy import create_engine
import os
from decimal import *
from patsy import dmatrices


def regressStop(x_col, y_col):
    '''WHEN DOES REGRESSION STOP!!!'''
    results = sm.OLS(y_col, x_col).fit()
    # create DataFrame for filering
    # TODO exclude 'const' from dfResults
    dfResults = pd.DataFrame()
    dfResults['pValues'] = results.pvalues.fillna(1)
    dfResults['params'] = results.params
    dfResults = dfResults.reset_index(drop=False)
    dfResults.columns = dfResults.columns.str.replace('index', 'variables')
    dfResults = dfResults[dfResults['variables'].str.contains(
        'const') == False]
    # print(dfResults)

    pvalList = dfResults['pValues'].tolist()
    # print(pvalList)

    if all(Decimal(i) < 0.05 for i in pvalList) is True:
        stop = True
    else:
        stop = False
    return stop


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


# path = os.path.dirname(os.path.abspath(__file__))
# db_path = os.path.join(path, 'database.db')
# engine = create_engine('sqlite:///'+db_path).connect()
# raw = pd.read_sql_table('info', con=engine)

df = raw.drop(['sector_name', 'lat', 'long', 'address', 'housing', 'income',
              'housing_size', 'amount_waste_kg', 'waste_rate', 'edit_date', 'id', 'created_at', 'user_id'], axis=1)

# print(df.head())

df = df.replace('ภาคเหนือ', 'north')
df = df.replace('ภาคกลาง', 'middle')
df = df.replace('ภาคตะวันออกเฉียงเหนือ', 'north-east')
df = df.replace('ภาคตะวันออก', 'east')
df = df.replace('ภาคใต้', 'south')

# * filering DataFrame
df = df.loc[df['zone'] == 'north']

# print(df.head())


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
# print(dfCalculation.head())
# * ----------------------------------------------------------

# * create DataFrame for 1st regression
# * ----------------------------------------------------------
# create DataFrame for regression
# dfCalculation['y'] = df['amount_waste']
# dfCalculation['x'] = df['population']
dfCalculation[['x', 'y']] = df[['population', 'amount_waste']].values
dfCalculation['const'] = 1
# print(dfCalculation)
dfCalculation['y'] = pd.to_numeric(dfCalculation['y'], errors='coerce')
dfCalculation['x'] = pd.to_numeric(dfCalculation['x'], errors='coerce')
dfCalculation = dfCalculation.dropna()
df_y = dfCalculation['y']
# # print(df_y)
x = dfCalculation.drop('y', axis=1)
y = dfCalculation['y']
print(dfCalculation.head())
# print(dfCalculation.isnull().values.any())
# dfCalculation.to_csv(r'C:\Users\PC-01\Desktop\check.csv', index=False)
# print(dfCalculation.dtypes)
# * ----------------------------------------------------------


# # ! first regression ----- #
# # y, X = dmatrices('y ~ a1 + a2 + a3 + a4 + x',
# #                  data=dfCalculation, return_type='dataframe')

# # print(y[:3])
# # print(X[:3])
model = sm.OLS(y.astype(float), x.astype(float))
# model = sm.OLS(formula='y ~ a1 + a2 + a3 + a4 + x', data=dfCalculation)
results = model.fit()
# print(results.summary())
# # print(results.pvalues)

dfResults = pd.DataFrame()
dfResults['pValues'] = results.pvalues.fillna(1)
dfResults['params'] = results.params
dfResults = dfResults.reset_index(drop=False)
dfResults.columns = dfResults.columns.str.replace('index', 'variables')
# print(dfResults)

# # * filter candidates
dfResults = dfResults.loc[dfResults['pValues'] < 0.05]
# dfResults = dfResults[dfResults['variables'].str.contains(
#     'Intercept') == False]


# print(dfResults)


# ! second regression ----- #


dfCalculation = dfCalculation[dfResults['variables'].tolist()]
dfCalculation['y'] = df_y

# * const-including condition
if 'const' in dfCalculation.columns:
    pass
else:
    dfCalculation['const'] = 1

# print(dfCalculation.isnull().values.any())
print(dfCalculation.head())
# print(dfCalculation.dtypes)


x = dfCalculation.drop('y', axis=1)
y = dfCalculation['y']


# paramsList = dfResults['variables'].tolist()
# print(dfResults['variables'].tolist())
# varsNext = '' + ' + '.join(dfResults['variables'].tolist())
# print(varsNext)


# y, X = dmatrices(f'y ~ {varsNext}', data=dfCalculation,
#                  return_type='dataframe')
# print(y[:3])
# print(X[:3])
model = sm.OLS(y.astype(float), x.astype(float))
results = model.fit()
# print(results.summary())
# print(results.pvalues)

dfResults = pd.DataFrame()
dfResults['pValues'] = results.pvalues.fillna(1)
dfResults['params'] = results.params
dfResults = dfResults.reset_index(drop=False)
dfResults.columns = dfResults.columns.str.replace('index', 'variables')
dfResults = dfResults.loc[dfResults['pValues'] < 0.05]


# print(dfResults)

# ! check if no more regression needed

if regressStop(x, y) is False:
    print('MORE REGRESSION!!!')

    dfCalculation = dfCalculation[dfResults['variables'].tolist()]
    dfCalculation['y'] = df_y

    print(dfCalculation.head())

    if 'const' in dfCalculation.columns:
        pass
    else:
        dfCalculation['const'] = 1

    print(dfCalculation.head())

    x = dfCalculation.drop('y', axis=1)
    y = dfCalculation['y']

    model = sm.OLS(y, x)
    results = model.fit()
    # print(results.summary())

    dfResults = pd.DataFrame()
    dfResults['pValues'] = results.pvalues.fillna(1)
    dfResults['params'] = results.params
    dfResults = dfResults.reset_index(drop=False)
    dfResults.columns = dfResults.columns.str.replace('index', 'variables')
    # noConstCase = dfResults
    dfResults = dfResults.loc[dfResults['pValues'] < 0.05]

    # print(dfResults)

else:
    print('NO MORE REGRESSION!!!')
    pass


# ! calculate predicted waste
# * ----------------------------------------------------------
if 'const' in dfResults['variables']:
    # print('const is in the variable column.')
    pass
else:
    # print('const is not in the variable column.')
    dfResults = pd.DataFrame()
    dfResults['pValues'] = results.pvalues.fillna(1)
    dfResults['params'] = results.params
    dfResults = dfResults.reset_index(drop=False)
    dfResults.columns = dfResults.columns.str.replace('index', 'variables')


varsList = dfResults['variables'].tolist()
paramsList = dfResults['params'].tolist()
# print(varsList)
# print(paramsList)

# create list which has only varibles' paramas
dropconsx = dfResults[dfResults['variables'].str.contains(
    'const|x') == False]
# print(dropconsx_vars)

onlyVars = dropconsx['variables'].tolist()
onlyPars = dropconsx['params'].tolist()
# print(onlyVars)
# print(onlyPars)


# if same section found
z = 'a3'  # * assign to sector dropdown
population = 10000  # * assign to population input

# index = 0

# create dict that key = var and values = par
varsAndPars = {}
for key in onlyVars:
    for value in onlyPars:
        varsAndPars[key] = value
        onlyPars.remove(value)
        break
# print(varsAndPars)

resFromVars = 0
if varsList.count(z) != 0:
    resFromVars = varsAndPars.get(z)*1
    # print(resFromVars)
else:
    pass
    # print(resFromVars)
# print(resFromVars)

waste = resFromVars+(population*paramsList[-2])+paramsList[-1]
print(waste)
wasteRate = waste*1000/population
print(wasteRate)

# for var in onlyVars:  # * a1 , a2
#     if varsList.count(z) != 0:  # * selected sector = sector in equation
#         resFromVars += (onlyPars[index]*1)
#         index += 1
#     else:  # * selected sector != sector in equation
#         resFromVars += 0
#         index += 1

# for var in onlyVars:
#     for par in onlyPars:
#         if varsList.count(z) != 0:
#             # if same sector
#             b = 1
#             resFromVars += (par*b)
#             print(par, var)
#         else:
#             # if not same sector
#             resFromVars += 0
#             print(par, var)


# * ----------------------------------------------------------


# ! create equation
# * ----------------------------------------------------------
toEquation = dfResults[dfResults['variables'].str.contains(
    'const') == False]
toEquation = toEquation.drop('pValues', axis=1).round(3)
cons = dfResults.loc[dfResults['variables'] == 'const'].round(3)

stringList = []
showEquation = ''
varIndex = 0
for par in toEquation['params'].tolist():
    appendedPar = toEquation['variables'].tolist()[varIndex]
    stringList.append(f'{str(par)}({appendedPar})')
    varIndex += 1
# print(stringList)
getConst = cons['params'].tolist()[0]
equat = 'y = ' + '+'.join(stringList) + f'+({getConst})'
# ''.join(str(c) for c in cons['params'].tolist())
print(equat)

# # * ----------------------------------------------------------
