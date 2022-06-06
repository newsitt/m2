import flask
import dash
from dash import Input, Output, dcc, html, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import os
from sqlalchemy import create_engine
import pandas as pd
import statsmodels.api as sm
from decimal import *


# dashboard = flask.Blueprint('dashboard', __name__)
sidebar_style = {
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'width': '20rem',
    'padding': '2rem 1rem',
    'background-color': '#f8f6fa',
}

content_style = {
    'margin-left': '20rem',
    'margin-right': '2rem',
    'padding': '2rem 1rem'
}


# server = flask.Flask(__name__)
dashapp = dash.Dash(__name__,
                    update_title=None,
                    external_stylesheets=[dbc.themes.BOOTSTRAP],
                    suppress_callback_exceptions=True,
                    # server=server,
                    url_base_pathname='/prediction/')

sectorOption1 = [
    {'label': 'เขตปกครองพิเศษ', 'value': 'a1'},
    {'label': 'เทศบาลนคร', 'value': 'a2'},
    {'label': 'เทศบาลเมือง', 'value': 'a3'},
    {'label': 'เทศบาลตำบล', 'value': 'a4'},
    {'label': 'องค์การบริหารส่วนตำบล', 'value': 'a5'},
]

sectorOption2 = [
    {'label': 'เทศบาลนคร', 'value': 'a2'},
    {'label': 'เทศบาลเมือง', 'value': 'a3'},
    {'label': 'เทศบาลตำบล', 'value': 'a4'},
    {'label': 'องค์การบริหารส่วนตำบล', 'value': 'a5'},
]

# !get records from database
path = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(path, 'database.db')
engine = create_engine('sqlite:///'+db_path).connect()
records = pd.read_sql_table('info', con=engine)

# get records from csv format
# location = pd.read_csv(
#     'https://raw.githubusercontent.com/newsitt/m2-showcase/main/all.csv')

# !copy records from database table
df = records.drop(['sector_name', 'lat', 'long', 'address', 'housing', 'income',
                   'housing_size', 'amount_waste_kg', 'waste_rate', 'edit_date', 'id', 'created_at', 'user_id'], axis=1)

# !modify zone to meet value from dropdown
df = df.replace('ภาคเหนือ', 'north')
df = df.replace('ภาคกลาง', 'middle')
df = df.replace('ภาคตะวันออกเฉียงเหนือ', 'north-east')
df = df.replace('ภาคตะวันออก', 'east')
df = df.replace('ภาคใต้', 'south')

waste = 'กรุณาระบุภาคและประเภทขององค์กรบริหารส่วนท้องถิ่น'
w_rate = 'กรุณาระบุภาคและประเภทขององค์กรบริหารส่วนท้องถิ่น'
equat = 'กรุณาระบุภาคและประเภทขององค์กรบริหารส่วนท้องถิ่น'

# !regression function


def regress(x_col, y_col):
    results = sm.OLS(y_col, x_col).fit()
    return results


def regressWithFilter(x_col, y_col):
    '''GO REGRESSION AND THEN RETURN DATAFRAME CONTAINING VARIAABLES, PVALUES, AND PARAMS '''
    # do the regression for 1st commit
    x = x_col
    y = y_col
    results = sm.OLS(y.astype(float), x.astype(float)).fit()
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
    '''WHEN DOES REGRESSION STOP!!!'''
    x = x_col
    y = y_col
    results = sm.OLS(y.astype(float), x.astype(float)).fit()
    dfResults = pd.DataFrame()
    dfResults['pValues'] = results.pvalues.fillna(1)
    dfResults['params'] = results.params
    dfResults = dfResults.reset_index(drop=False)
    dfResults.columns = dfResults.columns.str.replace('index', 'variables')
    dfResults = dfResults[dfResults['variables'].str.contains(
        'const') == False]
    pvalList = dfResults['pValues'].tolist()
    if all(Decimal(i) < 0.05 for i in pvalList) is True:
        stop = True
    else:
        stop = False
    return stop

# !sectorType conversion


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

# !create waste-at-transport pie chart


def transport_pie_chart():
    labels = ['มูลฝอยอินทรีย์', 'กระดาษ', 'พลาสติก', 'แก้ว',
              'โลหะ', 'ผ้าและสิ่งทอ', 'ยาง', 'ไม้', 'ขยะอันตราย', 'อื่นๆ']
    values = [42.37, 8.35, 25.61, 6.8, 1.73, 4.10, 0.75, 1.90, 2.69, 5.69]
    transport_fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
    return transport_fig


