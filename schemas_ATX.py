import numpy as np 
import numpy.typing as npt 

import subprocess
chemin_gurobi: str = r"C:\gurobi1202\win64\bin\gurobi_cl" # a remplacer en fonction de l'ordinateur / os

from Algorithmes_centraux.outils_programmation_lineaire import *
from Algorithmes_centraux.programmation_lineaire import *

# Explications ATX #

def ATX(vb: npt.NDArray, va: npt.NDArray, 
        heuristique, pretraitement = None, don_final: bool = False, 
        U: float = np.inf, 
        verbose: bool = False)-> list:
    '''
    Renvoie la liste des explications associees 
    pour passer du vecteur vb au vecteur va (avec va qui domine vb du pdv de la dominance de Lorenz)
    en procedant a des transferts redistributifs 
    + des dons si version generalisee de la dominance de Lorenz. 

    Version avec heuristiques.

    Parametres
    ----------
        vb: vecteur domine 
        va: vecteur dominant
        heuristique: fonction heuristique
        pretraitement: pretraitement ("ruissellement" ou "don_equitable")
        don_final: version avec don final ("gift") si vrai
        U: borne superieure d'argent pour chaque agent 
        verbose: affichages si vrai (version indices de 1 a n)
    '''

    if verbose:
        print(f"ATX({vb}, {va}) | heuristique : {heuristique.__name__} | don_final : {"oui" if don_final else "non"}")

    p: list = [vb] # liste des vecteurs d'explications
    y: npt.NDArray = vb # vecteur courant 
    indices_R: npt.NDArray = np.where(va > vb)[0] # liste des agents qui doivent etre receveurs
    indices_D: npt.NDArray = np.where(va < vb)[0] # liste des agents qui doivent etre donneurs
    k: int = 1 # compteur du nombre d'etapes

    if pretraitement is not None:
        pretraitements = ["ruissellement", "don_equitable"]
        nom_pretraitement: str = pretraitement.__name__
        assert nom_pretraitement in pretraitements, "Nom de fonction de pretraitement invalide"

        if verbose:
            print(f"\tPretraitement : {nom_pretraitement}")

        y = pretraitement(vb, va, U, verbose)
        p.append(y)  

    if verbose:
        print("|\tAvant boucle")
        print("|\t\tR =", [i + 1 for i in indices_R])
        print("|\t\tD =", [j + 1 for j in indices_D])
        print("|\t\ty =", y)
    
    while(len(indices_D) != 0):
        if verbose:
            print("|\tIteration", k)
        
        j, i, t = heuristique(y, va, indices_D, indices_R, verbose)
        
        # Creation du nouveau vecteur apres transfert redistributif
        x = np.copy(y)
        x[j] = x[j] - t
        x[i] = x[i] + t

        # Nouveau vecteur ajoute a la liste des explications
        p.append(x)

        # Retrait de certains agents a traiter s'il n'y a plus besoin de changer leurs valeurs
        if va[i] - y[i] == t:
            indices_R = np.delete(indices_R, np.where(indices_R == i)) 
        if y[j] - va[j] == t:
            indices_D = np.delete(indices_D, np.where(indices_D == j)) 

        # MAJ de y pour l'etape suivante   
        y = np.copy(x)

        if verbose:
            print("|\t\tR =", [i + 1 for i in indices_R])
            print("|\t\tD =", [j + 1 for j in indices_D])
            print("|\t\ty =", list(y))        
        
        k = k + 1
    
    # Verification du vecteur atteint
    if not don_final: 
        assert np.array_equal(y, va), "Le vecteur atteint n'est pas le vecteur dominant donne en parametres."

    # Possible ajout d'un don final (dominance de Lorenz generalisee)
    if don_final and len(indices_R) != 0:
        p.append(va)

    if verbose:
        print(f"FIN ATX({vb}, {va}) | heuristique : {heuristique.__name__} | don_final : {"oui" if don_final else "non"}")
        print("----------------------------------")

    return p 


