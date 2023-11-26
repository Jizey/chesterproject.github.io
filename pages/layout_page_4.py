# Dash
import dash
# Pour le Body
from dash import html, dcc
import dash_bootstrap_components as dbc
# Pour les callbacks
from dash.dependencies import Input, Output, State
# Pour le layout
from app import app

def page_4():
    """Créé le layout à renvoyer vers dash.Dash()
    Peut être utile pour ajouter un header supplémentaire sur certaines pages et pas d'autres."""
    layout = html.Div([
        body
    ])
    return layout 

# Contenu de la page
body = html.Div([
# UPLOAD
    html.Div([
        html.H1(children='Welcome !'),
        html.H3(children='Have a seat.'),
    ]),
# ENDPAGE
    html.Div(id='endpage', style={'height': '200px'})
], #style={'width': '95%', 'margin': 'auto', 'textAlign': 'center'} # Futurs tests pour la mise en page
)

# Afficher contenu de la page.
app.layout = page_4()