dashapp.layout = html.Div(
    children=[
        html.Div(
            children=[
                dbc.Row(
                    html.Div(
                        children=[
                            html.A(
                                html.Button('กลับสู่หน้าหลัก',
                                            id='back_btn'),
                                href="/"
                            ),
                            html.Br(),
                            html.H3(children=['ตำแหน่งที่อยู่']),
                            html.Hr(),
                            html.Div(children=[
                                dbc.Label('ภาค'),
                                dcc.Dropdown(id='zone_dropdown',
                                             options=[{'label': 'ภาคเหนือ',
                                                       'value': 'north'},
                                                      {'label': 'ภาคกลาง',
                                                       'value': 'middle'},
                                                      {'label': 'ภาคตะวันออกเฉียงเหนือ',
                                                       'value': 'north-east'},
                                                      {'label': 'ภาคตะวันออก',
                                                       'value': 'east'},
                                                      {'label': 'ภาคใต้',
                                                       'value': 'south'},
                                                      ],

                                             searchable=False
                                             ),
                                # dcc.Interval(id='interval-component',
                                #              interval=10000,
                                #              n_intervals=0
                                #              ),
                            ]
                            ),
                            html.Div(children=[
                                dbc.Label('องค์กรปกครองส่วนท้องถิ่น'),
                                dcc.Dropdown(
                                    id='sector_dropdown', searchable=False),
                            ]
                            ),
                            html.Br(),
                            html.H3(
                                children=['ค่าที่ต้องระบุเพื่อคาดการณ์']),
                            html.Hr(),
                            html.Div(children=[
                                html.Label(children=['จำนวนประชากร']),
                                html.Br(),
                                dbc.Input(id='population_get',
                                          type='number',
                                          placeholder='ระบุจำนวนประชากร (คน)',)
                            ]
                            ),
                            # html.Button(
                            #     'ยืนยัน', id='submit', n_clicks=0),
                            # html.Button(
                            #     'เริ่มใหม่', id='reset', n_clicks=0),
                            html.Hr(),
                            html.Div(children=[
                                html.H5(id='description-title'),
                                html.P(id='description')
                            ]
                            ),

                        ]
                    )
                ),
            ],
            style=sidebar_style,
        ),
        html.Div(id='page-content', style=content_style,
                 children=[
                     dbc.Row(
                         [
                             html.Div(
                                 children=[
                                     html.H3(
                                         'การคาดการณ์ปริมาณขยะ ณ สถานที่กำจัด'),
                                     html.Table(
                                         children=[
                                             html.Tr(children=[
                                                 html.Td(['ประชากร']),
                                                 html.Td(
                                                     id='population_show'),
                                                 html.Td(['คน']),
                                             ]
                                             ),
                                             html.Tr(children=[
                                                 html.Td(
                                                     ['ปริมาณขยะที่เกิดขึ้น']),
                                                 html.Td(
                                                     id='generate_waste'),
                                                 html.Td(['ตัน/วัน']),
                                             ]
                                             ),
                                             html.Tr(children=[
                                                 html.Td(
                                                     ['อัตราการเกิดขยะ']),
                                                 html.Td(id='waste_rate'),
                                                 html.Td(
                                                     ['กิโลกรัม/คน/วัน']),
                                             ]),
                                             html.Tr(children=[
                                                 html.Td(
                                                     ['สมการที่ใช้คาดการณ์ปริมาณขยะ']),
                                                 html.Td(
                                                     id='predictive_equation'),
                                                 html.Td(),
                                             ]),
                                             html.Br(),
                                             html.H5(
                                                 'หมายเหตุ: สมการการคาดการณ์จากข้อมูลปี พ.ศ.2564'),
                                         ]
                                     ),
                                     html.Br(),

                                 ],
                             ),
                         ],
                     ),
                     dbc.Row(
                         [
                             dbc.Col(
                                 html.Div(
                                     id='from-transport',
                                     children=[
                                         html.H4(
                                             'ภาพรวมองค์ประกอบมูลฝอย ณ สถานีขนถ่าย ของทั้งประเทศ'),
                                         html.Br(),
                                         dcc.Graph(
                                             id='transport-graph', figure=transport_pie_chart()),
                                     ],
                                 ),
                             ),
                             dbc.Col(
                                 html.Div(
                                     id='from-disposal',
                                     children=[
                                         html.H4(
                                             'ภาพรวมองค์ประกอบมูลฝอย ณ สถานที่กำจัด ของทั้งประเทศ'),
                                         html.Br(),
                                         dcc.Graph(
                                             id='disposal-graph',),
                                         html.Br(),
                                         html.Hr(),
                                         html.H4(
                                             'ตารางแสดงปริมาณมูลฝอยประเภทต่างๆ ณ สถานที่กำจัด ของทั้งประเทศ'),
                                         html.Table(children=[
                                             html.Tr(children=[
                                                 html.Td(
                                                     ['มูลฝอยอินทรีย์']),
                                                 html.Td(id='organic'),
                                                 html.Td(['ตัน/วัน']),
                                             ]
                                             ),
                                             html.Tr(children=[
                                                 html.Td(
                                                     ['กระดาษ']),
                                                 html.Td(id='paper',),
                                                 html.Td(['ตัน/วัน']),
                                             ]
                                             ),
                                             html.Tr(children=[
                                                 html.Td(
                                                     ['พลาสติก']),
                                                 html.Td(id='plastic',),
                                                 html.Td(['ตัน/วัน']),
                                             ]
                                             ),
                                             html.Tr(children=[
                                                 html.Td(
                                                     ['แก้ว']),
                                                 html.Td(id='glass',),
                                                 html.Td(['ตัน/วัน']),
                                             ]
                                             ),
                                             html.Tr(children=[
                                                 html.Td(
                                                     ['อะลูมิเนียม']),
                                                 html.Td(id='aluminium',),
                                                 html.Td(['ตัน/วัน']),
                                             ]
                                             ),
                                             html.Tr(children=[
                                                 html.Td(
                                                     ['โลหะ']),
                                                 html.Td(id='metal',),
                                                 html.Td(['ตัน/วัน']),
                                             ]
                                             ),
                                             html.Tr(children=[
                                                 html.Td(
                                                     ['ผ้าและสิ่งทอ']),
                                                 html.Td(id='fiber',),
                                                 html.Td(['ตัน/วัน']),
                                             ]
                                             ),
                                             html.Tr(children=[
                                                 html.Td(
                                                     ['ยาง']),
                                                 html.Td(id='rubber',),
                                                 html.Td(['ตัน/วัน']),
                                             ]
                                             ),
                                             html.Tr(children=[
                                                 html.Td(
                                                     ['ไม้']),
                                                 html.Td(id='wood',),
                                                 html.Td(['ตัน/วัน']),
                                             ]
                                             ),
                                             html.Tr(children=[
                                                 html.Td(
                                                     ['ขยะอันตราย']),
                                                 html.Td(id='danger',),
                                                 html.Td(['ตัน/วัน']),
                                             ]
                                             ),
                                             html.Tr(children=[
                                                 html.Td(
                                                     ['อืนๆ']),
                                                 html.Td(id='etc',),
                                                 html.Td(['ตัน/วัน']),
                                             ]
                                             ),
                                         ],
                                             style={'width': '100%', 'padding': '5px 5px 5px 5px'})
                                     ],
                                 ),
                             ),
                         ],
                     ),
                 ]
                 )
    ]
)
# !dropdown callback
# this callback depends on zone_dropdown.


@ dashapp.callback(
    Output('sector_dropdown', 'options'),
    Input('zone_dropdown', 'value')
)
def set_sector_option(selected_zone):
    if selected_zone == 'middle':
        sectorOption = sectorOption1
    elif selected_zone == 'east':
        sectorOption = sectorOption1
    else:
        sectorOption = sectorOption2
    return sectorOption

# !description callback
# this callback depends on sector_dropdown.


@ dashapp.callback(
    Output('description-title', 'children'),
    Output('description', 'children'),
    Input('sector_dropdown', 'value')
)
def generated_description(selected_sector):
    if selected_sector == 'sector1':
        title = 'องค์กรปกครองส่วนท้องถิ่นรูปแบบพิเศษ'
        text = 'ข้อมูล องค์กรปกครองส่วนท้องถิ่นรูปแบบพิเศษ'
    elif selected_sector == 'sector2':
        title = 'เทศบาลนคร (ทน.)'
        text = 'ข้อมูล เทศบาลนคร (ทน.)'
    elif selected_sector == 'sector3':
        title = 'เทศบาลเมือง (ทม.)'
        text = 'ข้อมูล เทศบาลเมือง (ทม.)'
    elif selected_sector == 'sector4':
        title = 'เทศบาลตำบล (ทต.)'
        text = 'ข้อมูล เทศบาลตำบล (ทต.)'
    elif selected_sector == 'sector5':
        title = 'องค์การบริหารส่วนตำบล (อบต.)'
        text = 'ข้อมูล องค์การบริหารส่วนตำบล (อบต.)'
    return title, text


