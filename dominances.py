import numpy as np
import numpy.typing as npt

# DOMINANCES entre alternatives #

def indice_gini(v: npt.NDArray)-> float:
    ''' 
    Retourne l'indice de Gini du vecteur v.
    '''
    n: int = len(v)
    somme_vecteur_ordonne = np.sum(v.vecteur_ordonne)
    vecteur_i = np.arange(1, n + 1) # [1, 2, ..., n]
    return (2 * vecteur_i @ v) / (n * somme_vecteur_ordonne) - (n + 1) / n


def dominance_avec_gini(va: npt.NDArray, vb: npt.NDArray)-> bool:
    ''' 
    Retourne True si va domine vb au sens de l'indice de Gini, 
    False sinon.

    Parametres
    ----------
        va: vecteur pouvant etre dominant
        vb: vecteur pouvant etre domine
    '''
    return indice_gini(va) < indice_gini(vb)


def dominance_pareto(va: npt.NDArray, vb: npt.NDArray)-> bool: 
    ''' 
    Retourne True si va domine vb au sens de la dominance (faible) de Pareto, 
    False sinon.

    Parametres
    ----------
        va: vecteur pouvant etre dominant
        vb: vecteur pouvant etre domine
    '''
    return np.all(vb <= va)


def dominance_lorenz(va: npt.NDArray, vb: npt.NDArray, restreinte: bool)-> bool: 
    ''' 
    Retourne True si va domine vb au sens de la dominance de Lorenz restreinte ou generalisee, 
    False sinon.

    Parametres
    ----------
        va: vecteur pouvant etre dominant
        vb: vecteur pouvant etre domine
        restreinte: dominance restreinte si True, generalisee sinon
    '''
    va_lorenz: npt.NDArray = np.cumsum(va)
    vb_lorenz: npt.NDArray = np.cumsum(vb)
    dominance: bool = np.all(vb_lorenz <= va_lorenz) 
    if restreinte:
        return dominance and np.isclose(va_lorenz[-1], vb_lorenz[-1])
    return dominance

