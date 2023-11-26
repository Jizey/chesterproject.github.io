# Dash
import dash
# Pour le Body
from dash import html, dcc
import dash_bootstrap_components as dbc
# Pour les callbacks
from dash.dependencies import Input, Output, State
# Pour le layout
from app import app

import dash_leaflet as dl
from dash_extensions.javascript import assign

import random

def page_3():
    """Créé le layout à renvoyer vers dash.Dash()
    Peut être utile pour ajouter un header supplémentaire sur certaines pages et pas d'autres."""
    layout = html.Div([
        body
    ])
    return layout 

import json
path_json_file = './data/us-states.json'
with open(path_json_file) as json_file:
    features = [feature for feature in json.load(json_file)["features"]]

geojson_url = "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json"
# Create javascript function that filters on feature name.
geojson_filter = assign("function(feature, context){return context.props.hideout == feature.id;}")

# Contenu de la page
body = html.Div([
# UPLOAD
    html.Div([
        html.H1(children='Welcome !'),
        html.H3(children='Have a seat.'),
        html.Center(
            html.Div([
                dbc.Button(id='button_question', children='Random State'),
                dcc.Store(id="stored_random_feature"),
                html.Div(id='random_question'),
            ]),
        ),
        dl.Map(children=[
                dl.TileLayer(),
                # The "normal" geojson layer, colored in grey.
                dl.GeoJSON(url=geojson_url, zoomToBounds=True, options=dict(style=dict(color="grey")), id='geojson'),
                # The "selected" geojson layer, colored in blue (default).
                dl.GeoJSON(url=geojson_url, options=dict(filter=geojson_filter), id="selected"),
                dl.GeoJSON(url=geojson_url, options=dict(style=dict(color="green"), filter=geojson_filter), id="right_answer"),
            ], style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block"}, id="map"),
        html.Center(html.Div(id="state")),
        html.Center(html.Div(id="capital")),
    ]),
# ENDPAGE
    html.Div(id='endpage', style={'height': '200px'})
], #style={'width': '95%', 'margin': 'auto', 'textAlign': 'center'} # Futurs tests pour la mise en page
)

@app.callback(
    Output("random_question", "children"),
    Output("stored_random_feature", "data"),
    Output("map", "children"),
    Input("button_question", "n_clicks"),
)
def random_state(n_clicks):
    random_feature = features[random.randrange(len(features))]
    random_state = random_feature['properties']['name']
    question = f"Where is {random_state} ?"
    children_map = [
                dl.TileLayer(),
                # The "normal" geojson layer, colored in grey.
                dl.GeoJSON(url=geojson_url, zoomToBounds=True, options=dict(style=dict(color="grey")), id='geojson'),
                # The "selected" geojson layer, colored in blue (default).
                dl.GeoJSON(url=geojson_url, options=dict(filter=geojson_filter), id="selected"),
                dl.GeoJSON(url=geojson_url, options=dict(style=dict(color="green"), filter=geojson_filter), id="right_answer"),
    ]
    return question, random_feature, children_map

@app.callback(
    Output("state", "children"),
    Output("selected", "hideout"),
    Output("right_answer", "hideout"),
    Input("geojson", "click_feature"),
    State("stored_random_feature", "data"),
    )
def state_click(feature, random_feature):
    if feature is not None:
        state_clicked = f"{feature['properties']['name']}"
        state = f"{random_feature['properties']['name']}"
        if state_clicked == state:
            answer = f"Congratulations, the right answer was {state} !"
            div_answer = html.Div(children=answer, style={'color': 'lightgreen'})
        else:
            answer = [f"Unfortunately, {state_clicked} is a wrong answer.", f"The right answer was {state}."]
            div_answer = [html.Div(children=answer[0], style={'color': 'red'}),html.Div(children=answer[1], style={'color': 'lightgreen'})]
        return div_answer, feature['id'], random_feature['id']
    else:
        return '', '', ''

# Afficher contenu de la page.
app.layout = page_3()