# !calculation callback
# * this is regression callout


@ dashapp.callback(
    Output('generate_waste', 'children'),
    Output('population_show', 'children'),
    Output('waste_rate', 'children'),
    Output('predictive_equation', 'children'),
    Input('zone_dropdown', 'value'),
    Input('sector_dropdown', 'value'),
    Input('population_get', 'value'),
)
def waste_calculation(zone, sector, pop):
    global df, waste, w_rate, equat
    # !NORTH ZONE
    if zone == 'north':
        # * filter records by zone
        df_north = df.loc[df['zone'] == 'north']

        # *classify sector_type and converted to parameters
        sectorList = df_north['sector_type'].tolist()
        sectorParam = []

        for i in sectorList:
            sectorParam.append(convertSectorVal(i))

        # *create dataframe used in calculation
        dfCalculation = pd.DataFrame(columns=['a1', 'a2', 'a3', 'a4'])

        # *insert data for sectorType
        for i in range(len(sectorParam)):
            dfCalculation.loc[len(dfCalculation)] = sectorParam[i]

        # *insert data for cons, x, and, y
        dfCalculation[['x', 'y']] = df_north[[
            'population', 'amount_waste']].values
        dfCalculation['const'] = 1

        # *convert datatype for each column
        dfCalculation['y'] = pd.to_numeric(dfCalculation['y'], errors='coerce')
        dfCalculation['x'] = pd.to_numeric(dfCalculation['x'], errors='coerce')

        # *exclude NaN-containing rows from DataFrame
        dfCalculation = dfCalculation.dropna()
        df_y = dfCalculation['y']

        # ! first regression -----
        # *assign x and y columns
        x = dfCalculation.drop('y', axis=1)
        y = dfCalculation['y']

        # *commit regression (1)
        model = sm.OLS(y.astype(float), x.astype(float))
        results = model.fit()

        # * create results DataFrame
        dfResults = pd.DataFrame()
        dfResults['pValues'] = results.pvalues.fillna(1)
        dfResults['params'] = results.params
        dfResults = dfResults.reset_index(drop=False)
        dfResults.columns = dfResults.columns.str.replace('index', 'variables')

        # *filter candidates
        dfResults = dfResults.loc[dfResults['pValues'] < 0.05]

        # ! second regression -----
        # * prepare DataFrame: filer variables from previous commit
        dfCalculation = dfCalculation[dfResults['variables'].tolist()]
        dfCalculation['y'] = df_y

        # * const-including condition
        if 'const' in dfCalculation.columns:
            pass
        else:
            dfCalculation['const'] = 1

        # *assign x and y columns
        x = dfCalculation.drop('y', axis=1)
        y = dfCalculation['y']

        # *commit regression (2)
        model = sm.OLS(y.astype(float), x.astype(float))
        results = model.fit()

        # *create result DataFrame
        dfResults = pd.DataFrame()
        dfResults['pValues'] = results.pvalues.fillna(1)
        dfResults['params'] = results.params
        dfResults = dfResults.reset_index(drop=False)
        dfResults.columns = dfResults.columns.str.replace('index', 'variables')
        dfResults = dfResults.loc[dfResults['pValues'] < 0.05]

        # !check if more regression required
        if regressStop(x, y) is False:
            print('MORE REGRESSION!!!')

            # *prepare DataFrame: filer variables from previous commit
            dfCalculation = dfCalculation[dfResults['variables'].tolist()]
            dfCalculation['y'] = df_y

            # * const-including condition
            if 'const' in dfCalculation.columns:
                pass
            else:
                dfCalculation['const'] = 1

            # *assign x and y columns
            x = dfCalculation.drop('y', axis=1)
            y = dfCalculation['y']

            # *commit regression (3)
            model = sm.OLS(y, x)
            results = model.fit()

            # *create result DataFrame
            dfResults = pd.DataFrame()
            dfResults['pValues'] = results.pvalues.fillna(1)
            dfResults['params'] = results.params
            dfResults = dfResults.reset_index(drop=False)
            dfResults.columns = dfResults.columns.str.replace(
                'index', 'variables')
            dfResults = dfResults.loc[dfResults['pValues'] < 0.05]

        else:
            print('NO MORE REGRESSION!!!')
            pass

        # ! calculate predicted waste -----
        # *take const back to DataFrame for calculation
        if 'const' in dfResults['variables']:
            pass
        else:
            dfResults = pd.DataFrame()
            dfResults['pValues'] = results.pvalues.fillna(1)
            dfResults['params'] = results.params
            dfResults = dfResults.reset_index(drop=False)
            dfResults.columns = dfResults.columns.str.replace(
                'index', 'variables')

        # *create var and param lists
        varsList = dfResults['variables'].tolist()
        paramsList = dfResults['params'].tolist()

        # *create list which has only varibles' paramas
        dropconsx = dfResults[dfResults['variables'].str.contains(
            'const|x') == False]

        # *create lists that contain only vars and  pars, respectively
        onlyVars = dropconsx['variables'].tolist()
        onlyPars = dropconsx['params'].tolist()

        # *create dict that key = var and values = par
        varsAndPars = {}
        for key in onlyVars:
            for value in onlyPars:
                varsAndPars[key] = value
                onlyPars.remove(value)
                break

        # *get sum of variables
        resFromVars = 0
        if varsList.count(sector) != 0:
            resFromVars = varsAndPars.get(sector)*1
        else:
            pass

        # *calculation results
        waste = resFromVars+(pop*paramsList[-2])+paramsList[-1]
        w_rate = waste*1000/pop

        # ! create equation -----
        toEquation = dfResults[dfResults['variables'].str.contains(
            'const') == False]
        toEquation = toEquation.drop('pValues', axis=1).round(3)
        cons = dfResults.loc[dfResults['variables'] == 'const'].round(3)
        stringList = []
        varIndex = 0
        for par in toEquation['params'].tolist():
            appendedPar = toEquation['variables'].tolist()[varIndex]
            stringList.append(f'{str(par)}({appendedPar})')
            varIndex += 1
        getConst = cons['params'].tolist()[0]
        equat = 'y = ' + '+'.join(stringList) + f'+({getConst})'

        print(f'zone: {zone}')
        print(f'sector: {sector}')
        print(f'population: {pop} people')
        print(f'waste: {waste} tons/day')
        print(f'waste rate: {w_rate} kg/person/day')
        print(f'the equation: {equat}')

    # ! MIDDLE ZONE ---
    if zone == 'middle':
        # * filter records by zone
        df_middle = df.loc[df['zone'] == 'middle']

        # *classify sector_type and converted to parameters
        sectorList = df_middle['sector_type'].tolist()
        sectorParam = []

        for i in sectorList:
            sectorParam.append(convertSectorVal(i))

        # *create dataframe used in calculation
        dfCalculation = pd.DataFrame(columns=['a1', 'a2', 'a3', 'a4'])

        # *insert data for sectorType
        for i in range(len(sectorParam)):
            dfCalculation.loc[len(dfCalculation)] = sectorParam[i]

        # *insert data for cons, x, and, y
        dfCalculation[['x', 'y']] = df_middle[[
            'population', 'amount_waste']].values
        dfCalculation['const'] = 1

        # *convert datatype for each column
        dfCalculation['y'] = pd.to_numeric(dfCalculation['y'], errors='coerce')
        dfCalculation['x'] = pd.to_numeric(dfCalculation['x'], errors='coerce')

        # *exclude NaN-containing rows from DataFrame
        dfCalculation = dfCalculation.dropna()
        df_y = dfCalculation['y']

        # ! first regression -----
        # *assign x and y columns
        x = dfCalculation.drop('y', axis=1)
        y = dfCalculation['y']

        # *commit regression (1)
        model = sm.OLS(y.astype(float), x.astype(float))
        results = model.fit()

        # * create results DataFrame
        dfResults = pd.DataFrame()
        dfResults['pValues'] = results.pvalues.fillna(1)
        dfResults['params'] = results.params
        dfResults = dfResults.reset_index(drop=False)
        dfResults.columns = dfResults.columns.str.replace('index', 'variables')

        # *filter candidates
        dfResults = dfResults.loc[dfResults['pValues'] < 0.05]

        # ! second regression -----
        # * prepare DataFrame: filer variables from previous commit
        dfCalculation = dfCalculation[dfResults['variables'].tolist()]
        dfCalculation['y'] = df_y

        # * const-including condition
        if 'const' in dfCalculation.columns:
            pass
        else:
            dfCalculation['const'] = 1

        # *assign x and y columns
        x = dfCalculation.drop('y', axis=1)
        y = dfCalculation['y']

        # *commit regression (2)
        model = sm.OLS(y.astype(float), x.astype(float))
        results = model.fit()

        # *create result DataFrame
        dfResults = pd.DataFrame()
        dfResults['pValues'] = results.pvalues.fillna(1)
        dfResults['params'] = results.params
        dfResults = dfResults.reset_index(drop=False)
        dfResults.columns = dfResults.columns.str.replace('index', 'variables')
        dfResults = dfResults.loc[dfResults['pValues'] < 0.05]

        # !check if more regression required
        if regressStop(x, y) is False:
            print('MORE REGRESSION!!!')

            # *prepare DataFrame: filer variables from previous commit
            dfCalculation = dfCalculation[dfResults['variables'].tolist()]
            dfCalculation['y'] = df_y

            # * const-including condition
            if 'const' in dfCalculation.columns:
                pass
            else:
                dfCalculation['const'] = 1

            # *assign x and y columns
            x = dfCalculation.drop('y', axis=1)
            y = dfCalculation['y']

            # *commit regression (3)
            model = sm.OLS(y, x)
            results = model.fit()

            # *create result DataFrame
            dfResults = pd.DataFrame()
            dfResults['pValues'] = results.pvalues.fillna(1)
            dfResults['params'] = results.params
            dfResults = dfResults.reset_index(drop=False)
            dfResults.columns = dfResults.columns.str.replace(
                'index', 'variables')
            dfResults = dfResults.loc[dfResults['pValues'] < 0.05]

        else:
            print('NO MORE REGRESSION!!!')
            pass

        # ! calculate predicted waste -----
        # *take const back to DataFrame for calculation
        if 'const' in dfResults['variables']:
            pass
        else:
            dfResults = pd.DataFrame()
            dfResults['pValues'] = results.pvalues.fillna(1)
            dfResults['params'] = results.params
            dfResults = dfResults.reset_index(drop=False)
            dfResults.columns = dfResults.columns.str.replace(
                'index', 'variables')

        # *create var and param lists
        varsList = dfResults['variables'].tolist()
        paramsList = dfResults['params'].tolist()

        # *create list which has only varibles' paramas
        dropconsx = dfResults[dfResults['variables'].str.contains(
            'const|x') == False]

        # *create lists that contain only vars and  pars, respectively
        onlyVars = dropconsx['variables'].tolist()
        onlyPars = dropconsx['params'].tolist()

        # *create dict that key = var and values = par
        varsAndPars = {}
        for key in onlyVars:
            for value in onlyPars:
                varsAndPars[key] = value
                onlyPars.remove(value)
                break

        # *get sum of variables
        resFromVars = 0
        if varsList.count(sector) != 0:
            resFromVars = varsAndPars.get(sector)*1
        else:
            pass

        # *calculation results
        waste = resFromVars+(pop*paramsList[-2])+paramsList[-1]
        w_rate = waste*1000/pop

        # ! create equation -----
        toEquation = dfResults[dfResults['variables'].str.contains(
            'const') == False]
        toEquation = toEquation.drop('pValues', axis=1).round(3)
        cons = dfResults.loc[dfResults['variables'] == 'const'].round(3)
        stringList = []
        varIndex = 0
        for par in toEquation['params'].tolist():
            appendedPar = toEquation['variables'].tolist()[varIndex]
            stringList.append(f'{str(par)}({appendedPar})')
            varIndex += 1
        getConst = cons['params'].tolist()[0]
        equat = 'y = ' + '+'.join(stringList) + f'+({getConst})'

        print(f'zone: {zone}')
        print(f'sector: {sector}')
        print(f'population: {pop} people')
        print(f'waste: {waste} tons/day')
        print(f'waste rate: {w_rate} kg/person/day')
        print(f'the equation: {equat}')

    # ! NORTH-EAST ZONE ---
    if zone == 'north-east':
        # * filter records by zone
        df_northeast = df.loc[df['zone'] == 'north-east']

        # *classify sector_type and converted to parameters
        sectorList = df_northeast['sector_type'].tolist()
        sectorParam = []

        for i in sectorList:
            sectorParam.append(convertSectorVal(i))

        # *create dataframe used in calculation
        dfCalculation = pd.DataFrame(columns=['a1', 'a2', 'a3', 'a4'])

        # *insert data for sectorType
        for i in range(len(sectorParam)):
            dfCalculation.loc[len(dfCalculation)] = sectorParam[i]

        # *insert data for cons, x, and, y
        dfCalculation[['x', 'y']] = df_northeast[[
            'population', 'amount_waste']].values
        dfCalculation['const'] = 1

        # *convert datatype for each column
        dfCalculation['y'] = pd.to_numeric(dfCalculation['y'], errors='coerce')
        dfCalculation['x'] = pd.to_numeric(dfCalculation['x'], errors='coerce')

        # *exclude NaN-containing rows from DataFrame
        dfCalculation = dfCalculation.dropna()
        df_y = dfCalculation['y']

        # ! first regression -----
        # *assign x and y columns
        x = dfCalculation.drop('y', axis=1)
        y = dfCalculation['y']

        # *commit regression (1)
        model = sm.OLS(y.astype(float), x.astype(float))
        results = model.fit()

        # * create results DataFrame
        dfResults = pd.DataFrame()
        dfResults['pValues'] = results.pvalues.fillna(1)
        dfResults['params'] = results.params
        dfResults = dfResults.reset_index(drop=False)
        dfResults.columns = dfResults.columns.str.replace('index', 'variables')

        # *filter candidates
        dfResults = dfResults.loc[dfResults['pValues'] < 0.05]

        # ! second regression -----
        # * prepare DataFrame: filer variables from previous commit
        dfCalculation = dfCalculation[dfResults['variables'].tolist()]
        dfCalculation['y'] = df_y

        # * const-including condition
        if 'const' in dfCalculation.columns:
            pass
        else:
            dfCalculation['const'] = 1

        # *assign x and y columns
        x = dfCalculation.drop('y', axis=1)
        y = dfCalculation['y']

        # *commit regression (2)
        model = sm.OLS(y.astype(float), x.astype(float))
        results = model.fit()

        # *create result DataFrame
        dfResults = pd.DataFrame()
        dfResults['pValues'] = results.pvalues.fillna(1)
        dfResults['params'] = results.params
        dfResults = dfResults.reset_index(drop=False)
        dfResults.columns = dfResults.columns.str.replace('index', 'variables')
        dfResults = dfResults.loc[dfResults['pValues'] < 0.05]

        # !check if more regression required
        if regressStop(x, y) is False:
            print('MORE REGRESSION!!!')

            # *prepare DataFrame: filer variables from previous commit
            dfCalculation = dfCalculation[dfResults['variables'].tolist()]
            dfCalculation['y'] = df_y

            # * const-including condition
            if 'const' in dfCalculation.columns:
                pass
            else:
                dfCalculation['const'] = 1

            # *assign x and y columns
            x = dfCalculation.drop('y', axis=1)
            y = dfCalculation['y']

            # *commit regression (3)
            model = sm.OLS(y, x)
            results = model.fit()

            # *create result DataFrame
            dfResults = pd.DataFrame()
            dfResults['pValues'] = results.pvalues.fillna(1)
            dfResults['params'] = results.params
            dfResults = dfResults.reset_index(drop=False)
            dfResults.columns = dfResults.columns.str.replace(
                'index', 'variables')
            dfResults = dfResults.loc[dfResults['pValues'] < 0.05]

        else:
            print('NO MORE REGRESSION!!!')
            pass

        # ! calculate predicted waste -----
        # *take const back to DataFrame for calculation
        if 'const' in dfResults['variables']:
            pass
        else:
            dfResults = pd.DataFrame()
            dfResults['pValues'] = results.pvalues.fillna(1)
            dfResults['params'] = results.params
            dfResults = dfResults.reset_index(drop=False)
            dfResults.columns = dfResults.columns.str.replace(
                'index', 'variables')

        # *create var and param lists
        varsList = dfResults['variables'].tolist()
        paramsList = dfResults['params'].tolist()

        # *create list which has only varibles' paramas
        dropconsx = dfResults[dfResults['variables'].str.contains(
            'const|x') == False]

        # *create lists that contain only vars and  pars, respectively
        onlyVars = dropconsx['variables'].tolist()
        onlyPars = dropconsx['params'].tolist()

        # *create dict that key = var and values = par
        varsAndPars = {}
        for key in onlyVars:
            for value in onlyPars:
                varsAndPars[key] = value
                onlyPars.remove(value)
                break

        # *get sum of variables
        resFromVars = 0
        if varsList.count(sector) != 0:
            resFromVars = varsAndPars.get(sector)*1
        else:
            pass

        # *calculation results
        waste = resFromVars+(pop*paramsList[-2])+paramsList[-1]
        w_rate = waste*1000/pop

        # ! create equation -----
        toEquation = dfResults[dfResults['variables'].str.contains(
            'const') == False]
        toEquation = toEquation.drop('pValues', axis=1).round(3)
        cons = dfResults.loc[dfResults['variables'] == 'const'].round(3)
        stringList = []
        varIndex = 0
        for par in toEquation['params'].tolist():
            appendedPar = toEquation['variables'].tolist()[varIndex]
            stringList.append(f'{str(par)}({appendedPar})')
            varIndex += 1
        getConst = cons['params'].tolist()[0]
        equat = 'y = ' + '+'.join(stringList) + f'+({getConst})'

        print(f'zone: {zone}')
        print(f'sector: {sector}')
        print(f'population: {pop} people')
        print(f'waste: {waste} tons/day')
        print(f'waste rate: {w_rate} kg/person/day')
        print(f'the equation: {equat}')

    # ! EAST ZONE ---
    if zone == 'east':
        # * filter records by zone
        df_east = df.loc[df['zone'] == 'east']

        # *classify sector_type and converted to parameters
        sectorList = df_east['sector_type'].tolist()
        sectorParam = []

        for i in sectorList:
            sectorParam.append(convertSectorVal(i))

        # *create dataframe used in calculation
        dfCalculation = pd.DataFrame(columns=['a1', 'a2', 'a3', 'a4'])

        # *insert data for sectorType
        for i in range(len(sectorParam)):
            dfCalculation.loc[len(dfCalculation)] = sectorParam[i]

        # *insert data for cons, x, and, y
        dfCalculation[['x', 'y']] = df_east[[
            'population', 'amount_waste']].values
        dfCalculation['const'] = 1

        # *convert datatype for each column
        dfCalculation['y'] = pd.to_numeric(dfCalculation['y'], errors='coerce')
        dfCalculation['x'] = pd.to_numeric(dfCalculation['x'], errors='coerce')

        # *exclude NaN-containing rows from DataFrame
        dfCalculation = dfCalculation.dropna()
        df_y = dfCalculation['y']

        # ! first regression -----
        # *assign x and y columns
        x = dfCalculation.drop('y', axis=1)
        y = dfCalculation['y']

        # *commit regression (1)
        model = sm.OLS(y.astype(float), x.astype(float))
        results = model.fit()

        # * create results DataFrame
        dfResults = pd.DataFrame()
        dfResults['pValues'] = results.pvalues.fillna(1)
        dfResults['params'] = results.params
        dfResults = dfResults.reset_index(drop=False)
        dfResults.columns = dfResults.columns.str.replace('index', 'variables')

        # *filter candidates
        dfResults = dfResults.loc[dfResults['pValues'] < 0.05]

        # ! second regression -----
        # * prepare DataFrame: filer variables from previous commit
        dfCalculation = dfCalculation[dfResults['variables'].tolist()]
        dfCalculation['y'] = df_y

        # * const-including condition
        if 'const' in dfCalculation.columns:
            pass
        else:
            dfCalculation['const'] = 1

        # *assign x and y columns
        x = dfCalculation.drop('y', axis=1)
        y = dfCalculation['y']

        # *commit regression (2)
        model = sm.OLS(y.astype(float), x.astype(float))
        results = model.fit()

        # *create result DataFrame
        dfResults = pd.DataFrame()
        dfResults['pValues'] = results.pvalues.fillna(1)
        dfResults['params'] = results.params
        dfResults = dfResults.reset_index(drop=False)
        dfResults.columns = dfResults.columns.str.replace('index', 'variables')
        dfResults = dfResults.loc[dfResults['pValues'] < 0.05]

        # !check if more regression required
        if regressStop(x, y) is False:
            print('MORE REGRESSION!!!')

            # *prepare DataFrame: filer variables from previous commit
            dfCalculation = dfCalculation[dfResults['variables'].tolist()]
            dfCalculation['y'] = df_y

            # * const-including condition
            if 'const' in dfCalculation.columns:
                pass
            else:
                dfCalculation['const'] = 1

            # *assign x and y columns
            x = dfCalculation.drop('y', axis=1)
            y = dfCalculation['y']

            # *commit regression (3)
            model = sm.OLS(y, x)
            results = model.fit()

            # *create result DataFrame
            dfResults = pd.DataFrame()
            dfResults['pValues'] = results.pvalues.fillna(1)
            dfResults['params'] = results.params
            dfResults = dfResults.reset_index(drop=False)
            dfResults.columns = dfResults.columns.str.replace(
                'index', 'variables')
            dfResults = dfResults.loc[dfResults['pValues'] < 0.05]

        else:
            print('NO MORE REGRESSION!!!')
            pass

        # ! calculate predicted waste -----
        # *take const back to DataFrame for calculation
        if 'const' in dfResults['variables']:
            pass
        else:
            dfResults = pd.DataFrame()
            dfResults['pValues'] = results.pvalues.fillna(1)
            dfResults['params'] = results.params
            dfResults = dfResults.reset_index(drop=False)
            dfResults.columns = dfResults.columns.str.replace(
                'index', 'variables')

        # *create var and param lists
        varsList = dfResults['variables'].tolist()
        paramsList = dfResults['params'].tolist()

        # *create list which has only varibles' paramas
        dropconsx = dfResults[dfResults['variables'].str.contains(
            'const|x') == False]

        # *create lists that contain only vars and  pars, respectively
        onlyVars = dropconsx['variables'].tolist()
        onlyPars = dropconsx['params'].tolist()

        # *create dict that key = var and values = par
        varsAndPars = {}
        for key in onlyVars:
            for value in onlyPars:
                varsAndPars[key] = value
                onlyPars.remove(value)
                break

        # *get sum of variables
        resFromVars = 0
        if varsList.count(sector) != 0:
            resFromVars = varsAndPars.get(sector)*1
        else:
            pass

        # *calculation results
        waste = resFromVars+(pop*paramsList[-2])+paramsList[-1]
        w_rate = waste*1000/pop

        # ! create equation -----
        toEquation = dfResults[dfResults['variables'].str.contains(
            'const') == False]
        toEquation = toEquation.drop('pValues', axis=1).round(3)
        cons = dfResults.loc[dfResults['variables'] == 'const'].round(3)
        stringList = []
        varIndex = 0
        for par in toEquation['params'].tolist():
            appendedPar = toEquation['variables'].tolist()[varIndex]
            stringList.append(f'{str(par)}({appendedPar})')
            varIndex += 1
        getConst = cons['params'].tolist()[0]
        equat = 'y = ' + '+'.join(stringList) + f'+({getConst})'

        print(f'zone: {zone}')
        print(f'sector: {sector}')
        print(f'population: {pop} people')
        print(f'waste: {waste} tons/day')
        print(f'waste rate: {w_rate} kg/person/day')
        print(f'the equation: {equat}')

    # !SOUTH ZONE
    if zone == 'south':
        # * filter records by zone
        df_south = df.loc[df['zone'] == 'south']

        # *classify sector_type and converted to parameters
        sectorList = df_south['sector_type'].tolist()
        sectorParam = []

        for i in sectorList:
            sectorParam.append(convertSectorVal(i))

        # *create dataframe used in calculation
        dfCalculation = pd.DataFrame(columns=['a1', 'a2', 'a3', 'a4'])

        # *insert data for sectorType
        for i in range(len(sectorParam)):
            dfCalculation.loc[len(dfCalculation)] = sectorParam[i]

        # *insert data for cons, x, and, y
        dfCalculation[['x', 'y']] = df_south[[
            'population', 'amount_waste']].values
        dfCalculation['const'] = 1

        # *convert datatype for each column
        dfCalculation['y'] = pd.to_numeric(dfCalculation['y'], errors='coerce')
        dfCalculation['x'] = pd.to_numeric(dfCalculation['x'], errors='coerce')

        # *exclude NaN-containing rows from DataFrame
        dfCalculation = dfCalculation.dropna()
        df_y = dfCalculation['y']

        # ! first regression -----
        # *assign x and y columns
        x = dfCalculation.drop('y', axis=1)
        y = dfCalculation['y']

        # *commit regression (1)
        model = sm.OLS(y.astype(float), x.astype(float))
        results = model.fit()

        # * create results DataFrame
        dfResults = pd.DataFrame()
        dfResults['pValues'] = results.pvalues.fillna(1)
        dfResults['params'] = results.params
        dfResults = dfResults.reset_index(drop=False)
        dfResults.columns = dfResults.columns.str.replace('index', 'variables')

        # *filter candidates
        dfResults = dfResults.loc[dfResults['pValues'] < 0.05]

        # ! second regression -----
        # * prepare DataFrame: filer variables from previous commit
        dfCalculation = dfCalculation[dfResults['variables'].tolist()]
        dfCalculation['y'] = df_y

        # * const-including condition
        if 'const' in dfCalculation.columns:
            pass
        else:
            dfCalculation['const'] = 1

        # *assign x and y columns
        x = dfCalculation.drop('y', axis=1)
        y = dfCalculation['y']

        # *commit regression (2)
        model = sm.OLS(y.astype(float), x.astype(float))
        results = model.fit()

        # *create result DataFrame
        dfResults = pd.DataFrame()
        dfResults['pValues'] = results.pvalues.fillna(1)
        dfResults['params'] = results.params
        dfResults = dfResults.reset_index(drop=False)
        dfResults.columns = dfResults.columns.str.replace('index', 'variables')
        dfResults = dfResults.loc[dfResults['pValues'] < 0.05]

        # !check if more regression required
        if regressStop(x, y) is False:
            print('MORE REGRESSION!!!')

            # *prepare DataFrame: filer variables from previous commit
            dfCalculation = dfCalculation[dfResults['variables'].tolist()]
            dfCalculation['y'] = df_y

            # * const-including condition
            if 'const' in dfCalculation.columns:
                pass
            else:
                dfCalculation['const'] = 1

            # *assign x and y columns
            x = dfCalculation.drop('y', axis=1)
            y = dfCalculation['y']

            # *commit regression (3)
            model = sm.OLS(y, x)
            results = model.fit()

            # *create result DataFrame
            dfResults = pd.DataFrame()
            dfResults['pValues'] = results.pvalues.fillna(1)
            dfResults['params'] = results.params
            dfResults = dfResults.reset_index(drop=False)
            dfResults.columns = dfResults.columns.str.replace(
                'index', 'variables')
            dfResults = dfResults.loc[dfResults['pValues'] < 0.05]

        else:
            print('NO MORE REGRESSION!!!')
            pass

        # ! calculate predicted waste -----
        # *take const back to DataFrame for calculation
        if 'const' in dfResults['variables']:
            pass
        else:
            dfResults = pd.DataFrame()
            dfResults['pValues'] = results.pvalues.fillna(1)
            dfResults['params'] = results.params
            dfResults = dfResults.reset_index(drop=False)
            dfResults.columns = dfResults.columns.str.replace(
                'index', 'variables')

        # *create var and param lists
        varsList = dfResults['variables'].tolist()
        paramsList = dfResults['params'].tolist()

        # *create list which has only varibles' paramas
        dropconsx = dfResults[dfResults['variables'].str.contains(
            'const|x') == False]

        # *create lists that contain only vars and  pars, respectively
        onlyVars = dropconsx['variables'].tolist()
        onlyPars = dropconsx['params'].tolist()

        # *create dict that key = var and values = par
        varsAndPars = {}
        for key in onlyVars:
            for value in onlyPars:
                varsAndPars[key] = value
                onlyPars.remove(value)
                break

        # *get sum of variables
        resFromVars = 0
        if varsList.count(sector) != 0:
            resFromVars = varsAndPars.get(sector)*1
        else:
            pass

        # *calculation results
        waste = resFromVars+(pop*paramsList[-2])+paramsList[-1]
        w_rate = waste*1000/pop

        # ! create equation -----
        toEquation = dfResults[dfResults['variables'].str.contains(
            'const') == False]
        toEquation = toEquation.drop('pValues', axis=1).round(3)
        cons = dfResults.loc[dfResults['variables'] == 'const'].round(3)
        stringList = []
        varIndex = 0
        for par in toEquation['params'].tolist():
            appendedPar = toEquation['variables'].tolist()[varIndex]
            stringList.append(f'{str(par)}({appendedPar})')
            varIndex += 1
        getConst = cons['params'].tolist()[0]

        equat = 'y = ' + '+'.join(stringList) + f'+({getConst})'

        print(f'zone: {zone}')
        print(f'sector: {sector}')
        print(f'population: {pop} people')
        print(f'waste: {waste} tons/day')
        print(f'waste rate: {w_rate} kg/person/day')
        print(f'the equation: {equat}')

    else:
        pass

    return waste, pop, w_rate, equat

    # ! ---old-version--------------------------------------------------------
    # global df
    # if zone == 'north':
    #     df = df.loc[df['zone'] == 'north']

    #     # *classify sector_type and converted to parameters
    #     sectorList = df['sector_type'].tolist()
    #     sectorParam = []

    #     for i in sectorList:
    #         sectorParam.append(convertSectorVal(i))

    #     # *create dataframe used in calculation
    #     dfCalculation = pd.DataFrame(columns=['a1', 'a2', 'a3', 'a4'])

    #     # *insert data for sectorType
    #     for i in range(len(sectorParam)):
    #         dfCalculation.loc[len(dfCalculation)] = sectorParam[i]

    #     # *insert data for cons, x, and, y
    #     dfCalculation[['x', 'y']] = df[['population', 'amount_waste']].values
    #     dfCalculation['const'] = 1

    #     # *convert datatype for each column
    #     dfCalculation['y'] = pd.to_numeric(dfCalculation['y'], errors='coerce')
    #     dfCalculation['x'] = pd.to_numeric(dfCalculation['x'], errors='coerce')

    #     # *exclude NaN-containing rows from DataFrame
    #     dfCalculation = dfCalculation.dropna()
    #     # df_y = dfCalculation['y']

    #     # 1st commit
    #     # print(dfCalculation.head())
    #     x = dfCalculation.drop('y', axis=1)
    #     y = dfCalculation['y']
    #     # do regression
    #     res_df = regressWithFilter(x_col=x, y_col=y)
    #     # stopCal = regressStop(x_col=x, y_col=y)
    #     # 2nd commit
    #     # prepare DataFrame
    #     dfCalculation = dfCalculation[res_df['variables'].tolist()]
    #     dfCalculation['y'] = df['amount_waste']
    #     # reassign x and y columns
    #     x = dfCalculation.drop('y', axis=1)
    #     y = dfCalculation['y']
    #     # do regression
    #     res_df = regressWithFilter(x_col=x, y_col=y)
    #     # stopCal = regressStop(x_col=x, y_col=y)
    #     paramsList = res_df['params'].tolist()
    #     varsList = res_df['variables'].tolist()
    #     dropconsx = res_df[res_df['variables'].str.contains('x|cons') == False]
    #     onlyVars = dropconsx['variables'].tolist()
    #     onlyPars = dropconsx['params'].tolist()

    #     # if same section found
    #     resFromVars = 0
    #     for var in onlyVars:
    #         for par in onlyPars:
    #             if varsList.count(sector) != 0:
    #                 b = 1
    #                 resFromVars += (par*b)
    #                 # print(b)
    #             else:
    #                 resFromVars += 0
    #                 # print(b)
    #     waste = resFromVars+(pop*paramsList[-2])+paramsList[-1]

    #     toEquation = res_df[res_df['variables'].str.contains('cons') == False]
    #     toEquation = toEquation.drop('pValues', axis=1).round(3)
    #     cons = res_df.loc[res_df['variables'] == 'cons'].round(3)
    #     # print(cons)
    #     # print(toEquation)
    #     stringList = []
    #     # print(toEquation['params'].tolist())
    #     # print(toEquation['variables'].tolist())
    #     varIndex = 0
    #     for par in toEquation['params'].tolist():
    #         appendedPar = toEquation['variables'].tolist()[varIndex]
    #         stringList.append(f'{str(par)}({appendedPar})')
    #         varIndex += 1
    #     # print(stringList)
    #     equat = 'y = ' + '+'.join(stringList) + ''.join(str(c)
    #                                                     for c in cons['params'].tolist())

    # elif zone == 'middle':
    #     df = df.loc[df['zone'] == 'middle']
    #     # classify sector_type and converted to parameters
    #     sectorList = df['sector_type'].tolist()
    #     sectorParam = []

    #     for i in sectorList:
    #         sectorParam.append(convertSectorVal(i))

    #     # create dataframe used in calculation
    #     dfCalculation = pd.DataFrame(columns=['a1', 'a2', 'a3', 'a4'])
    #     # insert data for sectorType
    #     for i in range(len(sectorParam)):
    #         dfCalculation.loc[len(dfCalculation)] = sectorParam[i]
    #     # insert data for cons, x, and, y
    #     dfCalculation['y'] = df['amount_waste']
    #     dfCalculation['x'] = df['population']
    #     dfCalculation['cons'] = 1
    #     # convert datatype for each column
    #     dfCalculation['y'] = pd.to_numeric(dfCalculation['y'], errors='coerce')
    #     dfCalculation['x'] = pd.to_numeric(dfCalculation['x'], errors='coerce')
    #     # exclude NaN-containing rows from DataFrame
    #     dfCalculation = dfCalculation.dropna()

    #     # 1st commit
    #     # print(dfCalculation.head())
    #     x = dfCalculation.drop('y', axis=1)
    #     y = dfCalculation['y']
    #     # do regression
    #     res_df = regressWithFilter(x_col=x, y_col=y)
    #     stopCal = regressStop(x_col=x, y_col=y)
    #     # 2nd commit
    #     # prepare DataFrame
    #     dfCalculation = dfCalculation[res_df['variables'].tolist()]
    #     dfCalculation['y'] = df['amount_waste']
    #     # reassign x and y columns
    #     x = dfCalculation.drop('y', axis=1)
    #     y = dfCalculation['y']
    #     # do regression
    #     res_df = regressWithFilter(x_col=x, y_col=y)
    #     stopCal = regressStop(x_col=x, y_col=y)
    #     paramsList = res_df['params'].tolist()
    #     varsList = res_df['variables'].tolist()
    #     dropconsx = res_df[res_df['variables'].str.contains('x|cons') == False]
    #     onlyVars = dropconsx['variables'].tolist()
    #     onlyPars = dropconsx['params'].tolist()

    #     # if same section found
    #     resFromVars = 0
    #     for var in onlyVars:
    #         for par in onlyPars:
    #             if varsList.count(sector) != 0:
    #                 b = 1
    #                 resFromVars += (par*b)
    #                 # print(b)
    #             else:
    #                 resFromVars += 0
    #                 # print(b)
    #     waste = resFromVars+(pop*paramsList[-2])+paramsList[-1]
    # else:
    #     waste = 0
    # wasteRate = (waste*1000)/pop

    # return waste, pop, wasteRate, equat

    # # ภาคเหนือ
    # if zone == 'north':
    #     # เทศบาลนคร
    #     if sector == 'sector2':
    #         waste = 82.9754 + 0.0013*pop - 5.2651
    #     else:
    #         waste = 0.0013*pop - 5.2651
    # # ภาคกลาง
    # elif zone == 'middle':
    #     waste = 0.0013*pop - 0.6573
    # # ภาคตะวันออกเฉียงเหนือ
    # elif zone == 'north-east':
    #     # เทศบางเมือง
    #     if sector == 'sector3':
    #         waste = 51.5684 + 0.0013*pop - 8.0016
    #     else:
    #         waste = 0.0013*pop - 8.0016
    # # ภาคตะวันออก
    # elif zone == 'east':
    #     # เขตปกครองพิเศษ
    #     if sector == 'sector1':
    #         waste = 174.1710 + 0.0014*pop - 2.1519
    #     # เทศบาลนคร
    #     elif sector == 'sector2':
    #         waste = 135.7430*1 + 0.0014*pop - 2.1519
    #     else:
    #         waste = 0.0014*pop - 2.1519
    # # ภาคใต้
    # elif zone == 'south':
    #     # เทศบาลนคร
    #     if sector == 'sector2':
    #         waste = 39.6355 + 0.0007*pop - 2.5566
    #     # เทศบาลเมือง
    #     elif sector == 'sector3':
    #         waste = 8.8051 + 0.0007*pop - 2.5566
    #     else:
    #         waste = 0.0007*pop - 2.5566
    # w_rate = (waste*1000)/pop
    # return waste, pop, w_rate, equat

