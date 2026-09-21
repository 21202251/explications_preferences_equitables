import csv
import numpy as np
import numpy.typing as npt

def pl_solutions(nom_fichier: str)-> tuple[float, dict[str, float]]:
    '''
    Retourne le tuple (solution objectif, dictionnaire (variable, valeur))
    des solutions du programme lineaire dont le resultat est donne dans
    un fichier '.sol'.

    Parametres
    ----------
        nom_fichier: nom du fichier contenant la solution d'un PL
    '''
    # Verification des conditions sur les parametres
    assert nom_fichier.endswith(".sol"), "Le fichier de la solution du PL doit etre un '.sol'."

    # Ouverture du fichier avec csv
    try:
        with open(nom_fichier, newline='\n') as fichier_csv:
            reader = csv.reader(fichier_csv, delimiter=' ')

            # Passer l'entete
            next(reader)

            # Enregistrer le resultat de la fonction objectif
            sol_objectif: list[str] = next(reader)
            solution: str
            _, _, _, _, solution = sol_objectif
            solution_float: float = float(solution)

            # Enregistrer les solutions des variables dans un dictionnaire
            dico_solutions: dict[str, float] = dict()
            for var, value in reader:
                dico_solutions[var] = float(value)

    except:
        return (-1, dict())
        assert "Mauvais" == "Format", "Le contenu du fichier n'est pas formate de la maniere suivante :\n\t1 ligne d'entete, 1 ligne '# Objective value = <solution>',  1+ ligne(s) '<nom_variable> <solution>'."

    return (solution_float, dico_solutions)

#----------------------------------------------------------------------

def extraire_indices(nvar: str, dico: dict[str, float])-> list[tuple[list[str], float]]:
    '''
    Parcourt le dictionnaire des solutions et retourne, pour chaque variable
    dont le nom commence par "<nvar>_", la liste de ses indices (sous forme
    de chaines) accompagnee de sa valeur.
    Factorise le parcours commun aux fonctions lister_var_*.

    Parametres
    ----------
        nvar: nom de la variable
        dico: dictionnaire des solutions du PL
    '''
    resultats: list[tuple[list[str], float]] = []
    var: str
    val: float
    for (var, val) in dico.items():
        if var[:len(nvar)+1] == nvar + "_":
            indice = var[len(nvar)+1:].split("_")
            resultats.append((indice, val))
    return resultats

#----------------------------------------------------------------------

def formater_ligne(valeurs, entier: bool)-> str:
    '''
    Construit la chaine "v1 v2 ... " a partir d'une suite de valeurs,
    chaque valeur etant convertie en entier si demande.
    Factorise la construction de ligne commune aux fonctions afficher_var_2d*.

    Parametres
    ----------
        valeurs: suite de valeurs a mettre en forme
        entier: vrai si les variables sont entieres, faux si reelles
    '''
    ligne = ""
    for x in valeurs:
        x = int(x) if entier else x
        ligne += str(x) + " "
    return ligne


def lister_var( nvar: str,
                dico: dict[str, float],
                dimensions: tuple[int, ...] | None = None,
                ensembles: tuple | None = None,
              ) -> tuple[dict, npt.NDArray]:
    '''
    Retourne le dictionnaire et la matrice des variables nvar.

    Parametres
    ----------
        nvar: nom de la variable
        dico: dictionnaire des solutions du PL
        dimensions : dimensions de la matrice si elles sont connues
        ensembles : ensembles d'indices si les indices ne sont pas
                    consecutifs (ex: (L,) ou (L, N))
    '''
    dic = {}

    # Extraction des variables
    for indice, val in extraire_indices(nvar, dico):
        indices = tuple(int(i) for i in indice)
        dic[indices if len(indices) > 1 else indices[0]] = val

    # Détermination des dimensions / mappings
    if ensembles is not None:
        mappings = tuple({indice: i for i, indice in enumerate(ensemble)} for ensemble in ensembles)
        dimensions = tuple(len(ensemble) for ensemble in ensembles)

    elif dimensions is not None:
        mappings = tuple({i: i for i in range(dim)} for dim in dimensions)

    else:
        # Dimensions déduites des indices présentes
        if not dic:
            return dic, []

        if len(next(iter(dic))) if isinstance(next(iter(dic)), tuple) else 1:
            pass

        nb_dim = len(next(iter(dic))) if isinstance(next(iter(dic)), tuple)    else 1

        dimensions = tuple(
            max(indice[d] if isinstance(indice, tuple) else indice for indice in dic) + 1
            if nb_dim == 1
            else
            max(indice[d] for indice in dic) + 1 for d in range(nb_dim)
        )

        mappings = tuple({i: i for i in range(dim)} for dim in dimensions)

    # Construction de la matrice
    if len(dimensions) == 1:
        mat = [0 for _ in range(dimensions[0])]

        for indice, val in dic.items():
            i = mappings[0][indice]
            mat[i] = val

    elif len(dimensions) == 2:
        mat = [[0 for _ in range(dimensions[1])]
            for _ in range(dimensions[0])]

        for (i, j), val in dic.items():
            ii = mappings[0][i]
            jj = mappings[1][j]
            mat[ii][jj] = val

    else:
        raise ValueError("Nombre de dimensions non supporte.")

    return dic, np.array(mat)


def afficher_var(   nvar: str,
                    mat: list,
                    entier: bool,
                    axes: tuple | None = None
                ) -> None:
    '''
    Affiche une matrice de variables.

    Parametres
    ----------
        nvar : nom de la variable
        mat : matrice à afficher
        entier : vrai si les variables sont entières, faux si elles sont réelles
        axes : ensembles d'indices utilisés pour les dimensions.
               Par exemple :
                   None              -> indices 0, 1, 2, ...
                   (L,)              -> indices de L
                   (L, N)            -> indices de L et N
    '''
    # Pas d'axes fournis : on utilise les indices de la matrice
    if axes is None:
        axes = tuple(range(len(mat)),)

    if len(axes) == 1:
        for i, k in enumerate(axes[0]):
            x = int(mat[i]) if entier else mat[i]
            print(f"k={k+1}: {x}")

    elif len(axes) == 2:
        for i, k in enumerate(axes[0]):
            ligne = formater_ligne(mat[i], entier)
            print(f"k={k+1}:", ligne)
    else:
        raise ValueError("L'affichage ne marche que pour 1 ou 2 dimensions.")

    print("--------------------")
