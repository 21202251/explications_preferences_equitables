import numpy as np
import numpy.typing as npt

from itertools import permutations

from Algorithmes_centraux.outils_programmation_lineaire import * 
from Algorithmes_centraux.programmation_lineaire import *

from Algorithmes_centraux.schemas_ATX import *
from Algorithmes_centraux.heuristiques_lorenz_restreinte import * 
from Algorithmes_centraux.heuristiques_lorenz_generalisee import * 

import time
import subprocess
chemin_gurobi: str = r"C:\gurobi1202\win64\bin\gurobi_cl" # a remplacer en fonction de l'ordinateur / os

# ALGORITHMES OWA #

def dominance_OWA_robuste(n: int, vb: npt.NDArray, va: npt.NDArray, 
                  m: int, aj: npt.NDArray, bj: npt.NDArray, 
                  verbose: bool = False)-> bool:
    '''
    Retourne True si va domine vb au sens de la dominance des OWA robustes redistributives,
    False sinon. 

    Parametres
    ----------
        n: nombre de dimensions / d'agents
        vb: vecteur domine
        va: vecteur dominant
        m: nombre de preferences donnees par l'utilisateur
        aj: liste des vecteurs dominants (preferences utilisateurs)
        bj: liste des vecteurs domines (preferences utilisateurs)
        verbose: affichages si vrai
    '''
    pl_dominance_OWA_robuste(n, vb, va, m, aj, bj)
    arguments: list[str] = [f"ResultFile=prog_lin/pl_dominance_owa.sol", f"prog_lin/pl_dominance_owa.lp"] 
    subprocess.run([chemin_gurobi] + arguments, stdout=subprocess.DEVNULL, check=True)
    solution, dico = pl_solutions(f"prog_lin/pl_dominance_owa.sol") 

    if verbose:
        _, mat = (lister_var("w", dico, dimensions=(n,)))
        afficher_var("w", mat, entier=False, axes=(range(n),))

    return solution >= 0


def dico_a_vecteurs_transferts(n: int, dico_transferts: dict) -> npt.NDArray:
    '''
    Retourne des vecteurs de transferts [0..+quantite (receveur)..0..-quantite(donneur)..0]
    a partir d'un dictionnaire de transferts.

    Parametres
    ----------
        n: nombre de dimensions / d'agents
        dico_transferts: dictionnaire de transferts de la forme (donneur, receveur):quantite
    '''
    res = []
    for (j, i), t in dico_transferts.items():
        if t > 0.0:
            vec = np.zeros(n)
            vec[j] -= t 
            vec[i] += t
            res.append(vec)
    return np.array(res)


def recuperer_Farkas_1(n: int,  vb: npt.NDArray, va: npt.NDArray, 
                       entier: bool, 
                       m: int, aj: npt.NDArray, bj: npt.NDArray,
                       timeout: float = 10e6, 
                       verbose: bool = False):
    '''
    Retourne les coefficients associes aux 
    (congruences, dons, transferts)
    a l'aide du certificat de Farkas (formule 4.10).
    
    Parametres
    ----------
        n: nombre de dimensions / d'agents
        vb: vecteur domine
        va: vecteur dominant
        entier: vrai si les variables sont entieres, faux si reelles
        m: nombre de preferences donnees par l'utilisateur
        aj: liste des vecteurs dominants (preferences utilisateurs)
        bj: liste des vecteurs domines (preferences utilisateurs)
        verbose: affichages si vrai
    '''
    pl_Farkas_1(n, vb, va, entier, m, aj, bj)
    arguments: list[str] = [f"ResultFile=prog_lin/pl_farkas_1.sol", f"prog_lin/pl_farkas_1.lp"] # arguments a passer
    try:
        subprocess.run([chemin_gurobi] + arguments, stdout=subprocess.DEVNULL, check=True, timeout=timeout) # executer commande gurobi sans affichage
    except subprocess.TimeoutExpired:
        return None # a changer pour differencier
    _, dico = pl_solutions(f"prog_lin/pl_farkas_1.sol")
    if not dico:
        return None 
    
    _, lambdas = (lister_var("lambda", dico, dimensions=(m,)))     
    _, dons = (lister_var("u", dico, dimensions=(n, )))
    
    dico_transferts, mat_t = (lister_var("tau", dico, dimensions=(n,n)))
    transferts = dico_a_vecteurs_transferts(n, dico_transferts)

    if verbose:
        afficher_var("lambda", lambdas, entier, axes=(range(m),))
        afficher_var("u", dons, entier, axes=(range(n),))
        afficher_var("tau", mat_t, entier, axes=(range(n),range(n)))

    return lambdas, dons, transferts


