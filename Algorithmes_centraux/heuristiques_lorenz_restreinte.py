import numpy as np 
import numpy.typing as npt

# HEURISTIQUES - Dominance de Lorenz restreinte #
 
def hlp(y: npt.NDArray, va: npt.NDArray, donneurs: npt.NDArray, receveurs: npt.NDArray, verbose: bool = False)-> tuple[int, int, float]:
    ''' 
    Retourne les indices j du donneur, i du receveur et la quantite de richesse transferee t.
    
    Heuristique HLP (Algorithme 1, page 42). 

    Parametres
    ----------
        y: vecteur courant 
        a: vecteur dominant
        donneurs: liste des agents qui doivent etre donneurs (taille > 0)
        receveurs: liste des agents qui doivent etre receveurs (taille > 0)
        verbose: affichage si vrai (version indices de 1 a n)
    '''
    if verbose:
        print(f"\tAppel hlp({y}, {va}, {donneurs}, {receveurs})")
        
    j: int = np.min(donneurs) # le donneur le plus pauvre
    i: int = np.max(receveurs[np.where(receveurs < j)]) # le receveur le plus riche (plus pauvre que le donneur)
    t: float = min(va[i] - y[i], y[j] - va[j])

    if verbose:
        print("|\t\tj =", j + 1, "| i =", i + 1, "| t =", t)

    return j, i, t


def glouton(y: npt.NDArray, va: npt.NDArray, donneurs: npt.NDArray, receveurs: npt.NDArray, verbose: bool = False)-> tuple[int, int, float]:
    ''' 
    Retourne les indices j du donneur, i du receveur et la quantite de richesse transferee t.
    
    Heuristique glouton (Algorithme 6 page 189): 
        Transfert de la quantite de richesse la plus grande possible a chaque etape.

    Parametres
    ----------
        y: vecteur courant 
        va: vecteur dominant
        d: liste des agents qui doivent etre donneurs (taille > 0)
        r: liste des agents qui doivent etre receveurs (taille > 0)
        verbose: affichage si vrai (version indices de 1 a n)
    '''
    if verbose:
        print(f"\tAppel glouton({y}, {va}, {donneurs}, {receveurs})")

    # Vecteurs cumules (ou de Lorenz)
    la: npt.NDArray = np.cumsum(va)
    ly: npt.NDArray = np.cumsum(y)

    # Indices et quantite a transferer a renvoyer
    j_tmax, i_tmax, t_max = -1, -1, -1

    for i in receveurs:
        for j in donneurs[np.where(donneurs > i)]:
            min_lorenz: float = np.min((la - ly)[i:j]) # preserver la dominance de lorenz
            t: float = min(y[i+1] - y[i], y[j] - y[j-1], va[i] - y[i], y[j] - va[j], min_lorenz) # preserver l'ordre (valeurs) + donner/recevoir le necessaire

            if t > t_max: # prendre la quantite maximale
                j_tmax, i_tmax, t_max = j, i, t

    if verbose:
        print("|\t\tj =", j_tmax + 1, "| i =", i_tmax + 1, "| t =", t_max)

    return j_tmax, i_tmax, t_max

    
def glouton_fute(y: npt.NDArray, va: npt.NDArray, donneurs: npt.NDArray, receveurs: npt.NDArray, verbose: bool = False)-> tuple[int, int, float]:
    '''
    Retourne les indices j du donneur, i du receveur et la quantite de richesse transfere t.
    
    Heuristique glouton fute (Algorithme 7, page 190): 
        Transfert de la quantite de richesse la plus grande possible parmi celles
        qui permettent une redistribution en un transfert pour un des agents concernes.
 
    Parametres
    ----------
        y: vecteur courant 
        a: vecteur dominant
        donneurs: liste des agents qui doivent etre donneurs (taille > 0)
        receveurs: liste des agents qui doivent etre receveurs (taille > 0)
        verbose: affichage si vrai (version indices de 1 a n)
    '''
    if verbose:
        print(f"\tAppel glouton fute({y}, {va}, {donneurs}, {receveurs})")

    d_etoile: npt.NDArray = np.array([j for j in donneurs if j > 0 and y[j] - y[j-1] >= y[j] - va[j]])
    r_etoile: npt.NDArray = np.array([i for i in receveurs if i < len(y)-1 and y[i+1] - y[i] >= va[i] - y[i]])

    if verbose:
        print("|\t\tR* =", [i + 1 for i in r_etoile])
        print("|\t\tD* =", [j + 1 for j in d_etoile])

    return glouton(y, va, d_etoile, r_etoile, verbose)
