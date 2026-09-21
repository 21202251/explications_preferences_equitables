import numpy as np # pour representer les alternatives

from Algorithmes_centraux.schemas_ATX import ATX
from Algorithmes_centraux.heuristiques_lorenz_restreinte import hlp, glouton, glouton_fute

verbose: bool = False

print("TESTS HEURISTIQUES VERSION DOMINANCE DE LORENZ RESTREINTE")
#--------------------------------------------

## alternatives considerees (exemple 20 page 40)
N: int = 5 # nombre de dimensions = d'agents
a = np.sort([76, 21, 88, 29, 26])
b = np.sort([23, 76, 34, 82, 22])
d = np.sort([90, 24, 12, 14, 100])
e = np.sort([26, 20, 100, 26, 26])
f = np.sort([18, 96, 6, 17, 88])
c = np.sort([72, 17, 90, 34, 39])
alternatives = [a, b, c, d, e, f]

## tests T-ATX
# d < a en 4 etapes (exemple 21 page 43)
assert np.array_equal(ATX(d, 
                          a, 
                          hlp, 
                          verbose = verbose),  [d, 
                                                np.array([12, 14, 29, 85, 100]),
                                                np.array([12, 23, 29, 76, 100]),
                                                np.array([12, 26, 29, 76, 97]), 
                                                a])

# d < a en 5 etapes (exemple 22 page 51)
assert np.array_equal(ATX(d, 
                          a, 
                          glouton, 
                          verbose = verbose),  [d,
                                                np.array([12, 24, 24, 80, 100]),
                                                np.array([21, 24, 24, 80, 91]),
                                                np.array([21, 24, 28, 76, 91]),
                                                np.array([21, 26, 28, 76, 89]), 
                                                a])

# d < a en 3 etapes (exemple 23 page 51) -> optimal
assert np.array_equal(ATX(d, 
                          a, 
                          glouton_fute, 
                          verbose = verbose),  [d,
                                                np.array([12, 14, 29, 85, 100]),
                                                np.array([12, 26, 29, 85, 88]), 
                                                a])

print("-> OK !")