def recuperer_Farkas_2(n: int, vb: npt.NDArray, va: npt.NDArray, 
                       entier: bool,
                       m: int, aj: npt.NDArray, bj: npt.NDArray, 
                       timeout: float = 10e6,
                       verbose: bool = False)-> tuple:
    '''
    Retourne les coefficients associes aux 
    (congruences, dons, transferts (recepteur), transferts (donneur))
    a l'aide du certificat de Farkas (formule 4.9).

    Parametres
    ----------
        n: nombre de dimensions / d'agents
        vb: vecteur domine
        va: vecteur dominant
        entier: vrai si les variables sont entieres, faux si reelles
        m: nombre de preferences donnees par l'utilisateur
        aj: liste des vecteurs dominants (preferences utilisateurs)
        bj: liste des vecteurs domines (preferences utilisateurs)
        verbose: affichages si vrai
    '''
    pl_Farkas_2(n, vb, va, entier, m, aj, bj)
    arguments: list[str] = [f"ResultFile=prog_lin/pl_farkas_2.sol", f"prog_lin/pl_farkas_2.lp"] # arguments a passer
    try:
        subprocess.run([chemin_gurobi] + arguments, stdout=subprocess.DEVNULL, check=True, timeout=timeout) # executer commande gurobi sans affichage
    except subprocess.TimeoutExpired:
        return None 
    _, dico = pl_solutions(f"prog_lin/pl_farkas_2.sol")
    if not dico:
        return None

    _, lambdas = lister_var("lambda", dico, dimensions=(m,))     
    _, dons = lister_var("u", dico, dimensions=(n, ))
    _, vp = lister_var("vp", dico, dimensions=(n,))
    _, vn = lister_var("vn", dico, dimensions=(n,))

    if verbose:
        afficher_var("lambda", lambdas, entier, axes=(range(m),))
        afficher_var("u", dons, entier, axes=(range(n),))
        afficher_var("vp", vp, entier, axes=(range(n),))
        afficher_var("vn", vn, entier, axes=(range(n),))

    return lambdas, dons, vp, vn


def recuperer_Farkas_optimal(n: int, vb: npt.NDArray, va: npt.NDArray, 
                             entier: bool,
                             m: int, aj: npt.NDArray, bj: npt.NDArray,  
                             timeout: float = 10e6,
                             verbose: bool = False):
    '''
    Retourne les coefficients associes aux 
    (congruences, dons, transferts)
    a l'aide du certificat de Farkas optimal (4.5).
    
    Parametres
    ----------
        n: nombre de dimensions / d'agents
        vb: vecteur domine
        va: vecteur dominant
        entier: vrai si les variables sont entieres, faux si reelles
        m: nombre de preferences donnees par l'utilisateur
        aj: liste des vecteurs dominants (preferences utilisateurs)
        bj: liste des vecteurs domines (preferences utilisateurs)
        verbose: affichages si vrai
    '''
    pl_Farkas_optimal(n, vb, va, entier, m, aj, bj)
    arguments: list[str] = [f"ResultFile=prog_lin/pl_farkas_opt.sol", f"prog_lin/pl_farkas_opt.lp"] # arguments a passer

    try:
        subprocess.run([chemin_gurobi] + arguments, stdout=subprocess.DEVNULL, check=True, timeout=timeout) # executer commande gurobi sans affichage
    except subprocess.TimeoutExpired:
        return None 
    
    _, dico = pl_solutions(f"prog_lin/pl_farkas_opt.sol")

    if not dico:
        return None 
    
    _, lambdas = (lister_var("lambda", dico, dimensions=(m,)))     
    _, dons = (lister_var("u", dico, dimensions=(n, )))
    
    dico_transferts, mat_t = (lister_var("tau", dico, dimensions=(n,n)))
    transferts = dico_a_vecteurs_transferts(n, dico_transferts)

    if verbose:
        afficher_var("lambda", lambdas, entier, axes=(range(m),))
        afficher_var("u", dons, entier, axes=(range(n),))
        afficher_var("tau", mat_t, entier, axes=(range(n),range(n)))

    return lambdas, dons, transferts


