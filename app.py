# Dash
import dash
import dash_bootstrap_components as dbc
import warnings

warnings.filterwarnings("ignore")

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO])
app.title = "Chester Project"
app.config.suppress_callback_exceptions = True
server = app.server

# Dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
#from app import app
# Layouts
from pages.header import Navbar
from pages.layout_homepage import Homepage
from pages.layout_page_1 import page_1
from pages.layout_page_2 import page_2
from pages.layout_page_3 import page_3
import warnings
import os
# Open app in webbrowser
import webbrowser
from threading import Timer

# Automatically open app locally at default port
default_port = 8040
def open_browser():
	webbrowser.open_new("http://localhost:{}".format(default_port))

warnings.filterwarnings("ignore")

# Layout rendu par l'application
app.layout = html.Div(children=[
    dcc.Location(id='url', refresh=False),
    Navbar(),
    html.Div(id='page-content')
])

# Callback pour mettre à jour les pages
@app.callback(
    Output(component_id='page-content', component_property='children'),
    Input(component_id='url', component_property='pathname')
)
def display_page(pathname):
    if pathname=='/' or pathname=='/homepage':
        return Homepage()
    elif pathname=='/page_1':
        return page_1()
    elif pathname=='/page_2':
        return page_2()
    elif pathname=='/page_3':
        return page_3()
    elif pathname=='/page_4':
        return page_4()
    else:
        return '404'


if __name__ == '__main__':
    Timer(5, open_browser).start()
    app.run_server(
        host='0.0.0.0', # Pour Docker
        debug=True, # Mettre false pour éviter double loading (mais plus de refresh lors d'un save)
        port=default_port,
        )