def recuperer_PL_ATX(l: int, n: int, vb: npt.NDArray, va: npt.NDArray, 
                     sat: bool, dominance: str, entier: bool, 
                     m: int = None, aj: npt.NDArray = None, bj: npt.NDArray = None, 
                     timeout: float = 10e6,
                     verbose: bool = False)-> list:
    ''' 
    Renvoie la liste des explications associees 
    pour passer du vecteur vb au vecteur va (avec va qui domine vb du pdv de la dominance de Lorenz)
    en procedant a des transferts redistributifs 
    + des dons si version non restreinte
    + des congruences si version OWA. 

    Version avec programmation lineaire.

    Parametres
    ----------
        l: nombre d'etapes de l'explication (l+1 vecteurs)
        n: nombre de dimensions / d'agents
        vb: vecteur domine 
        va: vecteur dominant
        sat: vrai si version satisfiabilite, faux si version optimisation
        dominance: type de dominance ("restreinte", "generalisee", "owa") 
        entier: vrai si les variables sont entieres, faux si reelles
        m: nombre de preferences donnees par l'utilisateur
        aj: liste des vecteurs dominants (preferences utilisateurs)
        bj: liste des vecteurs domines (preferences utilisateurs)
        timeout: 
        verbose: affichages si vrai (version indices de 1 a n)
    '''
    if verbose:
        print(f"recuperer_PL_ATX({l}, {n}, {vb}, {va}, {sat}, {dominance}, {entier})")

    # Ecriture du PL
    pl_ATX(l, n, vb, va, sat, dominance, entier, m, aj, bj)

    # Resolution avec le solveur Gurobi
    nom1: str = "sat" if sat else "opt"
    nom2: str = dominance[:3]
    arguments: list[str] = [f"ResultFile=prog_lin/pl_atx_{nom1}_{nom2}.sol", f"prog_lin/pl_atx_{nom1}_{nom2}.lp"] # arguments a passer
    try:
        subprocess.run([chemin_gurobi] + arguments, stdout=subprocess.DEVNULL, check=True, timeout=timeout) # executer commande gurobi sans affichage
    except subprocess.TimeoutExpired:
        return None

    # Recuperation de la solution
    _, dico = pl_solutions(f"prog_lin/pl_atx_{nom1}_{nom2}.sol")
    if not dico:
        return None

    _, x = (lister_var("x", dico, dimensions=(l+1, n)))
  
    if verbose:
        afficher_var("x", x, entier, axes=(range(l+1),range(n)))
        variables = {"vp", "vn", "gammap", "gamman"}
        for var in variables:
            _, mat = lister_var(var, dico, dimensions=(l, n))
            afficher_var(var, mat, entier, axes = (range(l),range(n)))

    if verbose and dominance != "restreinte":
        _, matg = (lister_var("g", dico, dimensions=(l,)))
        _, matu = (lister_var("u", dico, dimensions=(l, n)))
        afficher_var("g", matg, entier, axes=(range(l),))
        afficher_var("u", matu, entier, axes=(range(l),range(n)))

        if dominance == "owa":
            _, matl = (lister_var("lambda", dico, dimensions=(l,m)))
            _, matpi = (lister_var("pi", dico, dimensions=(l,m)))
            afficher_var("lambda", matl, entier, axes=(range(l),range(m)))
            afficher_var("pi", matpi, entier, axes=(range(l),range(m)))

    if not sat:
        _, mats = (lister_var("s", dico, dimensions=(l,)))
        if verbose:
            afficher_var("s", mats, entier, axes=(range(l),))

        indices: npt.NDArray = np.flatnonzero(np.array(mats) == 0.0)
        indice: int = indices[0] if len(indices) > 0 else None
        if indice:
            return x[:indice+1]

    if verbose:
        print(f"FIN recuperer_PL_ATX({l}, {n}, {vb}, {va}, {sat}, {dominance}, {entier})")
        
    return x