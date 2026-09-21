import numpy as np 
import numpy.typing as npt 

# HEURISTIQUES - Dominance de Lorenz generalisee #

def ruissellement(vb: npt.NDArray, va: npt.NDArray, U: float, verbose: bool = False)-> npt.NDArray:
    ''' 
    Renvoie le vecteur vb auquel on a ajoute le surplus de richesse de va.

    Ruissellement (Algorithme 8, page 200):
        Ce surplus est redistribue aux agents les plus riches.

    Parametres
    ----------
        vb: vecteur courant
        va: vecteur dominant
        U: borne superieure de richesse pour chaque agent 
        verbose: affichage si vrai (version indices de 1 a n)
    '''
    if verbose:
        print(f"\tAppel ruissellement({vb}, {va}, {U})")
    
    g: float = np.sum(va) - np.sum(vb)
    assert g > 0, "Le surplus de richesse doit etre strictement positif."

    n: int = len(vb)
    k: int = n-1 # agent qui recoit en premier (i.e. le plus riche)
    x: npt.NDArray = np.copy(vb)

    # Tant que tout le surplus n'a pas ete distribue, on le donne aux agents riches
    while(g != 0):
        if verbose:
            print("\t\tEtape", n-k, ": g =", g)

        assert x[k] <= U, "La borne superieure n'est pas correcte."

        if x[k] + g > U:
            g = g - (U - x[k])
            x[k] = U 
            k = k - 1
        else:
            x[k] = x[k] + g
            g = 0 

    return x


def don_equitable(vb: npt.NDArray, va: npt.NDArray, U: float = np.inf, verbose: bool = False)-> npt.NDArray:
    ''' 
    Renvoie le vecteur vb auquel on a ajoute le surplus de richesse de va.

    Don equitable (Algorithme 9, page 201):
        Ce surplus est redistribue aux agents les plus pauvres.
    
    Parametres
    ----------
        vb: vecteur courant
        va: vecteur dominant
        U: borne superieure de richesse pour chaque agent (ici, seulement utile pour formatage)
        verbose: affichages si vrai (version indices de 1 a n)
    '''
    if verbose:
            print(f"\tAppel don_equitable({vb}, {va}, {U})")

    # Vecteurs cumules (ou de Lorenz)
    la: npt.NDArray = np.cumsum(va)
    lb: npt.NDArray = np.cumsum(vb)
    
    k: int = 0 
    y2: npt.NDArray = np.copy(vb)
    g: float =  np.sum(va) - np.sum(vb)

    if verbose:
        print("\t\tg =", g)

    g_perf: float = 0 
    non_finis: list[int] = [] 

    # Tant que tout le surplus n'a pas ete distribue, on continue de modifier le vecteur
    while(g != 0):

        g_perf = min(g, max(0, va[k] - y2[k]), np.min(la[k:] - lb[k:]))        
        
        if y2[k+1] - y2[k] < g_perf:
            g = g - (y2[k+1] - y2[k])
            y2[k] = y2[k+1]
            non_finis.append(k)
        else:
            g = g - g_perf 
            y2[k] = y2[k] + g_perf

        if verbose:
            print("\t\tEtape", k+1, ": g_perf =", g_perf, "| y2 =", y2)
        
        # Possibilite de redonner de l'argent aux agents les plus pauvres si les contraintes liees a l'ordre social le permettent
        for j in non_finis:

            g_perf = min(g, max(0, va[j] - y2[j]))
            g_perf = min(g_perf, np.min(la[j:] - lb[j:]))

            if g_perf > 0:
                if y2[j+1] - y2[j] < g_perf:
                    g = g - (y2[k+1] - y2[k])
                    y2[k] = y2[k+1]
                else:
                    g = g - g_perf 
                    y2[k] = y2[k+1] + g_perf
                    non_finis.remove(j)

            if verbose:
                print("\t\tnon_finis :", j, ", g_perf =", g_perf, "| y2 =", y2)    
            
        k = k + 1 

    return y2