# generated graph callback


@ dashapp.callback(
    Output('disposal-graph', 'figure'),
    Input('generate_waste', 'children'))
def disposal_pie_chart(w):
    labels = ['มูลฝอยอินทรีย์', 'กระดาษ', 'พลาสติก', 'แก้ว', 'อะลูมิเนียม',
              'โลหะ', 'ผ้าและสิ่งทอ', 'ยาง', 'ไม้', 'ขยะอันตราย', 'อื่นๆ']
    values = [0.35*w, 0.1*w, 0.32*w, 0.05*w, 0.07*w, 0.13 *
              w, 0.04*w, 0.01*w, 0.01*w, 0.03*w, 0.07*w]
    disposal_fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
    return disposal_fig

# result table callback


@ dashapp.callback(
    Output('organic', 'children'),
    Output('paper', 'children'),
    Output('plastic', 'children'),
    Output('glass', 'children'),
    Output('aluminium', 'children'),
    Output('metal', 'children'),
    Output('fiber', 'children'),
    Output('rubber', 'children'),
    Output('wood', 'children'),
    Output('danger', 'children'),
    Output('etc', 'children'),
    Input('generate_waste', 'children'),)
def value_show(w):
    v1 = 0.35*int(w)
    v2 = 0.1*int(w)
    v3 = 0.32*int(w)
    v4 = 0.05*int(w)
    v5 = 0.07*int(w)
    v6 = 0.13*int(w)
    v7 = 0.04*int(w)
    v8 = 0.01*int(w)
    v9 = 0.01*int(w)
    v10 = 0.03*int(w)
    v11 = 0.07*int(w)
    return v1, v2, v3, v4, v5, v6, v7, v8, v9, v10, v11


if __name__ == '__main__':
    dashapp.run_server(debug=True)
