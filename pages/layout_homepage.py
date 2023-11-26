# Dash
from dash import html
# Pour le layout
from app import app

def Homepage():
    """Créé le layout à renvoyer vers dash.Dash()
    Peut être utile pour ajouter un header supplémentaire sur certaines pages et pas d'autres."""
    layout = html.Div([
        body
    ])
    return layout

# Contenu de la page
body = html.Div(children=[
    html.H1(children='Bienvenue'),
])

# Afficher contenu de la page.
app.layout = Homepage()