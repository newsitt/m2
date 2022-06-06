from flask import Blueprint, Flask
import dash
from dash import Input, Output, dcc, html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from decimal import *
import pandas as pd
import statsmodels.api as sm
from sqlalchemy import create_engine
import os
from flask_sqlalchemy import SQLAlchemy

dashboard = Blueprint('dashboard', __name__)

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

# ! create used functions


def transport_pie_chart():
    labels = ['มูลฝอยอินทรีย์', 'กระดาษ', 'พลาสติก', 'แก้ว',
              'โลหะ', 'ผ้าและสิ่งทอ', 'ยาง', 'ไม้', 'ขยะอันตราย', 'อื่นๆ']
    values = [42.37, 8.35, 25.61, 6.8, 1.73, 4.10, 0.75, 1.90, 2.69, 5.69]
    transport_fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
    return transport_fig


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


def convertSectorVal(text):
    if text == 'เขตปกครองพิเศษ':
        return [1, 0, 0, 0]
    if text == 'เทศบาลนคร (ทน.)':
        return [0, 1, 0, 0]
    if text == 'เทศบาลเมือง (ทม.)':
        return [0, 0, 1, 0]
    if text == 'เทศบาลตำบล (ทต.)':
        return [0, 0, 0, 1]
    if text == 'องค์การบริหารส่วนตำบล (อบต.)':
        return [0, 0, 0, 0]


# !get records from database
path = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(path, 'database.db')
engine = create_engine('sqlite:///'+db_path).connect()
records = pd.read_sql_table('info', con=engine)

# !copy records from database table
df = records.drop(['sector_name', 'lat', 'long', 'address', 'housing', 'income',
                   'housing_size', 'amount_waste_kg', 'waste_rate', 'edit_date', 'id', 'created_at', 'user_id'], axis=1)

# !modify zone to meet value from dropdown
df = df.replace('ภาคเหนือ', 'north')
df = df.replace('ภาคกลาง', 'middle')
df = df.replace('ภาคตะวันออกเฉียงเหนือ', 'north-east')
df = df.replace('ภาคตะวันออก', 'east')
df = df.replace('ภาคใต้', 'south')

waste = 'กรุณาระบุข้อมูลให้ครบ'
w_rate = 'กรุณาระบุข้อมูลให้ครบ'
equat = 'กรุณาระบุข้อมูลให้ครบ'

#! create dashapp


