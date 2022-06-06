from flask import Flask, Blueprint
from dash import Dash, html, dcc, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import os
from sqlalchemy import create_engine

mapapp = Blueprint('mapapp', __name__)


# !get records from database
path = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(path, 'database.db')
engine = create_engine('sqlite:///'+db_path).connect()
location = pd.read_sql_table('info', con=engine)

df = location
# df = df.fillna('ไม่มีข้อมูล', inplace=True)
# *rename columns in DataFrame
df.rename(columns={
    'lat': 'พิกัดละติจูด',
    'long': 'พิกัดลองติจูด',
    'sector_type': 'ประเภทองค์กรปกครองส่วนท้องถิ่น',
    'population': 'จำนวประชากร (คน)',
    'housing': 'จำนวนครัวเรือน (ครัวเรือน)',
    'income': 'รายได้เฉลี่ย (บาท/คน/ปี)',
    'housing_size': 'ขนาดครัวเรือน (คน/ครัวเรือน)',
    'amount_waste': 'ปริมาณขยะ (ตัน/วัน)',
    'waste_rate': 'อัตราการเกิดขยะ (กิโลกรัม/ตัน/วัน)'
},
    inplace=True
)

# print(df.columns)
df = df.astype({
    'จำนวประชากร (คน)': str,
    'จำนวนครัวเรือน (ครัวเรือน)': str,
    'รายได้เฉลี่ย (บาท/คน/ปี)': str,
    'ขนาดครัวเรือน (คน/ครัวเรือน)': str,
    'ปริมาณขยะ (ตัน/วัน)': str,
    'อัตราการเกิดขยะ (กิโลกรัม/ตัน/วัน)': str,
})
# print(df.dtypes)

df.fillna('ไม่มีข้อมูล', inplace=True)
# print(df[df == 'ไม่มีข้อมูล'].count())
# print(df.isnull().values.any())
# print(df.isnull().sum().sum())

# # !modify zone to meet value from dropdown
# df = df.replace('ภาคเหนือ', 'north')
# df = df.replace('ภาคกลาง', 'middle')
# df = df.replace('ภาคตะวันออกเฉียงเหนือ', 'north-east')
# df = df.replace('ภาคตะวันออก', 'east')
# df = df.replace('ภาคใต้', 'south')

opt = []
# !create dash application


