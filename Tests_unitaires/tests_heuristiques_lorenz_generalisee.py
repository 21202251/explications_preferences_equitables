import numpy as np # pour representer les alternatives
import numpy.typing as npt

from Algorithmes_centraux.schemas_ATX import ATX
from Algorithmes_centraux.heuristiques_lorenz_restreinte import hlp, glouton_fute
from Algorithmes_centraux.heuristiques_lorenz_generalisee import ruissellement, don_equitable

N: int = 5 # nombre de dimensions = d'agents
U: int = 100 # borne superieure du domaine

verbose: bool = False

print("TESTS HEURISTIQUES VERSION DOMINANCE GENERALISEE")
#--------------------------------------------

## Alternatives considerees et leur richesse totale (exemple 20 page 40)
N: int = 5 # nombre de dimensions = d'agents
a = np.sort([76, 21, 88, 29, 26]) # 240
b = np.sort([23, 76, 34, 82, 22]) # 237
c = np.sort([72, 17, 90, 34, 39]) # 252
d = np.sort([90, 24, 12, 14, 100]) # 240
e = np.sort([26, 20, 100, 26, 26]) # 198
f = np.sort([18, 96, 6, 17, 88]) # 225
np.sorts = [a, b, c, d, e, f]

## test ruissellement
res_ruiss: npt.NDArray = ruissellement(f, c, U)
assert np.array_equal(res_ruiss, np.array([6, 17, 29, 100, 100])), res_ruiss

## tests ATX_avec_ruissellement 
res = ATX(f, a, glouton_fute, pretraitement = ruissellement, U = U)
#for alt in res:
    #print(alt)

## tests don_equitable 
assert np.array_equal(don_equitable(f, a, verbose = False), np.array([17, 18, 21, 88, 96]))

## tests ATX_avec_don_equitable
res = ATX(f, a, hlp, pretraitement = don_equitable)
res = ATX(f, a, glouton_fute, pretraitement = don_equitable)

## tests don final 
assert np.array_equal(ATX(f, 
                          b, 
                          hlp, 
                          don_final = True),   [f, 
                                                np.array([6, 17, 30, 76, 96]), 
                                                np.array([6, 17, 34, 76, 92]), 
                                                np.array([6, 23, 34, 76, 86]), 
                                                np.array([10, 23, 34, 76, 82]), 
                                                b])

assert np.array_equal(ATX(f, 
                          b, 
                          glouton_fute, 
                          don_final = True),   [f, 
                                                np.array([6, 17, 30, 76, 96]), 
                                                np.array([6, 23, 30, 76, 90]), 
                                                np.array([14, 23, 30, 76, 82]), 
                                                b])

print("-> OK !")
