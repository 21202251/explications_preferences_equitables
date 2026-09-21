# Implémentation des algorithmes de génération d'explications pour des préférences équitables

## 1. Présentation du projet

Ce projet contient la ré-implémentation des différentes méthodes étudiées pour la comparaison d'alternatives et la génération d'explications **ATX** et **CTX**.
Source : "Certified explanations of robust models" (Willot, 2024)

L'implémentation est organisée de manière modulaire afin de séparer :

- les fonctions élémentaires de comparaison entre alternatives ;
- les méthodes de génération d'explications ;
- les heuristiques associées aux différentes relations de dominance ;
- les opérateurs OWA et les schémas associés ;
- les modèles de programmation linéaire ;
- la génération des données expérimentales ;
- les tests unitaires.

## 2. Arborescence du projet

L'arborescence générale du projet est organisée de la manière suivante :

```text
Implementation/
│
├── Algorithmes centraux/
│   ├── dominances.py
│   ├── schemas_ATX.py
│   ├── heuristiques_lorenz_restreinte.py
│   ├── heuristiques_lorenz_generalisee.py
│   ├── algorithmes_owa.py
│   ├── programmation_lineaire.py
│   └── outils_programmation_lineaire.py
│
├── Donnees/
│   └── generation_donnees.py
│
└── Tests unitaires/
    ├── tests_heuristiques_lorenz_restreinte.py
    ├── tests_heuristiques_lorenz_generalisee.py
    ├── tests_programmation_lineaire_lorenz.py
    └── tests_owa.py
```

## 3. Organisation des modules

### 3.1 Comparaison des alternatives

Le fichier `dominances.py` regroupe les fonctions permettant de comparer deux alternatives selon les différentes relations de dominance considérées dans les algorithmes.

Ces fonctions constituent des briques élémentaires de l'implémentation. Elles sont notamment utilisées lorsque les méthodes doivent déterminer si une alternative domine une autre selon :

- la dominance de Lorenz restreinte ;
- la dominance de Lorenz généralisée.

### 3.2 Génération des explications ATX

Le fichier `schemas_ATX.py` constitue l'un des fichiers centraux de l'implémentation.

Il regroupe les fonctions générales permettant de construire des explications ATX selon deux approches principales :

- une approche heuristique ;
- une approche fondée sur la programmation linéaire.

La structure générale du schéma ATX est ainsi séparée de la méthode utilisée pour rechercher l'explication.

Dans le cas de l'approche heuristique, les procédures spécifiques aux différentes relations de dominance sont regroupées dans des modules dédiés.

Le fichier `heuristiques_lorenz_restreinte.py` contient les heuristiques associées à la dominance de Lorenz restreinte, tandis que le fichier `heuristiques_lorenz_generalisee.py` contient celles associées à la dominance de Lorenz généralisée.

Ces fonctions sont fournies en paramètre aux fonctions générales définies dans `schemas_ATX.py`.

### 3.3 OWA et schémas associés

Le fichier `algorithmes_owa.py` regroupe les fonctions relatives aux opérateurs OWA (*Ordered Weighted Averaging*) et aux schémas associés à cette approche.

Ce module est volontairement séparé des fonctions générales de comparaison et des procédures spécifiques aux explications ATX.

### 3.4 Programmation linéaire

L'approche fondée sur la programmation linéaire est séparée en deux composantes principales.

#### `programmation_lineaire.py`

Ce fichier contient les fonctions permettant de construire et d'écrire les programmes linéaires correspondant aux différents problèmes considérés.

Les modèles ainsi construits sont ensuite transmis au solveur **Gurobi** afin d'être résolus.

#### `outils_programmation_lineaire.py`

Le traitement des solutions est regroupé dans ce fichier.

Il contient notamment les fonctions permettant de :

- lire les fichiers de solution produits par le solveur ;
- extraire les valeurs des variables ;
- transformer les résultats en structures directement utilisables par les algorithmes.

### 3.5 Génération des données

Le fichier `generation_donnees.py` contient les fonctions utilisées pour générer les instances nécessaires aux différentes expérimentations.

### 3.6 Tests unitaires

La ré-implémentation est accompagnée de plusieurs fichiers de tests unitaires correspondant aux principaux modules du projet.

Les tests portent sur :

- les procédures heuristiques ;
- les fonctions de construction des programmes linéaires ;
- les algorithmes OWA.

Les tests unitaires permettent de vérifier individuellement les différents éléments de base de l'implémentation avant leur utilisation dans les méthodes complètes.

## 4. Dépendances

Le projet utilise notamment **Gurobi** pour résoudre les programmes linéaires générés par l'approche de programmation linéaire.

Le chemin d'installation de Gurobi doit être adapté dans les fichiers :

- `algorithmes_owa.py` ;
- `schemas_ATX.py`.

Les autres dépendances Python nécessaires au fonctionnement du projet sont :

- `numpy`
- `pulp`
- `matplotlib`
- `pandas`
- `seaborn`
- `csv`
- `subprocess`
- `time`

## 5. Exécution

Pour exécuter un script Python, il faut se placer dans le dossier principal du projet, puis ajouter le nom du sous-dossier avant celui du fichier à tester.

Par exemple :

```bash
python -m Tests_unitaires.tests_owa
```

De la même manière, les autres tests peuvent être exécutés avec :

```bash
python -m Tests_unitaires.tests_heuristiques_lorenz_restreinte
python -m Tests_unitaires.tests_heuristiques_lorenz_generalisee
python -m Tests_unitaires.tests_programmation_lineaire_lorenz
```