def create_dash_map_application(flask_server):
    map_app = Dash(update_title=None,
                   server=flask_server,
                   external_stylesheets=[dbc.themes.BOOTSTRAP],
                   name='Search',
                   url_base_pathname='/search/',
                   title='การค้นหาตำแหน่ง',
                   suppress_callback_exceptions=True
                   )

    def thailand_map():
        fig = px.scatter_mapbox(df,
                                lat='พิกัดละติจูด',
                                lon='พิกัดลองติจูด',
                                hover_name='sector_name',
                                hover_data=['ประเภทองค์กรปกครองส่วนท้องถิ่น', 'จำนวประชากร (คน)', 'จำนวนครัวเรือน (ครัวเรือน)', 'รายได้เฉลี่ย (บาท/คน/ปี)',
                                            'ขนาดครัวเรือน (คน/ครัวเรือน)', 'ปริมาณขยะ (ตัน/วัน)', 'อัตราการเกิดขยะ (กิโลกรัม/ตัน/วัน)'],
                                zoom=5,
                                height=800)
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        # fig.update_mapboxes(center_lat=15.42817, center_lon=100.48848,)
        return fig
    # create_map function
    map_app.layout = html.Div(
        children=[
            html.Div(children=[
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(
                                    children=[
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
                                        'text-align': 'left'
                                    }
                                )
                            ]
                        ),
                        dbc.Col(
                            [
                                html.Div(
                                    children=[
                                        html.H1(
                                            children=['ฐานข้อมูลปริมาณขยะมูลฝอย']),
                                    ],
                                    style={
                                        'text-align': 'center'
                                    }
                                )

                            ]
                        ),
                        dbc.Col(
                            [
                                html.Div(
                                    children=[
                                        html.A(
                                            html.Button('กลับสู่หน้าหลัก',
                                                        id='back_btn',
                                                        style={
                                                            'width': '30%',
                                                            'height': '100%',
                                                            'border': 'none',
                                                            'border-radius': '15px',
                                                            'color': '#fff',
                                                            'background': '#4CAF50',
                                                            'display': 'inline-block',
                                                            'font-size': '20px'
                                                        }
                                                        ),
                                            href="/"),
                                    ],
                                    style={
                                        'text-align': 'right'
                                    }
                                )
                            ]
                        )
                    ]
                )
            ],
                style={
                'margin-top': '20px',
                'margin-left': '20px',
                'margin-right': '20px'
            }
            ),
            html.Hr(),
            html.Br(),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                children=[dcc.Graph(id='shown_location', figure=thailand_map())]),
                        ],
                        style={
                            'margin': '10px 5px 10px 10px'
                        }
                    ),
                    dbc.Col(
                        [
                            html.Div(id='location_dropdown',
                                     children=[
                                         html.Div(id='search_box',
                                                  children=[
                                                      html.H3(
                                                          'รายละเอียดข้อมูลองค์กรปกครองส่วนท้องถิ่น (อปท.)',
                                                      ),
                                                     html.Label(
                                                         'กรุณาเลือกภาค',
                                                         style={
                                                             'margin-top': '20px'
                                                         }
                                                      ),
                                                      dcc.Dropdown(options=[{'label': 'ภาคเหนือ',
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
                                                                   id='zone_dropdown',
                                                                   placeholder='กรุณาระบุภาค',
                                                                   clearable=False,
                                                                   style={
                                                                       'margin-top': '5px'
                                                      }
                                                      ),
                                                      html.Label(
                                                         'กรุณาเลือกองค์กรปกครองส่วนท้องถิ่น (อปท.) ที่ต้องการทราบข้อมูล',
                                                         style={
                                                             'margin-top': '10px'
                                                         }
                                                      ),
                                                      dcc.Dropdown(
                                                         id='sector_dropdown',
                                                         searchable=True,
                                                         placeholder='กรุณาระบุองค์กรบริหารส่วนท้องถิ่น (อปท.)',
                                                         clearable=False,
                                                         style={
                                                             'margin-top': '5px'
                                                         }
                                                      ),
                                                  ],
                                                  style={
                                                      'padding': '10px 5px 10px 5px'
                                                  }
                                                  ),
                                     ]
                                     ),
                            html.Div(id='shown_data',
                                     children=[
                                        html.Label('ข้อมูลปี พ.ศ.2564'),
                                        html.Table(id='data_list_table',
                                                   children=[
                                                       html.Tr(
                                                           children=[
                                                               html.Td(
                                                                   'ชื่อองค์กรปกครองส่วนท้องถิ่น'),
                                                               html.Td(
                                                                   id='name'),
                                                           ],

                                                       ),
                                                       html.Tr(
                                                           children=[
                                                               html.Td(
                                                                   'ประเภทองค์กรปกครองส่วนท้องถิ่น'
                                                               ),
                                                               html.Td(
                                                                   id='type'
                                                               )
                                                           ]
                                                       ),
                                                       html.Tr(
                                                           children=[
                                                               html.Td(
                                                                   'ที่อยู่'),
                                                               html.Td(
                                                                   id='address'),
                                                           ],
                                                       ),
                                                       html.Tr(
                                                           children=[
                                                               html.Td(
                                                                   'จำนวนประชากร (คน)'),
                                                               html.Td(
                                                                   id='population'),
                                                           ],
                                                       ),
                                                       html.Tr(
                                                           children=[
                                                               html.Td(
                                                                   'จำนวนครัวเรือน (ครัวเรือน)'),
                                                               html.Td(
                                                                   id='housing'),
                                                           ],
                                                       ),
                                                       html.Tr(
                                                           children=[
                                                               html.Td(
                                                                   'รายได้เฉลี่ยของประชากร (บาท/หัว/ปี)'),
                                                               html.Td(
                                                                   id='income'),
                                                           ],
                                                       ),
                                                       html.Tr(
                                                           children=[
                                                               html.Td(
                                                                   'ขนาดครัวเรือน (คน/ครัวเรือน)'),
                                                               html.Td(
                                                                   id='fam_size'),
                                                           ],
                                                       ),
                                                       html.Tr(
                                                           children=[
                                                               html.Td(
                                                                   'ปริมาณขยะ (ตัน/วัน)'),
                                                               html.Td(
                                                                   id='amount_waste'),
                                                           ],
                                                       ),
                                                       html.Tr(
                                                           children=[
                                                               html.Td(
                                                                   'อัตราการเกิดขยะ (กิโลกรัม/คน/วัน)'),
                                                               html.Td(
                                                                   id='waste_rate'),
                                                           ],
                                                       ),
                                                   ],
                                                   style={
                                                       'margin-top': '10px',
                                                       'border': '1px solid',
                                                       'width': '100%',
                                                       'height': '530px',
                                                       'table-layout': 'fixed'

                                                   }
                                                   )
                                     ],
                                     style={
                                         'padding': '10px 5px 10px 5px'
                                     }
                                     )
                        ],
                        style={
                            'margin': '10px 10px 10px 5px'
                        }
                    ),
                ]
            )
        ]
    )

    @map_app.callback(
        Output('sector_dropdown', 'options'),
        Input('zone_dropdown', 'value')
    )
    def dropdown(zone):
        global df, opt
        if zone == 'north':
            print('NORTH')
            df_north = df.loc[df['zone'] == 'ภาคเหนือ']
            opt = [{'label': i, 'value': i}
                   for i in df_north.sector_name.unique()]
            print(opt)

        elif zone == 'middle':
            print('MIDDLE')
            df_middle = df.loc[df['zone'] == 'ภาคกลาง']
            opt = [{'label': i, 'value': i}
                   for i in df_middle.sector_name.unique()]
            print(opt)
        elif zone == 'north-east':
            print('NORTH EAST')
            df_northeast = df.loc[df['zone'] == 'ภาคตะวันออกเฉียงเหนือ']
            opt = [{'label': i, 'value': i}
                   for i in df_northeast.sector_name.unique()]
            print(opt)
        elif zone == 'east':
            print('EAST')
            df_east = df.loc[df['zone'] == 'ภาคตะวันออก']
            opt = [{'label': i, 'value': i}
                   for i in df_east.sector_name.unique()]
            print(opt)
        elif zone == 'south':
            print('SOUTH')
            df_south = df.loc[df['zone'] == 'ภาคใต้']
            opt = [{'label': i, 'value': i}
                   for i in df_south.sector_name.unique()]
            print(opt)
        return opt

    @ map_app.callback(
        Output('name', 'children'),
        Output('type', 'children'),
        Output('address', 'children'),
        Output('population', 'children'),
        Output('housing', 'children'),
        Output('income', 'children'),
        Output('fam_size', 'children'),
        Output('amount_waste', 'children'),
        Output('waste_rate', 'children'),
        Input('sector_dropdown', 'value')
    )
    def display_data(sector):
        if sector is None:
            name_data = 'กรุณาเลือกสถานที่เพื่อแสดงข้อมูล'
            type_data = 'กรุณาเลือกสถานที่เพื่อแสดงข้อมูล'
            address_data = 'กรุณาเลือกสถานที่เพื่อแสดงข้อมูล'
            population_data = 'กรุณาเลือกสถานที่เพื่อแสดงข้อมูล'
            housing_data = 'กรุณาเลือกสถานที่เพื่อแสดงข้อมูล'
            income_data = 'กรุณาเลือกสถานที่เพื่อแสดงข้อมูล'
            fam_size_data = 'กรุณาเลือกสถานที่เพื่อแสดงข้อมูล'
            amount_waste_data = 'กรุณาเลือกสถานที่เพื่อแสดงข้อมูล'
            waste_rate_data = 'กรุณาเลือกสถานที่เพื่อแสดงข้อมูล'
        else:
            name_data = sector
            type_data = df['ประเภทองค์กรปกครองส่วนท้องถิ่น'].where(
                df['sector_name'] == sector)
            address_data = df['address'].where(
                df['sector_name'] == sector)
            population_data = df['จำนวประชากร (คน)'].where(
                df['sector_name'] == sector)
            housing_data = df['จำนวนครัวเรือน (ครัวเรือน)'].where(
                df['sector_name'] == sector)
            income_data = df['รายได้เฉลี่ย (บาท/คน/ปี)'].where(
                df['sector_name'] == sector)
            fam_size_data = df['ขนาดครัวเรือน (คน/ครัวเรือน)'].where(
                df['sector_name'] == sector)
            amount_waste_data = df['ปริมาณขยะ (ตัน/วัน)'].where(
                df['sector_name'] == sector)
            waste_rate_data = df['อัตราการเกิดขยะ (กิโลกรัม/ตัน/วัน)'].where(
                df['sector_name'] == sector)
        return name_data, type_data, address_data, population_data, housing_data, income_data, fam_size_data, amount_waste_data, waste_rate_data

    return map_app


# if __name__ == '__main__':
#     map_app.run_server(debug=True)
