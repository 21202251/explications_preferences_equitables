from Algorithmes_centraux.programmation_lineaire import *

from Algorithmes_centraux.schemas_ATX import recuperer_PL_ATX

N: int = 5 # nombre de dimensions = d'agents
L: int = 5 # nombre d'etapes

sat: bool = False # vrai si PL version satisfiabilite, faux si version optimisation
dominance: str = "generalisee" # restreinte, generalisee
entier: bool = True # vrai si variables entieres, faux si reelles
nom1: str = "sat" if sat else "opt"
nom2: str = dominance[:3]
verbose: bool = False

print("TESTS PROGRAMMATION LINEAIRE - DOMINANCE DE LORENZ")
#--------------------------------------------

# exemples
a = np.sort([76, 21, 88, 29, 26])
d = np.sort([90, 24, 12, 14, 100])
f = np.sort([18, 96, 6, 17, 88])
vec1 = a
vec2 = d if dominance == "restreinte" else f # d pour restreint, f sinon 

# affichages
#print("Depart :", vec2)
#print("Objectif :", vec1)
#print("--------------------")
explication = recuperer_PL_ATX(L, N, vec2, vec1, sat, dominance, entier, verbose=verbose)
#print(explication)

assert(np.array_equal(recuperer_PL_ATX(L, N, 
                                       d, a, 
                                       sat=False, dominance="restreinte", 
                                       entier=True, verbose=verbose), [ [12.0, 14.0, 24.0, 90.0, 100.0], 
                                                                        [12.0, 14.0, 38.0, 76.0, 100.0], 
                                                                        [12.0, 26.0, 38.0, 76.0, 88.0], 
                                                                        [21.0, 26.0, 29.0, 76.0, 88.0]
                                                                       ]))
assert(np.array_equal(recuperer_PL_ATX(L, N, 
                                       f, a, 
                                       sat=False, dominance="generalisee", 
                                       entier=True, verbose=verbose), [ [6.0, 17.0, 18.0, 88.0, 96.0], 
                                                                        [9.0, 18.0, 29.0, 88.0, 96.0], 
                                                                        [9.0, 26.0, 29.0, 88.0, 88.0], 
                                                                        [21.0, 26.0, 29.0, 76.0, 88.0]
                                                                      ]))

print("-> OK !")
