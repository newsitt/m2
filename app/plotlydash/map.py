from statistics import mode
from flask import Flask
from dash import Dash, html, dcc, Input, Output
from numpy import var
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc


# create dash application
map_app = Dash(__name__, external_stylesheets=[
               dbc.themes.BOOTSTRAP], title='การค้นหาตำแหน่ง')

location = pd.read_csv(
    r'C:\Users\PC-01\Desktop\m2_project\data\data_for_map.csv',)

# create_map function


def thailand_map():
    fig = px.scatter_mapbox(location, lat='lat', lon='long',
                            hover_name='name', zoom=5, height=800)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


# def zoom_map(place_name_lat_pos, lng_pos):
#     fig = px.scatter_mapbox(lat=[lat_pos], lon=[long_pos], hover_name=[
#                             place_name], zoom=12, height=800)
#     fig.update_layout(mapbox_style="open-street-map")
#     fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
#     return fig


map_app.layout = html.Div(
    children=[
        html.H1(children=['การค้นหาตำแหน่งที่ตั้ง']),
        html.Hr(),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            children=[dcc.Graph(id='shown_location', figure=thailand_map())]),
                    ]
                ),
                dbc.Col(
                    [
                        html.Div(id='location_dropdown',
                                 children=[
                                     html.H3('การแสดงข้อมูลของตำแหน่งที่ตั้ง'),
                                     html.Div(id='search_box',
                                              children=[
                                                  html.Label(
                                                      'กรุณาเลือกตำแหน่งที่ต้องการทราบข้อมูล'),
                                                  dcc.Dropdown(options=[{'label': i, 'value': i} for i in location.name.unique()],
                                                               id='location_dd_selection',
                                                               searchable=True,
                                                               placeholder='ค้นหาตำแหน่งที่ต้องการแสดงข้อมูล',
                                                               clearable=False
                                                               ),
                                                  html.Br(),
                                              ]
                                              ),
                                 ]
                                 ),
                        html.Div(id='shown_data',
                                 children=[
                                     html.Label('ข้อมูล'),
                                     html.Table(id='data_list_table',
                                                children=[
                                                    html.Tr(
                                                        children=[
                                                            html.Td(
                                                                'ชื่อ อปท.'),
                                                            html.Td(id='name'),
                                                        ],
                                                    ),
                                                    html.Tr(
                                                        children=[
                                                            html.Td('ที่อยู่'),
                                                            html.Td(
                                                                id='address'),
                                                        ],
                                                    ),
                                                    html.Tr(
                                                        children=[
                                                            html.Td(
                                                                'จำนวนประชากร'),
                                                            html.Td(
                                                                id='population'),
                                                        ],
                                                    ),
                                                    html.Tr(
                                                        children=[
                                                            html.Td(
                                                                'จำนวนครัวเรือน'),
                                                            html.Td(
                                                                id='housing'),
                                                        ],
                                                    ),
                                                    html.Tr(
                                                        children=[
                                                            html.Td(
                                                                'รายได้เฉลี่ยของประชากร'),
                                                            html.Td(
                                                                id='income'),
                                                        ],
                                                    ),
                                                    html.Tr(
                                                        children=[
                                                            html.Td(
                                                                'ขนาดครัวเรือน'),
                                                            html.Td(
                                                                id='fam_size'),
                                                        ],
                                                    ),
                                                    html.Tr(
                                                        children=[
                                                            html.Td(
                                                                'ปริมาณขยะ'),
                                                            html.Td(
                                                                id='amount_waste'),
                                                        ],
                                                    ),
                                                    html.Tr(
                                                        children=[
                                                            html.Td(
                                                                'อัตราการเกิดขยะ'),
                                                            html.Td(
                                                                id='waste_rate'),
                                                        ],
                                                    ),
                                                ],
                                                )
                                 ],
                                 )
                    ]
                ),
            ]
        )
    ]
)


@map_app.callback(
    # Output('shown_location', 'fig'),
    Output('name', 'children'),
    Output('address', 'children'),
    Output('population', 'children'),
    Output('housing', 'children'),
    Output('income', 'children'),
    Output('fam_size', 'children'),
    Output('amount_waste', 'children'),
    Output('waste_rate', 'children'),
    Input('location_dd_selection', 'value')
)
def display_data(location_selection):
    if location_selection is None:
        # map = thailand_map()
        name_data = 'กรุณาเลือกสถานที่เพื่อแสดงข้อมูล'
        address_data = 'กรุณาเลือกสถานที่เพื่อแสดงข้อมูล'
        population_data = 'กรุณาเลือกสถานที่เพื่อแสดงข้อมูล'
        housing_data = 'กรุณาเลือกสถานที่เพื่อแสดงข้อมูล'
        income_data = 'กรุณาเลือกสถานที่เพื่อแสดงข้อมูล'
        fam_size_data = 'กรุณาเลือกสถานที่เพื่อแสดงข้อมูล'
        amount_waste_data = 'กรุณาเลือกสถานที่เพื่อแสดงข้อมูล'
        waste_rate_data = 'กรุณาเลือกสถานที่เพื่อแสดงข้อมูล'
    else:
        name_data = location_selection
        address_data = location['address'].where(
            location['name'] == location_selection)
        population_data = location['population'].where(
            location['name'] == location_selection)
        housing_data = location['housing'].where(
            location['name'] == location_selection)
        income_data = location['income'].where(
            location['name'] == location_selection)
        fam_size_data = location['fam_size'].where(
            location['name'] == location_selection)
        amount_waste_data = location['amount_waste'].where(
            location['name'] == location_selection)
        waste_rate_data = location['waste_rate'].where(
            location['name'] == location_selection)
        # zoom_lat = location['lat'].where(
        #     location['name'] == location_selection)
        # zoom_long = location['long'].where(
        #     location['name'] == location_selection)
# #       create zoom map
        # zoom_lat_to_zmap = zoom_lat
        # zoom_long_to_zmap = zoom_long
        # data_to_zmap = {'name': [name_data],
        #                 'lat': [zoom_lat_to_zmap],
        #                 'lng': [zoom_long_to_zmap]}
        # dataframe_to_zmap = pd.DataFrame(data_to_zmap)
        # map = px.scatter_mapbox(dataframe_to_zmap,
        #                         lat=['lat'], lon=['lng'], hover_name=['name'], zoom=12, height=800,
        #                         )
        # map.update_layout(mapbox_style="open-street-map",
        #                   margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return name_data, address_data, population_data, housing_data, income_data, fam_size_data, amount_waste_data, waste_rate_data


if __name__ == '__main__':
    map_app.run_server(debug=True)