def recuperer_Farkas_avec_transferts(farkas: str, 
                                     n: int, vb: npt.NDArray, va: npt.NDArray, 
                                     entier: bool,
                                     m: int, aj: npt.NDArray, bj: npt.NDArray,  
                                     timeout: float = 10e6,
                                     verbose: bool = False):
    '''
    Retourne les coefficients associes aux 
    (congruences, dons, transferts)
    a l'aide du certificat de Farkas 1 ou optimal.
    
    Parametres
    ----------
        farkas: nom du certificat ("1" ou "optimal")
        n: nombre de dimensions / d'agents
        vb: vecteur domine
        va: vecteur dominant
        entier: vrai si les variables sont entieres, faux si reelles
        m: nombre de preferences donnees par l'utilisateur
        aj: liste des vecteurs dominants (preferences utilisateurs)
        bj: liste des vecteurs domines (preferences utilisateurs)
        verbose: affichages si vrai
    '''
    assert farkas in {"1", "optimal"}, "Nom de certificat de Farkas invalide."
    if farkas == "1":
        return recuperer_Farkas_1(n, vb, va, entier, m, aj, bj, timeout, verbose)
    elif farkas == "optimal":
        return recuperer_Farkas_optimal(n, vb, va, entier, m, aj, bj, timeout, verbose)


def algorithme_permutation(vb: npt.NDArray, va: npt.NDArray, 
                           lambdas: npt.NDArray, dons: npt.NDArray, transferts: npt.NDArray, 
                           compromis: npt.NDArray, 
                           l: float = 0, U: float = 100,
                           timeout: float = 10e6)-> list:
    '''
    Avec les donnees obtenues par le certificat de Farkas 
    concernant les dons, les transferts et les congruences,
    retourne si elle existe une explication
    grace a une permutation de ces operations.

    Permutations (Algorithme 13, page 214).

    Parametres
    ----------
        vb: vecteur domine
        va: vecteur dominant
        lambdas: liste des coefficients de la I-congruence
        dons: liste des dons
        transferts: liste des transferts redistributifs de la forme [0..+quantite (receveur)..0..-quantite(donneur)..0]
        compromis: ensemble des compromis dans I
        l: borne inferieure du domaine
        U: borne superieure du domaine
        timeout:
    '''
    debut: float = time.time()

    nb_transferts: int = len(transferts)
    m: int = len(lambdas)
    nb_possibilites = 1 + nb_transferts + m

    ti = [None] * nb_possibilites

    # Construction des operations possibles (dons, transferts, congruences)
    for i in range(nb_possibilites):
        if i == 0:
            ti[i] = dons
        elif i <= nb_transferts:
            ti[i] = transferts[i-1]
        else:
            indice = i - (1 + nb_transferts)
            ti[i] = lambdas[indice] * compromis[indice]

    ti = np.array(ti, dtype=object)

    # Test de toutes les permutations
    for sigma in permutations(range(nb_possibilites)):
        if time.time() - debut > timeout:
            break
        y = np.copy(vb)
        p = [y]
        valide = True
        for i in sigma:
            nouveau_y = y + ti[i]
            # Verification que nouveau_y appartient a X^n
            if not ((np.all(nouveau_y >= l) and np.all(nouveau_y <= U)) and np.all(nouveau_y[:-1] <= nouveau_y[1:])):
                valide = False
                break
            p.append(nouveau_y.copy())
            y = nouveau_y

        if valide and np.array_equal(y, va) :
            return p

    return None


