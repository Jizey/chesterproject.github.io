import bs4 as bs
import urllib.request
import pandas as pd

import math
import requests
from PIL import Image
from io import BytesIO
from dash import html

url_wiki_search = 'https://en.wikipedia.org/w/index.php?limit=500&offset=0&profile=default&search=list+presidents&title=Special:Search&ns0=1'
with_color = ['\033[92m', '\033[93m', '\033[91m', '\033[0m']
no_color = ['', '', '', '']
green, yellow, red, normal = no_color


# TABLES PART
def make_soup(url=str):
    """À partir de l'url d'une page, en extrait le contenu html"""
    source = urllib.request.urlopen(url).read()
    soup = bs.BeautifulSoup(source, features="lxml")
    return soup

def find_urls_for_tests(url_wiki_search=str):
    """À partir de l'url d'une recherche wikipedia des pages sur les listes des présidents de divers pays,
    récupère une liste d'url à tester pour nos fonctions de scrapping"""
    soup = make_soup(url_wiki_search)
    list_urls = ['https://en.wikipedia.org'+a['href'] for a in soup.find_all('a', href=True) if 'presidents' in a['href'].lower() and a['href'].startswith('/wiki/List')]
    # Quelques mots-clés pour éviter des pages qui ne parlent pas de présidents tel que nous l'entendons.
    keywords_filter = ['by', 'senate', 'chile', 'piedmont', 'marseille', 'legislature', 'sporting', 'fictional'] # Pour Chile il s'agit d'un problème de scrapping
    for url in list_urls:
        for keyword in keywords_filter:
            if keyword in url.lower():
                list_urls.remove(url)

    return list(set(list_urls)) #Supprime les doublons

def find_tables(soup):
    """"Récupère la liste des tables afin de créer une liste de DataFrames"""
    tables = soup.findAll("table")
    dfs = pd.read_html(str(tables), header=0)
    return dfs

def kept_df_with_name_column(dfs=list):
    """D'une liste de DataFrames, ne conserve que ceux contenant la colonne 'name', et les fusionnent en un unique DataFrame"""
    # Mettre dfs_kept sous forme de fonction(name_or_president_column=str)
    name_or_president_column = 'name'
    dfs_kept = [single_df for single_df in dfs if len([col for col in list(single_df.columns) if type(col) != tuple and name_or_president_column in str(col).lower() and str(col).lower().startswith(name_or_president_column)]) > 0]
    # Si ne trouve pas de colonne avec 'name', essaye avec 'president'
    if len(dfs_kept) < 1:
        name_or_president_column = 'president'
        dfs_kept = [single_df for single_df in dfs if len([col for col in list(single_df.columns) if type(col) != tuple and name_or_president_column in str(col).lower() and str(col).lower().startswith(name_or_president_column)]) > 0]
    if len(dfs_kept) > 1:
        df = pd.concat(dfs_kept, ignore_index=True)
    else:
        df = dfs_kept[0]
    return df, name_or_president_column

def keep_int_first_column(df, name_or_president_column):
    """La première colonne du DataFrame est censé contenir des numéros.
    On met de côté le cas où il s'agit d'un tiret (Gouvernements provisoires, intérimaires, etc.) <= Étape devenue inutile ?
    Puis on s'assure de ne conserver que les int"""
    # Ne garder que les lignes dont le N° est autre qu'un tiret
    df = df.loc[df[df.columns[0]] != '-'].reset_index(drop=True)
    # Éliminer les N° qui ne sont pas des int
    if df.columns[0].lower() != name_or_president_column:
        df = df.loc[pd.to_numeric(df[df.columns[0]], errors='coerce').notna()].reset_index(drop=True)
        df = df.astype({df.columns[0]: int})
    return df

def get_and_clean_name_column(df, name_or_president_column):
    """Cherche l'intutilé de la colonne des noms et les renvoie afin de générer les questions ultérieurement."""
    try:
        # Trouver avec certitude la colonne des noms
        name_column_list = sorted([col for col in df.columns if name_or_president_column in col.lower()])
        name_column = [name_column for name_column in name_column_list if name_column.lower().startswith(name_or_president_column)][0]
        # Fonction pour retirer les liens dans la colonne des noms
        df[name_column] = df.apply(lambda x: x[name_column].split(' [')[0].split('[')[0], axis=1)
    except (IndexError):
        print('Colonne Name introuvable')
        name_column = None
    return df, name_column

def wiki_scrap(url=str):
    """À partir de l'url wikipedia des présidents des États-Unis, récupère un tableau et nettoie la colonne des noms.
    Renvoie le tableau sous forme de dataframe pandas et l'intitulé de la colonne des noms"""
    soup = make_soup(url)
    dfs = find_tables(soup)
    df, name_or_president_column = kept_df_with_name_column(dfs)
    df = keep_int_first_column(df, name_or_president_column)
    df, name_column = get_and_clean_name_column(df, name_or_president_column)
    return df, name_column


# IMAGE PART
def get_img_urls(img_search_url=str):
    """D'une url de recherche d'images comme gettyimages.fr, récupère les urls des résultats."""
    source = urllib.request.urlopen(img_search_url).read()
    soup = bs.BeautifulSoup(source, features="xml")
    links = [img_tag.get('src') for img_tag in soup.find_all('img') if img_tag.get('src') != None and img_tag.get('src').startswith('http')]
    return links

def get_img_from_url(img_url=str):
    """De l'url d'une image, ressort l'image sous format PIL.image"""
    response = requests.get(img_url)
    img = Image.open(BytesIO(response.content))
    return img

def resize_img(img, width_coef=100):
    """D'une image par exemple ouverte avec PIL, lui offre de nouvelles dimensions avec une hauteur de 100 pixels
    et calcule la largeur en fonction. Renvoie l'image redimensionnée."""
    coef_reduc = width_coef / img.size[1]
    new_size = (math.ceil(img.size[0]*coef_reduc), math.ceil(img.size[1]*coef_reduc))
    img_resized = img.resize(new_size)
    if img_resized.size[0] > img_resized.size[1]:
        width_img = img_resized.size[0]
        list_crop_left_right = [math.ceil((width_img - width_coef) / 2), width_img - math.floor((width_img - width_coef) / 2)]
        img_resized = img_resized.crop((list_crop_left_right[0], 0, list_crop_left_right[1], img_resized.size[1]))
    return img_resized

def get_first_image_from_name(name, active=False):
    """Créé une url à partir d'un nom et recherche une image correspondant.
    Renvoie une image PIL redimensionnée."""
    if active == True:
        split_name = '-'.join(name.split(' ')).lower()
        img_search_url = f'https://www.gettyimages.fr/photos/{split_name}?assettype=image'
        try:
            links = get_img_urls(img_search_url=img_search_url)
            img_url = links[0]
            img = get_img_from_url(img_url=img_url)
            img_resized = resize_img(img=img)
        except:
            print(f'Image not found for {name}')
            img_resized = 'Image not found.'
            return img_resized
    else:
        img_resized = ''
        return img_resized
    return html.Img(src=img_resized)