def create_dash_application(flask_server):
    dashapp = dash.Dash(update_title=None,
                        server=flask_server,
                        name='Prediction',
                        url_base_pathname='/prediction/',
                        external_stylesheets=[dbc.themes.BOOTSTRAP],
                        title='การคาดการณ์ปริมาณขยะที่จะเกิดขึ้น',
                        suppress_callback_exceptions=True,
                        )

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

    dashapp.layout = html.Div(
        children=[
            html.Div(
                children=[
                    dbc.Row(
                        html.Div(
                            children=[
                                html.Div(children=[
                                    html.A(
                                        html.Button(
                                            'กลับสู่หน้าหลัก',
                                            id='back_btn',
                                            style={
                                                'width': '100%',
                                                'height': '100%',
                                                'border': 'none',
                                                'border-radius': '15px',
                                                'color': '#fff',
                                                'background': '#4CAF50',
                                                'display': 'inline-block',
                                                'font-size': '20px'
                                            }

                                        ),
                                        href="/"
                                    ),
                                ],
                                    style={
                                        'width': '100%',
                                        'height': '10%',
                                        'border': '1px solid'
                                }
                                ),
                                html.Br(),
                                html.Div(children=[
                                    html.Img(src='static/nrct-logo.png',
                                             alt='nrct-logo',
                                             style={'width': '100%',
                                                    'height': '100%'}
                                             ),
                                    html.Img(src='static/hsm-logo.png',
                                             alt='hsm-logo',
                                             style={'width': '100%',
                                                    'height': '100%'}
                                             ),
                                ],
                                    style={
                                        'border': '1px solid',
                                        'width': '100%',
                                        'height': '50%',
                                }
                                ),
                                html.Div(children=[
                                    html.Br(),
                                    html.H4(
                                        children=['ค่าที่ต้องระบุเพื่อคาดการณ์']),
                                    html.Hr(),
                                ],
                                    style={
                                    'border': '1px solid',
                                    'margin-top': '5px',
                                }
                                ),
                                html.Div(children=[
                                    html.Label('ภาค'),
                                    dcc.Dropdown(id='zone_dropdown',
                                                 #  options=list(all_options.keys()),
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

                                                 searchable=False,
                                                 placeholder='กรุณาเลือกภาค',
                                                 style={
                                                     'width': '100%',
                                                     'margin-top': '5px'
                                                 }
                                                 ),
                                    html.Br(),
                                    html.Label(
                                        'ประเภทองค์กรปกครองส่วนท้องถิ่น'),
                                    dcc.Dropdown(
                                        id='sector_dropdown',
                                        searchable=False,
                                        placeholder='กรุณาเลือกประเภท อปท.',
                                        style={
                                            'width': '100%',
                                            'margin-top': '5px'
                                        }
                                    ),
                                    html.Br(),
                                    html.Label(children=['จำนวนประชากร']),
                                    dcc.Input(id='population',
                                              type='number',
                                              placeholder='ระบุจำนวนประชากร (คน)',
                                              style={
                                                  'width': '100%',
                                                  'margin-top': '5px'
                                              }
                                              ),

                                ],
                                    style={
                                    'border': '1px solid',
                                    'margin-top': '5px',
                                    'width': '100%',
                                    'padding': '5px 5px 5px 5px'
                                }
                                ),
                                html.Hr(),
                                html.Div(children=[
                                    html.H5(id='description-title'),
                                    html.P(id='description')
                                ],
                                    style={
                                    'border': '1px solid',
                                    'margin-top': '5px',
                                    'width': '100%',
                                    'height': '100%'
                                }
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
                                                            id='popu'),
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
                                                ],
                                                ),
                                                html.Br(),
                                                html.P(
                                                    'หมายเหตุ: สมการการคาดการณ์จากข้อมูลปี พ.ศ.2564')
                                            ],
                                            style={
                                                'text-align': 'left',
                                                'width': '80%',
                                                # 'border': '1px solid',
                                            }
                                        ),
                                        html.Br(),

                                    ],
                                    style={
                                        'border': '1px solid',
                                        'padding-top': '10px',
                                        'padding-left': '20px',
                                        'padding-right': '20px',
                                    }
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
                                                'ภาพรวมองค์ประกอบมูลฝอย ณ สถานีขนถ่าย'),
                                            html.Br(),
                                            dcc.Graph(
                                                id='transport-graph', figure=transport_pie_chart()),
                                        ],
                                        style={}
                                    ),
                                ),
                                dbc.Col(
                                    html.Div(
                                        id='from-disposal',
                                        children=[
                                            html.H4(
                                                'ภาพรวมองค์ประกอบมูลฝอย ณ สถานที่กำจัด'),
                                            html.Br(),
                                            dcc.Graph(
                                                id='disposal-graph',),
                                            html.Br(),
                                            html.Hr(),
                                            html.H4(
                                                'ตารางแสดงปริมาณมูลฝอยประเภทต่างๆ ณ สถานที่กำจัด'),
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
                     ],
                     )
        ]
    )


# callback

# dropdown callback

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


# description callback


    @dashapp.callback(
        Output('description-title', 'children'),
        Output('description', 'children'),
        Input('sector_dropdown', 'value')
    )
    def generated_description(selected_sector):
        if selected_sector == 'sector1':
            title = 'องค์กรปกครองส่วนท้องถิ่นรูปแบบพิเศษ'
            text = 'ประเทศไทยมีการปกครองรูปแบบพิเศษ จำนวน 2 แห่ง คือ กรุงเทพมหานครและเมืองพัทยา โดยกรุงเทพมหานครมีฐานะเป็นนิติบุคคลและเป็นราชการบริหารส่วนท้องถิ่นนครหลวง ซึ่งมีการแบ่งพื้นที่การบริหารออกเป็นเขตและแขวง'
        elif selected_sector == 'sector2':
            title = 'เทศบาลนคร (ทน.)'
            text = 'เทศบาลนคร (ทน.) คือ ท้องถิ่นชุมชนที่มีประชากรตั้งแต่ 50,000 คนขึ้นไปและมีรายได้พอเพียงแก่การที่จะปฏิบัติหน้าที่ซึ่งกำหนดไว้ในกฎหมายว่าด้วยเทศบาล'
        elif selected_sector == 'sector3':
            title = 'เทศบาลเมือง (ทม.)'
            text = 'เทศบาลเมือง (ทม.) คือ ท้องถิ่นที่เป็นที่ตั้งของศาลากลางจังหวัด หรือท้องถิ่นชุมชนที่มีจำนวนประชากรมากกว่า 10,000 คนขึ้นไป และมีรายได้พอควรแก่การที่จะปฏิบัติหน้าที่ซึ่งกำหนดไว้ในพระราชบัญญัติเทศบาล'
        elif selected_sector == 'sector4':
            title = 'เทศบาลตำบล (ทต.)'
            text = 'เทศบาลตำบล (ทต.) คือ ท้องถิ่นที่มีประกาศกระทรวงมหาดไทยในพระราชกฤษฎีกายกฐานะขึ้นเป็นเทศบาลตำบล โดยที่กฎหมายไม่ได้กำหนดไวเอย่างชัดเจนว่าการเป็นเทศบาลตำบลจะต้องมีเงื่อนไขอย่างไร แต่ในทางปฏิบัติกระทรวงมหาดไทยได้ตั้งหลักเกณฑ์การเป็นเทศบาลตำบลว่าพื้นที่จะจัดตั้งเป็นเทศบาลตำบลจะต้องมีรายได้ไม่ต่ำกว่า 12 ล้านบาท (ไม่รวมเงินอุดหนุน) มีประชากรมากกว่า 7,000 คนขึ้นไป และอยู่กันหนาแน่นไม่ต่ำกว่า 1,500 คน/ตารางกิโลเมตร'
        elif selected_sector == 'sector5':
            title = 'องค์การบริหารส่วนตำบล (อบต.)'
            text = 'องค์กรปกครองส่วนท้องถิ่นที่มีขนาดเล็กที่สุดและอยู่ใกล้ชิดประชาชนมากที่สุด มีพื้นที่เท่ากับตำบลแต่ละตำบล จัดตั้งมาจากสภาตำบลที่มีรายได้ตามเกณฑ์ที่กำหนดและมีจำนวนราษฎรไม่น้อยกว่า 2,000 คน'
        return title, text


