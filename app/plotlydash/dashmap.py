import flask
import dash
from dash import Input, Output, dcc, html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash_extensions.javascript import assign

# df = pd.read_csv(
# r'C:\Users\PC-01\Desktop\m2_project\m2_website\plotlydash\location_for_map.csv')

app = dash.Dash()
app.layout = dl.Map(dl.TileLayer(), style={
                    'width': '1000px', 'height': '500px'})


if __name__ == '__main__':
    app.run_server(debug=True)