def farkas_et_Permutation(farkas: str, 
                          n: int, vb: npt.NDArray, va: npt.NDArray,
                          entier: bool,
                          m: int, aj: npt.NDArray, bj: npt.NDArray, 
                          l: float, U: float, 
                          timeout: float = 10e6,
                          verbose: bool = False):
    ''' 
    Recupere un certificat de Farkas avec transferts puis applique l'algorithme de permutation.

    Parametres
    ----------
        farkas: nom du certificat ("1" ou "optimal")
        n: nombre de dimensions / d'agents
        vb: vecteur domine
        va: vecteur dominant
        entier: vrai si les variables sont entieres, faux si reelles
        m: nombre de preferences donnees par l'utilisateur
        aj: liste des vecteurs dominants (preferences utilisateurs)
        bj: liste des vecteurs domines (preferences utilisateurs)
        l: borne inferieure du domaine
        U: borne superieure du domaine
        timeout:
        verbose: affichages si vrai
    '''
    debut: float = time.time()
    res = recuperer_Farkas_avec_transferts(farkas, n, vb, va, entier, m, aj, bj, verbose)
    if res is None:
        return None
    lambdas, dons, transferts = res
    compromis = np.array([aj[i] - bj[i] for i in range(len(aj))])
    timeout_restant = max(0.0, timeout - (time.time() - debut))
    return algorithme_permutation(vb, va, lambdas, dons, transferts, compromis, l, U, timeout=timeout_restant)


def rff(n: int, vb: npt.NDArray, va: npt.NDArray, 
        entier: bool,
        m: int, lambdas: npt.NDArray, aj: npt.NDArray, bj: npt.NDArray, 
        timeout: float = 10e6,
        verbose: bool = False):
    '''
    Avec les donnees obtenues par le certificat de Farkas 
    concernant les congruences,
    retourne si elle existe une explication
    alternant des blocs de dominance de Lorenz avec des congruences.

    Parametres
    ----------
        n: nombre de dimensions / d'agents
        vb: vecteur domine
        va: vecteur dominant 
        entier: vrai si les variables sont entieres, faux si reelles
        m: nombre de preferences donnees par l'utilisateur
        lambdas: liste des coefficients de la I-congruence
        aj: liste des vecteurs dominants (preferences utilisateurs)
        bj: liste des vecteurs domines (preferences utilisateurs)
        timeout:
        verbose: affichages si vrai
    '''
    pl_pi_Lorenz(n, vb, va, entier, m, lambdas, aj, bj)
    arguments: list[str] = [f"ResultFile=prog_lin/pl_pi_lorenz.sol", f"prog_lin/pl_pi_lorenz.lp"] # arguments a passer
    try:
        subprocess.run([chemin_gurobi] + arguments, stdout=subprocess.DEVNULL, check=True) # executer commande gurobi sans affichage    
    except subprocess.TimeoutExpired:
        return None
    _, dico = pl_solutions(f"prog_lin/pl_pi_lorenz.sol")
    if not dico:
        return None 

    l: int = 2*m + 2 # nombre d'etapes
    K1 = [k for k in range(0, l-1, 2)] # dons ou transferts
    K0 = [k for k in range(1, l-2, 2)] # congruences

    _, matx = lister_var("x", dico, dimensions=(l, n))

    if verbose:
        afficher_var("x", matx, entier, axes=(range(l), range(n)))

        _, matvp = lister_var("vp", dico, ensembles=(K1, range(n)))
        _, matvn = lister_var("vn", dico, ensembles=(K1, range(n)))
        _, matu = lister_var("u", dico, ensembles=(K1, range(n)))
        _, matbeta = lister_var("beta", dico, ensembles=(K1,))
        _, matalpha = lister_var("alpha", dico, ensembles=(K0, range(m)))

        afficher_var("vp", matvp, entier ,axes=(K1, range(n)))
        afficher_var("vn", matvn, entier, axes=(K1, range(n)))
        afficher_var("u", matu, entier, axes=(K1, range(n)))
        afficher_var("beta", matbeta, entier, axes=(K1,))
        afficher_var("alpha", matalpha, entier=False, axes=(K0, range(m)))
    
    explication = []
    for i in range(l-1):
        if i % 2 == 0:
            y = np.array(matx[i])
            x = np.array(matx[i+1])
            explication += ATX(y, x, glouton_fute, don_final=True)
    
    return explication


def farkas_et_RFF(n: int, vb: npt.NDArray, va: npt.NDArray, 
                  entier: bool,
                  m: int, aj: npt.NDArray, bj: npt.NDArray, 
                  timeout: float = 10e6,
                  verbose: bool = False):
    '''
    Recupere le certificat de Farkas 1 puis applique RFF.

    Parametres
    ----------
        n: nombre de dimensions / d'agents
        vb: vecteur domine
        va: vecteur dominant 
        entier: vrai si les variables sont entieres, faux si reelles
        m: nombre de preferences donnees par l'utilisateur
        aj: liste des vecteurs dominants (preferences utilisateurs)
        bj: liste des vecteurs domines (preferences utilisateurs)
        verbose: affichages si vrai
    '''
    debut: float = time.time()
    res = recuperer_Farkas_1(n, vb, va, entier, m, aj, bj, verbose)
    if res is None:
        return None
    lambdas, _, _ = res
    timeout_restant = max(0.0, timeout - (time.time() - debut))
    return rff(n, vb, va, entier, m, lambdas, aj, bj, timeout= timeout_restant, verbose=verbose)

    
