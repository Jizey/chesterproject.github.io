# Dash
import dash
# Pour le Body
from dash import html, dcc
import dash_bootstrap_components as dbc
# Pour les callbacks
from dash.dependencies import Input, Output, State
# Pour le layout
from app import app

from functions.map_functions import get_us_map_data_frame, try_user_answer, plot_map

import pandas as pd
import plotly.express as px

def page_2():
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
        dcc.Store(id='stored_df'),
        dcc.Input(id="input_user_answer", type="text", placeholder="Name a state"),
        dbc.Button(id="button_input_answer", children="Check answer", n_clicks=0),
# GRAPH 1 ANSWER
        dbc.Row([
            dbc.Col(
                # Loading only first time ?
                #dcc.Loading(
                        dcc.Graph(id='map_quizz', figure=px.choropleth(locationmode="USA-states", scope="usa")),
                #),
                width=10,
            ),
            dbc.Col(
                [
                    html.H4('Your answers :'),
                    html.Br(),
                    html.Span(id='div_answers', children=[])
                ],
                width=2,
            ),
        ]),
        dbc.Row([
            html.Center(
                html.Div([
                    dbc.Button(id="button_show_solution", children="Show Solution", n_clicks=0),
                    dbc.Button(id="button_reset", children="Reset", n_clicks=0),
                ]),
            ),
        ])
    ]),
# ENDPAGE
    html.Div(id='endpage', style={'height': '200px'})
], #style={'width': '95%', 'margin': 'auto', 'textAlign': 'center'} # Futurs tests pour la mise en page
) 

@app.callback(
    Output('stored_df', 'data'),
    Output('map_quizz', 'figure'),
    Output('div_answers', 'children'),
    Input('button_input_answer', 'n_clicks'),
    Input('button_show_solution', 'n_clicks'),
    State('stored_df', 'data'),
    State('input_user_answer', 'value'),
    State('div_answers', 'children')
)
def update_df_answer_and_map(n_clicks_answer, n_clicks_solution, df_json, user_answer, answers):
    color_answer=''
    # upload dataframe
    if n_clicks_solution == 0 and n_clicks_answer == 0:
        df = get_us_map_data_frame(csv_file='./data/states.csv')
        answers = []
    else:
        df = pd.read_json(df_json)
    # SHOW SOLUTION
    if n_clicks_solution >= 1:
        df_updated = df
        df_updated['Answer'] = df['State']
        df_updated['Color'] = 1
        df_updated['Color'][df['Answer'] == 'District of Columbia'] = 0
    # TRY ANSWER
    else:
        df_updated, color_answer = try_user_answer(df, user_answer=user_answer)
    # Plot map
    fig = plot_map(df_updated)
    df_updated_json = df_updated.to_json()
    if answers is not None and user_answer != '':
        answers.append(html.Div(children=user_answer, style={'color': color_answer}))
    return df_updated_json, fig, answers

@app.callback(
    Output('input_user_answer', 'value'),
    Output('button_input_answer', 'n_clicks'),
    Output('button_show_solution', 'n_clicks'),
    Input('button_reset', 'n_clicks'),
)
def reset_button_show_solution(n_clicks):
    return '', 0, 0

# Afficher contenu de la page.
app.layout = page_2()