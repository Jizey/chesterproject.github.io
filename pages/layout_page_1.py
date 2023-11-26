# Dash
import dash
# Pour le Body
from dash import html, dcc
import dash_bootstrap_components as dbc
# Pour les callbacks
from dash.dependencies import Input, Output, State
# Pour le layout
from app import app

from dash import Dash, dcc, html, Input, Output, State, ctx, MATCH
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import webbrowser
from threading import Timer
import random
import json

from functions.scrapping_functions import wiki_scrap, url_wiki_search, find_urls_for_tests
from functions.scrapping_functions import get_first_image_from_name
from functions.questions_functions import generate_possibilities, generate_question, show_question

def page_1():
    """Créé le layout à renvoyer vers dash.Dash()
    Peut être utile pour ajouter un header supplémentaire sur certaines pages et pas d'autres."""
    layout = html.Div([
        body
    ])
    return layout 

#score de départ
score = 1
# On récupère la liste des urls testables pour nos fonctions de scrapping
list_url = find_urls_for_tests(url_wiki_search)

body = html.Div(children=[
    html.H1(children='Chester Project'),

    html.Div(children='''
        C'est l'heure du Quizz.
    '''),
# SETTINGS
    dbc.Row([
        dbc.Col(
            html.Div([
                html.Label('Score'),
                html.Div(id='div_score', children=score),
            ]),
        ),
        dbc.Col(

        ),
        dbc.Col(
            html.Div([
                html.Label(['Settings']),
                html.Div([
                    html.Label(['Afficher images (chargement plus long).']),
                    dcc.RadioItems(
                        options=[
                            {'label': 'Oui', 'value': True},
                            {'label': 'Non', 'value': False},
                        ],
                        value=False,
                        inline=True,
                        id='radio_activate_images',
                    ),
                ]),
                html.Div([
                    html.Label(['Nombre de possibilités.']),
                    dcc.Slider(
                        min=2,
                        max=10,
                        step=1,
                        value=4,
                        id='slider_nb_possibilities'
                    ),
                ]),
            ])
            , width=5
        ),
    ]),
# CHOOSE URL OR RANDOM
    dbc.Row([
        dcc.Dropdown(
            options = [
                {'label': url.split('wiki/')[-1], 'value':url} for url in sorted(list_url)
                ],
            id='dropdown_url',
            style={'color': 'black', 'width': '75%'},
            clearable=False,
        ),
        html.Center(
            dbc.Button('Random', id='button_random_url', n_clicks=0, color='secondary'),
        ),
    ]),
# QUESTION, BUTTONS AND ANSWER
    dbc.Row([
        html.Center(
            dbc.Button('Generate Question', id='button_generate_question', n_clicks=0, color='secondary'),
        ),
        dcc.Loading(
            html.Center([
                dcc.Store(id='dataframe_url'),
                html.Div(id='name_column_url'),
                dcc.Store(id='dict_good_answer'),

                html.Div(id='div_question'),
                html.Div(id='div_possibilities'),

                html.Div(id='answer'),
                html.Div(id='nb_buttons'),

                html.Div(id='div_answer'),
            ]),
        ),  
    ]),
    # ENDPAGE
    html.Div(style={'height': '200px'}),
])

@app.callback(
    Output('dropdown_url', 'value'),
    Input('button_random_url', 'n_clicks'),
)
def update_output(n_clicks):
    tested_url = list_url[random.randrange(len(list_url))]
    if n_clicks == 0:
        tested_url = 'https://en.wikipedia.org/wiki/List_of_presidents_of_the_United_States'
    return tested_url

@app.callback(
    Output('dataframe_url', 'data'),
    Output('name_column_url', 'children'),
    Input('dropdown_url', 'value'),
)
def update_output(tested_url):
    df, name_column = wiki_scrap(tested_url)
    df = df.to_json()
    return df, name_column

@app.callback(
    Output('div_question', 'children'),
    Output('div_possibilities', 'children'),
    Output('dict_good_answer', 'data'),
    Input('button_generate_question', 'n_clicks'),
    Input('dataframe_url', 'data'),
    State('radio_activate_images', 'value'),
    State('name_column_url', 'children'),
    State('dropdown_url', 'value'),
    State('slider_nb_possibilities', 'value'),
    State('div_possibilities', 'children'),
    prevent_initial_call=True,
)
def update_output(n_clicks, df_json, active, name_column, url, nb_possibilities, children_div_possibilities):
    # Generate questions and answers
    df = pd.read_json(df_json)
    country = url.split('List')[-1].split('of_presidents')[-1].replace('_', ' ')[1:]
    nb_president, all_answers, answer = generate_possibilities(df, name_column, nb_possibilities)
    question, possibilities, answer = generate_question(nb_president, country, all_answers, answer)
    # Dictionnary for the answer (name and color button)
    name_answer = answer.split(' (')[0]
    good_answer = {'name': name_answer, 'color': 'bg-success'}
    # Create divs with images and button answers
    div_question = html.Div([html.Label([question]), html.Div([possibilities])])
    div_possibilities = html.Div([
        dbc.Row([
            dbc.Col(
                html.Div([
                    html.Div([
                        get_first_image_from_name(name, active)
                    ]),
                    html.Div([
                        dbc.Button(
                            children=name,
                            id={
                                'type': 'dynamic-button',
                                'index': i,
                            },
                            size='lg',
                            color='warning',
                            outline=True,
                        )
                    ])
                ])
            , width=5
            ) for i, name in enumerate(all_answers)
        ]),
    ]),
    good_answer_json = json.dumps(good_answer)
    return div_question, div_possibilities, good_answer_json

@app.callback(
    Output({'type': 'dynamic-button', 'index': MATCH}, 'class_name'),
    Input({'type': 'dynamic-button', 'index': MATCH}, 'n_clicks'),
    State({'type': 'dynamic-button', 'index': MATCH}, 'children'),
    State('dict_good_answer', 'data'),
    prevent_initial_call=True,
) 
def update_output(n_clicks, button_name, good_answer_json):
    good_answer = json.loads(good_answer_json)
    if button_name == good_answer.get('name'):
        return 'bg-success'
    return 'bg-danger'

"""@app.callback(
    Output('div_answer', 'children'),
    Input({'type': 'dynamic-button', 'index': MATCH}, 'class_name'),
)
def update_output(button_class_name):
    if button_class_name == 'bg-success':
        answer = f'Félicitations, c\'était bien {button_name}'
        return dbc.Button(children=answer, color='success')
    answer = f'Navré, la bonne réponse était {button_name}'
    return dbc.Button(children=answer, color='danger')"""

# Afficher contenu de la page.
app.layout = page_1()