def atx_Optimal(n: int, vb: npt.NDArray, va: npt.NDArray, 
                entier: bool,
                m: int, aj: npt.NDArray, bj: npt.NDArray, 
                timeout: float)-> list:
    ''' 
    Retourne l'explication ATX (transferts, dons, congruences) de taille optimale
    si elle existe, None sinon.

    Parametres
    ----------
        n: nombre de dimensions / d'agents
        vb: vecteur domine
        va: vecteur dominant 
        entier: vrai si les variables sont entieres, faux si reelles
        m: nombre de preferences donnees par l'utilisateur
        aj: liste des vecteurs dominants (preferences utilisateurs)
        bj: liste des vecteurs domines (preferences utilisateurs)
        timeout:
    '''
    def tester(l: int)-> tuple:
        ''' 
        Teste une valeur de l et retourne 
        (la solution si elle existe, False si le timeout n'a pas encore ete atteint)

        Parametres
        ----------
            l: nombre d'etapes 
        '''
        if time.time() - debut > timeout:
            return None, True

        explication = recuperer_PL_ATX(l, n, vb, va, 
                                       sat=True, dominance="owa", entier=entier,
                                       m=m, aj=aj, bj=bj,
                                       timeout=10e6,
                                       verbose=False)

        return explication, False
    
    debut: float = time.time()
    l: int = max(1, n // 2)

    resultat, fini = tester(l)

    if fini:
        return None

    # n/2 fonctionne : on cherche vers le bas
    if resultat is not None:
        sup, inf = l,  max(1, l // 2)

        while inf > 0:
            resultat, fini = tester(inf)
            if fini:
                return None
            if resultat is not None:
                sup = inf
                if inf == 1:
                    return resultat
                inf //= 2
            else:
                break

    # n/2 ne fonctionne pas : on cherche vers le haut
    else:
        inf, sup = l, 2*l
        while True:
            resultat, fini = tester(sup)
            if fini:
                return None
            if resultat is not None:
                break
            inf = sup
            sup *= 2

    # Dichotomie
    while inf + 1 < sup:
        milieu = (inf + sup) // 2
        resultat, fini = tester(milieu)
        if fini:
            return None
        if resultat is not None:
            sup = milieu
        else:
            inf = milieu

    if fini:
        return None

    return resultat

# Calcul des nouveaux vecteurs pour la congruence (CTX)

def calcul_deltas(n: int, lambdas: npt.NDArray, dons: npt.NDArray, transferts: npt.NDArray, 
                  compromis: npt.NDArray)-> tuple:
    """
    Calcule et retourne delta+ et delta- depuis un certificat de Farkas.

    Parametres
    ----------
        n: nombre de dimensions / d'agents
        lambdas: liste des coefficients de la I-congruence
        dons: liste des dons
        transferts: liste des transferts redistributifs de la forme [0..+quantite (receveur)..0..-quantite(donneur)..0]
        compromis: liste des compromis de I
    """
    delta_plus = [0.0 for _ in range(n)]
    delta_minus = [0.0 for _ in range(n)]

    # Contributions des arguments I
    for j in range(len(lambdas)):
        if lambdas[j] == 0:
            continue
        v = compromis[j]   # vecteur a_j - b_j

        for i in range(n):
            contribution = lambdas[j] * v[i]
            if contribution >= 0:
                delta_plus[i] += contribution
            else:
                delta_minus[i] += contribution

    # Contributions des dons
    for i in range(n):
        if dons[i] != 0:
            delta_plus[i] += dons[i]

    # Contributions des transferts
    for transfert in transferts:
        for i in range(n):
            x = transfert[i]
            if x > 0:
                delta_plus[i] += x 
            elif x < 0: 
                delta_minus[i] += x 

    return delta_plus, delta_minus


def choix_s(valeur_max: float, dernier_delta: float, l: float, U: float)-> float:
    '''
    Retourne le coefficient s de mise a l'echelle pour l'explication CTX. 

    Parametres
    ----------
        valeur_max: max(vb', va')
        dernier_delta: delta_plus[-1]
        l: borne inferieure du domaine
        U: borne superieure du domaine
    '''
    s: float = (U-l)/(valeur_max + dernier_delta)
    return min(1.0, s)


def deplacement_non_borne(delta_plus: npt.NDArray, delta_minus: npt.NDArray)-> tuple[npt.NDArray, npt.NDArray]:
    ''' 
    Retourne (vb', va') obtenu avec la methode du deplacement 
    dans le cas non borne (R+).

    Parametres
    ----------
        delta_plus: somme des valeurs positives par agent
        delta_moins: somme des valeurs negatives par agent
    '''
    n: int = len(delta_plus)

    va_prime = [0.0] * n
    vb_prime = [0.0] * n

    ancien_vb = 0.0
    ancien_delta_plus = 0.0

    for i in range(n):
        vb_prime[i] = (ancien_vb + ancien_delta_plus - delta_minus[i])
        va_prime[i] = (ancien_vb + delta_plus[i] + ancien_delta_plus)

        # MAJ pour l'agent suivant
        ancien_vb = vb_prime[i]
        ancien_delta_plus = delta_plus[i]

    return vb_prime, va_prime


def deplacement_borne(delta_plus: npt.NDArray, delta_minus: npt.NDArray, 
                      l: float, U: float)-> tuple[npt.NDArray, npt.NDArray, float]:
    ''' 
    Retourne (vb', va', s) obtenu avec la methode du deplacement 
    dans le cas borne (l, U).

    Parametres
    ----------
        delta_plus: somme des valeurs positives par agent
        delta_moins: somme des valeurs negatives par agent
        l: borne inferieure du domaine
        U: borne superieure du domaine
    '''
    n: int = len(delta_plus)

    vb_prime_0, va_prime_0 = deplacement_non_borne(delta_plus, delta_minus)
    valeur_max = max(vb_prime_0[-1], va_prime_0[-1])
    s = choix_s(valeur_max, delta_plus[-1], l, U)

    # Nouveaux points de depart
    va_prime = [0.0] * n
    vb_prime = [0.0] * n

    # Initialisation
    ancien_vb = l
    ancien_delta_plus = 0.0

    # Construction de a_prime et b_prime selon les formules 
    for i in range(n):

        vb_prime[i] = (ancien_vb + s * (ancien_delta_plus - delta_minus[i]))
        va_prime[i] = (ancien_vb + s * (delta_plus[i] + ancien_delta_plus))

        ancien_vb = vb_prime[i]
        ancien_delta_plus = delta_plus[i]

    return vb_prime, va_prime, s


def agrandissement_non_borne(vb: npt.NDArray, va: npt.NDArray, 
                             delta_plus: npt.NDArray, delta_minus: npt.NDArray)-> tuple[npt.NDArray, npt.NDArray]:
    '''
    Retourne (vb', va') obtenu avec la methode de l'agrandissement 
    dans le cas non borne (R+).

    Parametres
    ----------
        vb: vecteur domine
        va: vecteur dominant
        delta_plus: somme des valeurs positives par agent
        delta_moins: somme des valeurs negatives par agent
    '''
    n: int = len(va)

    va_prime = [0.0] * n
    vb_prime = [0.0] * n

    marge = 0.0
    ancien_delta_plus = 0.0

    for i in range(n):

        # ajout de la marge necessaire
        marge += (ancien_delta_plus - delta_minus[i])

        
        va_prime[i] = va[i] + marge
        vb_prime[i] = vb[i] + marge


        ancien_delta_plus = delta_plus[i]

    return vb_prime, va_prime


def agrandissement_borne(vb: npt.NDArray, va: npt.NDArray, 
                         delta_plus: npt.NDArray, delta_minus: npt.NDArray, 
                         l: float, U: float)-> tuple[npt.NDArray, npt.NDArray, float]:
    '''
    Retourne (vb', va', s) obtenu avec la methode de l'agrandissement 
    dans le cas borne (l,U).

    Parametres
    ----------
        vb: vecteur domine
        va: vecteur dominant
        delta_plus: somme des valeurs positives par agent
        delta_moins: somme des valeurs negatives par agent
    '''
    vb_prime_0, va_prime_0 = agrandissement_non_borne(delta_plus, delta_minus)
    valeur_max: float = max(vb_prime_0[-1], va_prime_0[-1])
    s = choix_s(valeur_max, delta_plus[-1], l, U)

    n: int = len(va)

    va_prime = [0.0] * n
    vb_prime = [0.0] * n

    marge = 0.0
    ancien_delta_plus = 0.0

    for i in range(n):

        # ajout de la marge necessaire
        marge += (ancien_delta_plus - delta_minus[i])

        va_prime[i] = (s * (va[i] + marge) + l)
        vb_prime[i] = (s * (vb[i] + marge) + l)

        ancien_delta_plus = delta_plus[i]

    return vb_prime, va_prime, s


def ctx(n: int, vb: npt.NDArray, va: npt.NDArray, 
        lambdas: npt.NDArray, dons: npt.NDArray, transferts: npt.NDArray, aj: npt.NDArray, bj: npt.NDArray,  
        l: float = None, U: float = None,
        timeout: float = 10e6)-> list:
    '''
    Avec les donnees obtenues par le certificat de Farkas 
    concernant les dons, les transferts et les congruences,
    retourne si elle existe une explication CTX.

    Parametres
    ----------
        n: nombre de dimensions / d'agents
        vb: vecteur domine
        va: vecteur dominant
        lambdas: liste des coefficients de la I-congruence
        dons: liste des dons
        transferts: liste des transferts redistributifs de la forme [0..+quantite (receveur)..0..-quantite(donneur)..0]
        aj: liste des vecteurs dominants (preferences utilisateurs)
        bj: liste des vecteurs domines (preferences utilisateurs)
        l: borne inferieure du domaine
        U: borne superieure du domaine
        timeout:
    '''
    # Calcul des deltas
    compromis = np.array([aj[i] - bj[i] for i in range(len(aj))])
    delta_plus, delta_moins = calcul_deltas(n, lambdas, dons, transferts, compromis)

    if U is None:
        # Domaine non borne
        b_prime, a_prime = deplacement_non_borne(delta_plus, delta_moins)
        liste = algorithme_permutation(b_prime, a_prime, lambdas, dons, transferts, compromis, l, U, timeout)
        if liste:
            return [vb] + liste + [va]

    else:
        # Domaine borne
        b_prime, a_prime, s = deplacement_borne(delta_plus, delta_moins, l, U)
        dons_reduits = np.array(dons) * s 
        transferts_reduits = np.array(transferts) * s 
        lambdas_reduits = np.array(lambdas) * s 
        liste = algorithme_permutation(b_prime, a_prime, lambdas_reduits, dons_reduits, transferts_reduits, compromis, l, U, timeout)
        if liste:
            return [vb] + liste + [va]
    return


def farkas_et_CTX(farkas: str, n: int, vb: npt.NDArray, va: npt.NDArray, 
                  entier: bool,
                  m: int, aj: npt.NDArray, bj: npt.NDArray, 
                  l: float = None, U: float = None, 
                  timeout: float = 10e6,
                  verbose: bool = False):
    ''' 
    Recupere un certificat de Farkas avec transferts puis applique ctx.

    Parametres
    ----------
        farkas: nom du certificat ("1" ou "optimal")         
        n: nombre de dimensions / d'agents
        vb: vecteur domine
        va: vecteur dominant
        entier: vrai si les variables sont entieres, faux si reelles
        m: nombre de preferences donnees par l'utilisateur
        aj: liste des vecteurs dominants (preferences utilisateurs)
        bj: liste des vecteurs domines (preferences utilisateurs)
        l: borne inferieure du domaine
        U: borne superieure du domaine
        timeout:
        verbose: affichages si vrai
    '''
    # certificat Farkas
    debut: float = time.time()
    res_PL = recuperer_Farkas_avec_transferts(farkas, n, vb, va, entier, m, aj, bj, timeout, verbose)
    if res_PL:
        lambdas, dons, transferts = res_PL
        timeout_restant = max(0.0, timeout - (time.time() - debut))
    else:
        return None

    return ctx(n, vb, va, lambdas, dons, transferts, aj, bj, l, U, timeout_restant)