# calculation callback

    @dashapp.callback(
        Output('generate_waste', 'children'),
        Output('popu', 'children'),
        Output('waste_rate', 'children'),
        Output('predictive_equation', 'children'),
        Input('zone_dropdown', 'value'),
        Input('sector_dropdown', 'value'),
        Input('population', 'value'),
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
            dfCalculation['y'] = pd.to_numeric(
                dfCalculation['y'], errors='coerce')
            dfCalculation['x'] = pd.to_numeric(
                dfCalculation['x'], errors='coerce')

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
            dfResults.columns = dfResults.columns.str.replace(
                'index', 'variables')

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
            dfResults.columns = dfResults.columns.str.replace(
                'index', 'variables')
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
            dfCalculation['y'] = pd.to_numeric(
                dfCalculation['y'], errors='coerce')
            dfCalculation['x'] = pd.to_numeric(
                dfCalculation['x'], errors='coerce')

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
            dfResults.columns = dfResults.columns.str.replace(
                'index', 'variables')

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
            dfResults.columns = dfResults.columns.str.replace(
                'index', 'variables')
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
            dfCalculation['y'] = pd.to_numeric(
                dfCalculation['y'], errors='coerce')
            dfCalculation['x'] = pd.to_numeric(
                dfCalculation['x'], errors='coerce')

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
            dfResults.columns = dfResults.columns.str.replace(
                'index', 'variables')

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
            dfResults.columns = dfResults.columns.str.replace(
                'index', 'variables')
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
            dfCalculation['y'] = pd.to_numeric(
                dfCalculation['y'], errors='coerce')
            dfCalculation['x'] = pd.to_numeric(
                dfCalculation['x'], errors='coerce')

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
            dfResults.columns = dfResults.columns.str.replace(
                'index', 'variables')

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
            dfResults.columns = dfResults.columns.str.replace(
                'index', 'variables')
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
            dfCalculation['y'] = pd.to_numeric(
                dfCalculation['y'], errors='coerce')
            dfCalculation['x'] = pd.to_numeric(
                dfCalculation['x'], errors='coerce')

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
            dfResults.columns = dfResults.columns.str.replace(
                'index', 'variables')

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
            dfResults.columns = dfResults.columns.str.replace(
                'index', 'variables')
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

        return round(waste, 2), pop, round(w_rate, 2), equat

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
    # return waste, pop, w_rate


#  !Disposal pie chart generation

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
        v1 = round(0.35*w, 2)
        v2 = round(0.1*w, 2)
        v3 = round(0.32*w, 2)
        v4 = round(0.05*w, 2)
        v5 = round(0.07*w, 2)
        v6 = round(0.13*w, 2)
        v7 = round(0.04*w, 2)
        v8 = round(0.01*w, 2)
        v9 = round(0.01*w, 2)
        v10 = round(0.03*w, 2)
        v11 = round(0.07*w, 2)
        return v1, v2, v3, v4, v5, v6, v7, v8, v9, v10, v11

    return dashapp
