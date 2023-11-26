import pandas as pd
import plotly.express as px

def get_us_map_data_frame(csv_file='states.csv'):
    """Charge un fichier csv contenant les états des États-Unis et leurs abréviations.
    Ajoute les deux colonnes pour le map quizz. Retourne le DataFrame."""
    df = pd.read_csv(csv_file)
    df['Answer'] = '?'
    df['Color'] = 0
    return df

def try_user_answer(df, user_answer=str):
    """Teste la réponse de l'utilsateur dans le DataFrame, change la couleur si la réponse est trouvée.
    Retourne le DataFrame."""
    if user_answer is None:
        user_answer = ''
    series_answer_lower = df['State'].apply(lambda x: x.lower() if x is not None else x)
    df['Answer'][series_answer_lower == user_answer.lower()] = user_answer.title()
    df['Color'] = df[['State', 'Answer']].apply(lambda x: 1 if x[0].lower() == x[1].lower() else 0, axis=1)
    if user_answer.lower() in series_answer_lower.values:
        color_answer = 'lightgreen'
    else:
        color_answer = 'red'
    return df, color_answer

def plot_map(df):
    """Affiche le DataFrame. 
    Requiert les colonnes 'State Code' (les abréviations des états), 'Answer' pour les noms de pays trouvés et 'Color'."""
    nb_states_found = sum(df['Color'])
    fig = px.choropleth(
        title=f'States found : {nb_states_found} on {len(df)}.',
        data_frame=df,
        locations='State Code',
        locationmode="USA-states", 
        scope="usa",
        color='Color',
    )
    fig.update_coloraxes(showscale=False)
    fig.update_traces(hovertemplate=df['Answer'])
    return fig