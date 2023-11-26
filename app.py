# Dash
import dash
import dash_bootstrap_components as dbc
import warnings

warnings.filterwarnings("ignore")

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO])
app.title = "Chester Project"
app.config.suppress_callback_exceptions = True
server = app.server