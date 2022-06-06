import plotly.graph_objects as go
from dash import dcc, html
import dash_bootstrap_components as dbc

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


def sidebar():
    return html.Div(
        children=[
            dbc.Row(
                html.Div(
                    children=[
                        html.H3(children=['ตำแหน่งที่อยู่']),
                        html.Hr(),
                        html.Div(children=[
                            dbc.Label('ภาค'),
                            dcc.Dropdown(id='zone-dropdown', options=[
                                {'label': 'ภาคเหนือ', 'value': 'z1'},
                                {'label': 'ภาคกลาง', 'value': 'z2'},
                                {'label': 'ภาคตะวันออกเฉียงเหนือ', 'value': 'z3'},
                                {'label': 'ภาคตะวันออก', 'value': 'z4'},
                                {'label': 'ภาคใต้', 'value': 'z5'},
                            ],
                            )
                        ]
                        ),
                        # html.Div(children=[
                        #     dbc.Label('จังหวัด'),
                        #     dcc.Dropdown(id='province-dropdown',
                        #                  options=['cnx', 'bkk'])
                        # ]
                        # ),
                        # html.Div(children=[
                        #     dbc.Label('อำเภอ'),
                        #     dcc.Dropdown(id='district-dropdown', options=[
                        #                  'a', 'b', 'c'])
                        # ]
                        # ),
                        html.Div(children=[
                            dbc.Label('องค์กรปกครองส่วนท้องถิ่น'),
                            dcc.Dropdown(id='organization-dropdown', options=[
                                {'label': 'เขตปกครองพิเศษ', 'value': 'a1'},
                                {'label': 'เทศบาลนคร', 'value': 'a2'},
                                {'label': 'เทศบาลเมือง', 'value': 'a3'},
                                {'label': 'เทศบาลตำบล', 'value': 'a4'},
                                {'label': 'องค์การบริหารส่วนตำบล', 'value': 'a5'},
                            ],
                            )
                        ]
                        ),
                        html.Br(),
                        html.H3(children=['ระบุตัวเลข']),
                        html.Hr(),
                        html.Div(children=[
                            html.Label(children=['จำนวนประชากร']
                                       ),
                            dcc.Input(id='population', type='number',
                                      placeholder='ระบุจำนวนประชากร (คน)',)
                        ]
                        ),

                    ]
                )
            ),
        ],
        style=sidebar_style,
    )


def content():
    return html.Div(id='page-content', style=content_style,
                    children=[
                        dbc.Row(
                            [
                                html.Div(
                                    children=[
                                        html.H3('การคาดการณ์ปริมาณขยะ'),
                                        html.Tr(
                                            children=[
                                                html.Td(
                                                    ['ปริมาณขยะที่เกิดขึ้น']),
                                                html.Td(id='generate_waste'),
                                                html.Td(['ตัน/วัน']),
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


def transport_pie_chart():
    labels = ['มูลฝอยอินทรีย์', 'กระดาษ', 'พลาสติก', 'แก้ว',
              'โลหะ', 'ผ้าและสิ่งทอ', 'ยาง', 'ไม้', 'ขยะอันตราย', 'อื่นๆ']
    values = [42.37, 8.35, 25.61, 6.8, 1.73, 4.10, 0.75, 1.90, 2.69, 5.69]
    transport_fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
    return transport_fig
