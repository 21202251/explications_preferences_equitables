import numpy as np
import numpy.typing as npt
import random

from Algorithmes_centraux.dominances import *

# GENERATION de donnees synthetiques #

# Dominance de Lorenz restreinte

def generation_alternative_DLR(l: float, U: float, n: int, TS: float, entier: bool)-> npt.NDArray:
    ''' 
    Genere une alternative selon le processus de generation DLR.
    Les valeurs des criteres sont tirees aleatoirement dans l'intervalle [l, U].
    -> (PB : trop de zeros pour n qui grandit)

    (Algorithme 2 page 53)

    Parametres
    ----------
        l: borne inferieure du domaine
        U: borne superieure du domaine
        n: nombre de dimensions / d'agents 
        TS: somme totale 
    '''
    T: int = TS 
    a: npt.NDArray = np.zeros(n)
    
    for i in range(n):
        l_i = max(l, T -(n - (i+1))*U) # donner au moins l'argent necessaire si tous les agents suivants avaient la somme maximale
        U_i = min(U, T - (n - (i+1))*l) # retirer les sommes qui seront forcement donnees aux agents d'apres du fait de la borne inferieure
        a[i] = np.random.rand() * (U_i - l_i) + l_i if not entier else np.random.randint(l_i, U_i+1)
        T -= a[i]
    
    return np.sort(a)


def generation_ensemble_DLR(m: int, l: float, U: float, n: int, TS: float, entier: bool):
    '''
    Genere m alternatives selon le processus de generation DLR.
    Les valeurs des criteres sont tirees aleatoirement dans l'intervalle [l, U].

    Parametres
        ----------
        m: nombre d'alternatives a generer
        l: borne inferieure du domaine
        U: borne superieure du domaine
        n: nombre de dimensions / d'agents
        TS: somme totale 
    '''
    return [generation_alternative_DLR(l, U, n, TS, entier) for _ in range(m)]


def generation_ensembles_categories_DLR(categories: list, nb_ens: int, m: int, l: float, U: float, TSn: float, entier: bool):
    ''' 
    Pour chaque categorie, genere nb_ens ensembles de m alternatives.

    Parametres
    ----------
        categories: liste des categories de n
        nb_ens: nombre d'ensembles a generer
        m: nombre d'alternatives par ensemble
        l: borne inferieure du domaine
        U: borne superieure du domaine
        TSn: somme totale (liee a n)
        entier: si vrai, variables entieres, sinon variables reelles
    '''
    liste_par_cat = []
    for n in categories:
        liste_cat = []
        liste_par_cat.append(liste_cat)

        for _ in range(nb_ens):
            liste_alt = []
            liste_cat.append(liste_alt)

            for i in range(m):
                nouv_alt: npt.NDArray = generation_alternative_DLR(l, U, n, TSn*n, entier)
                liste_alt.append(nouv_alt)
    return liste_par_cat


def afficher_ensembles_categories(categories: list, liste_par_cat: list)-> None:
    ''' 
    Par categorie, affiche les ensembles d'alternatives associes. 

    Parametres
    ----------
        categories: liste des categories de n
        liste_par_cat: ensembles d'alternatives
    '''
    for i in range(len(liste_par_cat)):
        print("Categorie n =", categories[i])
        for j in range(len(liste_par_cat[i])):
            print("\tj =", j)
            for a in liste_par_cat[i][j]:
                print("\t\t",a)

# Dominance de Lorenz generalisee

def generation_alternative_DLG(l: float, U: float, n: int, S: float, entier: bool)-> npt.NDArray:
    ''' 
    Genere une alternative selon le processus de generation DLG.
    Les valeurs des criteres sont tirees aleatoirement dans l'intervalle [l, U]
    jusqu'a obtenir une alternative dont la somme des criteres respecte la
    contrainte S.

    Parametres
    ----------
        l: borne inferieure des valeurs des criteres
        U: borne superieure des valeurs des criteres
        n: nombre de criteres de l'alternative
        S: somme maximale autorisee pour les criteres
        entier: indique si les valeurs generees doivent etre entieres ou reelles
    '''
    while True:
        a = np.random.randint(l, U+1, n) if entier else np.random.rand(n)*(U-l)+l
        if np.sum(a) <= S:
            break
    return np.sort(a)


def generation_ensemble_DLG(m: int, l: float, U: float, n: int, S: float, entier: bool)-> list[npt.NDArray]:
    ''' 
    Genere une liste de m alternatives non dominees au sens de Pareto.

    Les alternatives sont generees avec le processus DLG puis ajoutees a
    l'ensemble uniquement si elles ne sont pas dominees par une alternative
    deja presente.

    Parametres
    ----------
        m: nombre d'alternatives a generer
        l: borne inferieure des valeurs des criteres
        U: borne superieure des valeurs des criteres
        n: nombre de criteres des alternatives
        S: somme maximale autorisee pour les criteres
        entier: indique si les valeurs generees doivent etre entieres ou reelles
    '''
    res = []

    while len(res) != m:
        a = generation_alternative_DLG(l, U, n, S, entier)
        valide = True
        for e in res:
            if dominance_pareto(e, a) or dominance_pareto(e, a):
                valide = False
                break
        if valide:
            res.append(a)
    return res

# Dominance des OWA robustes

def generer_w(n: int)-> npt.NDArray:
    ''' 
    Retourne un vecteur de poids omega.

    Parametres
    ----------
        n: nombre de dimensions / d'agents
    '''
    omega: npt.NDArray = np.random.dirichlet(np.ones(n))
    omega = np.sort(omega)[::-1]
    return omega


def generer_preferences(alternatives: npt.NDArray, omega: npt.NDArray, nb_preferences: int)-> list:
    '''
    Genere des informations de preference selon un vecteur de poids omega.

    Les paires selectionnees ne doivent pas etre comparables par dominance
    de Lorenz generalisee ou Lorenz restreinte. 

    Parametres
    ----------
        alternatives: ensemble des alternatives
        omega: vecteur de poids "ground truth"
        nb_preferences: nombre de preferences a generer
    '''
    preferences = []

    while len(preferences) < nb_preferences:

        a, b = random.sample(alternatives, 2)

        # Rejet si dominance Lorenz generalisee ou restreinte
        if dominance_lorenz(a, b, False) or dominance_lorenz(b, a, False):
            continue

        # Calcul de la preference selon omega
        score_a = np.dot(omega, a)
        score_b = np.dot(omega, b)

        # Pas d'indifference
        if np.isclose(score_a, score_b):
            continue

        # On garde la preference
        if score_a > score_b:
            preferences.append((b, a))
        else:
            preferences.append((a, b))

    return preferences


