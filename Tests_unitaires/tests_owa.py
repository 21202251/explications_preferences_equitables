from Algorithmes_centraux.programmation_lineaire import *

from Algorithmes_centraux.algorithmes_owa import *

np.set_printoptions(legacy = "1.25") # afficher les valeurs sans les types de numpy

print("TESTS PROGRAMMATION LINEAIRE - OWA")
#--------------------------------------------
print("\tTEST DOMINANCES OWA")
# exemples 1
N: int = 3
M: int = 2
b1 = np.sort( [9, 11, 21])
a1 = np.sort( [6, 18, 20])
b2 = np.sort( [5, 12, 15])
a2 = np.sort( [8, 10, 13])
aj = [a1, a2]
bj = [b1, b2]
b0 = np.sort( [6, 8, 21])
a0 = np.sort( [3, 20, 23])
#print("Vecteur domine ?", b0)
#print("Vecteur dominant ?", a0)
assert dominance_OWA_robuste(N, b0, a0, M, aj, bj, verbose=False)

# exemples 2
option: int = 0 # choix du nombre d'etapes (option 0 : L=3 ; option 1 : L=9)
N = 5
M = 1
L = 3 if option == 0 else 9
entier = True
a = np.sort( [76, 21, 88, 29, 26])
b = np.sort( [23, 76, 34, 82, 22])
c = np.sort( [72, 17, 90, 34, 39])
e = np.sort( [26, 20, 100, 26, 26])
f = np.sort( [18, 96, 6, 17, 88])
vec1 = e if option == 0 else f 
vec2 = b if option == 0 else e
aj = [a]
bj = [c]
#print("Vecteur domine ?", vec1)
#print("Vecteur dominant ?", vec2)
assert dominance_OWA_robuste(N, vec1, vec2, M, aj, bj, verbose = False)

# tests ATX OWA
print("\tTEST PL ATX OWA")
assert len(recuperer_PL_ATX(3, N, e, b, 
                            True, "owa", entier, 
                            M, aj, bj, 
                            verbose=False)) == len(atx_Optimal(N, e, b, 
                                                                entier, 
                                                                M, aj, bj, 
                                                                timeout=100))
assert len(recuperer_PL_ATX(9, N, f, e,
                             True, "owa", entier, 
                             M, aj, bj, 
                             verbose = False)) == len(atx_Optimal(N, f, e, 
                                                                  entier, 
                                                                  M, aj, bj, 
                                                                  timeout = 100))

print("\tTEST CERTIFICAT DE FARKAS 4.10")
lambdas, dons, transferts = recuperer_Farkas_1(N, vec1, vec2, entier, M,  aj, bj)
#print(lambdas, dons, transferts)

print("\tTEST CERTIFICAT DE FARKAS 4.9")
lambdas_2, dons_2, vp, vn = recuperer_Farkas_2(N, vec1, vec2, entier, M, aj, bj)
#print(lambdas_2, dons_2, vp, vn)

print("\tTEST MILP PI LORENZ F.3")
explication = rff(N, vec1, vec2, entier, M, lambdas, aj, bj, False)
assert explication
#print(explication)

print("\tTEST PERMUTATIONS")
compromis = np.array([aj[i] - bj[i] for i in range(len(aj))])
explication = algorithme_permutation(vec1, vec2, lambdas, dons, transferts, compromis)
assert explication
#print(explication)

# TEST CTX OWA VERSION 1 OK, VERSION OPTIMALE NON 
print("\tTEST CTX FIG 4.5")
explication = ctx(N, vec1, vec2, lambdas, dons, transferts, aj, bj, 0, 100)
assert explication
#print(explication)

print("-> OK !")
