import random
import time
from functions.scrapping_functions import green, yellow, red, normal

def find_row(df, nb_row):
    """À patir du numéro de question, trouver la ligne correspondante dans le dataframe
    Renvoie la ligne en question"""
    row = df.iloc[nb_row]
    return row

def find_str_nb_president(nb_president=int):
    """Fonction pour trouver les caractères à rajouter pour un énième président
    Renvoie une string pour écrire 1er, 2nd, etc."""
    if nb_president > 2:
        str_nb_president = 'ème'
    elif nb_president > 1:
        str_nb_president = 'nd'
    else:
        str_nb_president = 'er'
    return str_nb_president

def random_nb_answer_possibilites(df, nb_president, nb_possibilities=2):
    """Trouve d'autres numéros de président afin d'éviter les doublons"""
    i=0
    nb_answer_possibilities = []
    # À chaque boucle, on vérifie que le numéro de président n'est pas dans la liste, puis on a ajoute un numéro
    while len(nb_answer_possibilities) < nb_possibilities-1: # -1 car on ajoute bonne réponse plus tard
        rand_nb = random.randrange(len(df))
        if rand_nb not in nb_answer_possibilities:
            nb_answer_possibilities.append(rand_nb)
            # Simple sécurité pour éviter les boucles infinies
            i += 1
        nb_answer_possibilities = list(filter(lambda nb: nb != nb_president, nb_answer_possibilities))
        if i > 1000:
            break
    return nb_answer_possibilities

def generate_possibilities(df, name_column, nb_possibilities):
    """À partir du dataframe récupéré, génère une question aléatoire type 'Qui était le président n°?'
    avec nb_possibilities comme nombre d'autres possibilités proposées"""
    # Génère un numéro de question aléatoire
    nb_question = random.randrange(len(df))

    # Par rapport au numéro de question, trouve le président à la ligne correspondante
    row_question = find_row(df, nb_question)
    nb_president = row_question[0]
    # Dans le cas où il n'y a pas de colonne 'N°', la première colonne sera sûrement celle des noms
    # Dans ce cas, on se base sur l'index
    if type(nb_president) == str or df.columns[0].lower().startswith('year'):
        nb_president = nb_question+1
    answer = row_question[name_column]

    # Trouve d'autres réponses possibles à présenter
    nb_answer_possibilities = random_nb_answer_possibilites(df, nb_president, nb_possibilities)
    answer_possibilities = [find_row(df, nb)[name_column] for nb in nb_answer_possibilities]

    # Réunit la réponse et les possiblités dans une string
    # set() supprime les doublons et range dans l'ordre afin de ne pas déterminer l'emplacement de la bonne réponse
    all_answers = list(set(answer_possibilities+[answer]))
    all_answers = [answer.split(' (')[0] for answer in all_answers]
    return nb_president, all_answers, answer

def generate_question(nb_president, country, all_answers, answer):
    """À partir du dataframe récupéré, génère une question aléatoire type 'Qui était le président n°?'
    avec nb_possibilities comme nombre d'autres possibilités proposées 
    Renvoie les strings pour la question, les possibilités et la réponse"""    
    # Ajoute "er", "nd" ou "ème" selon la réponse
    str_nb_president = find_str_nb_president(nb_president)    

    str_all_answers = ''.join([yellow+ans.split(' (')[0]+f'{normal}, ' for ans in all_answers[:-2]])+yellow+all_answers[-2].split(' (')[0]+f'{normal} ou '+yellow+all_answers[-1].split(' (')[0]+normal

    # Ainsi on a nos questions/réponses
    question = f"Qui était le {yellow}{nb_president}{str_nb_president}{normal} president {country}?"
    possibilities = f"Était-ce {str_all_answers} ?"
    return question, possibilities, answer

def show_question(score, df, name_column, country, nb_possibilities=2):
    """À partir d'une question générée, la propose, et selon la réponse mise en input, met à jour le score"""
    new_score = score
    # On génère la question
    generate_possibilities(df, name_column, nb_possibilities)
    question, possibilities, answer = generate_question(nb_president, country, all_answers, answer)

    time.sleep(1)
    # Affichage de la question
    print(question)
    print(possibilities)

    # On demande notre réponse
    my_answer = input(possibilities+'\n\n')

    # Comparaison de notre réponse avec la bonne réponse
    print(f'\n{normal}Vous avez répondu {yellow}{my_answer}{normal}.\n')
    time.sleep(1)
    if my_answer in answer.lower() and len(my_answer)>2:
        print(f'{green}Félicitations, c\'était bien {normal}{answer}{green}.')
        new_score += 1
    else:
        print(f'{red}Navré, la bonne réponse était {normal}{answer}{red}.')
        new_score -= 1
    print(f'\n{normal}Votre score était de {yellow}{score}{normal}, il est maintenant de {yellow}{new_score}{normal}.\n')
    return new_score, my_answer