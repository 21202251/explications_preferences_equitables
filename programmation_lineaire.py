import numpy as np
import numpy.typing as npt

import pulp

M2: float = 10e6 # borne superieure pour les coefficients de congruence

# PROGRAMMATION LINEAIRE #

def pl_ATX(l: int, n: int, vb: npt.NDArray, va: npt.NDArray, 
           sat: bool, dominance: str, entier: bool, 
           m: int = None, aj = None, bj = None)-> bool:
    '''
    Ecrit dans un fichier "pl_atx_{<sat>,<opt>}_{<res>,<gen>,<owa>}.lp" 
    le programme lineaire qui donne le schema ATX pour passer du vecteur vb au vecteur va 
    (avec va qui domine vb du pdv de la dominance de Lorenz ou des OWA robustes pour un ensemble de preferences I)
    en procedant a des transferts redistributifs 
    + des dons si version non restreinte
    + des congruences si version OWA. 

    Retourne False si la planification est impossible a ecrire,
    True dans les autres cas (determines ou non). 

    Programmes lineaires possibles : 
        - Sat & Res : B.1 (page 185)
        - Opt & Res : B.2 (page 187)
        - Sat & Gen : C.1 (page 196)
        - Opt & Gen : C.2 (page 198)
        - Sat & OWA : F.1 (page 212)
        - Opt & OWA :  /

    Parametres
    ----------
        l: nombre d'etapes de l'explication (l+1 vecteurs)
        n: nombre de dimensions / d'agents
        vb: vecteur domine
        va: vecteur dominant
        sat: vrai si version satisfiabilite, faux si version optimisation
        dominance: type de dominance ("restreinte", "generalisee", "owa") 
        entier: vrai si les variables sont entieres, faux si reelles
        m: nombre de preferences donnees par l'utilisateur
        aj: liste des vecteurs dominants (preferences utilisateurs)
        bj: liste des vecteurs domines (preferences utilisateurs)
    '''
    assert dominance in {"restreinte", "generalisee", "owa"}, "Nom de dominance invalide"
    assert not(not sat and dominance == "owa"), "Pas de borne sur la taille de l'explication pour les OWA robustes"


    # CREATION DU PROBLEME
    probleme = pulp.LpProblem("", pulp.LpMinimize)


    # VARIABLES 
    variables = dict()
    cat = "Integer" if entier else "Continuous"

    # Variables avec (l+1)*n contraintes
    for k in range(l+1):
        for i in range(n):
            # (x_k_i) : vecteur de distribution a l'etape k
            variables[f"x_{k}_{i}"] = pulp.LpVariable(f"x_{k}_{i}", lowBound=0, cat=cat) #x_k_i >= 0

    # Variables avec l*n contraintes
    for k in range(l):
        for i in range(n):
            # (vp_k_i) : quantite de richesse recue par l'agent i grace a un transfert redistributif a l'etape k
            variables[f"vp_{k}_{i}"] = pulp.LpVariable(f"vp_{k}_{i}", lowBound=0, cat=cat) #vp_k_i >= 0   

            # (vn_k_i) : quantite de richesse donnee par l'agent i grace a un transfert redistributif a l'etape k
            variables[f"vn_{k}_{i}"] = pulp.LpVariable(f"vn_{k}_{i}", lowBound=0, cat=cat) #vn_k_i >= 0 

            # (gammap_k_i) = 1 si l'agent i recoit une quantite de richesse strictement positive grace a un transfert redistributif a l'etape k
            variables[f"gammap_{k}_{i}"] = pulp.LpVariable(f"gammap_{k}_{i}", lowBound=0, cat="Binary") #gammap_k_i, 0 ou 1

            # (gamman_k_i) = 1 si l'agent i donne une quantite de richesse strictement positive grace a un transfert redistributif a l'etape k
            variables[f"gamman_{k}_{i}"] = pulp.LpVariable(f"gamman_{k}_{i}", lowBound=0, cat="Binary") #gamman_k_i, 0 ou 1

            if dominance != "restreinte":
                # (u_k_i) : quantite de richesse recue par l'agent i grace a un don a l'etape k
                variables[f"u_{k}_{i}"] = pulp.LpVariable(f"u_{k}_{i}", lowBound=0, cat=cat) #u_k_i >= 0

    # Variables avec l*n*(n-1)/2 contraintes 
    for k in range(l):
        for i in range(n-1):
            for j in range(i+1, n):
                # (t_k_j_i) = 1 s'il y a un transfert redistributif de j a i effectue a l'etape k
                variables[f"t_{k}_{j}_{i}"] = pulp.LpVariable(f"t_{k}_{j}_{i}", lowBound=0, cat="Binary") #t_k_j_i, 0 ou 1

    # Variables avec l contraintes
    for k in range(l):
        if not sat: 
            # (s_k) = 1 s'il y a une operation effectuee a l'etape k
            variables[f"s_{k}"] = pulp.LpVariable(f"s_{k}", lowBound=0, cat="Binary") #s_k, 0 ou 1

        if dominance != "restreinte":
            # (g_k) = 1 s'il y a un don effectue a l'etape k
            variables[f"g_{k}"] = pulp.LpVariable(f"g_{k}", lowBound=0, cat="Binary") #g_k, 0 ou 1

    # Variables avec l*m contraintes
    if dominance == "owa":
        for k in range(l):
            for j in range(m):
                # (lambda_k_j) : valeur du coefficient associe a la congruence avec la j-eme comparaison a l'etape k
                variables[f"lambda_{k}_{j}"] = pulp.LpVariable(f"lambda_{k}_{j}", lowBound=0, cat="Continuous") #lamba_k_j, >= 0

                # (pi_k_j) = 1 si s'il y a une congruence effectuee avec la j-eme comparaison a l'etape k
                variables[f"pi_{k}_{j}"] = pulp.LpVariable(f"pi_{k}_{j}", lowBound=0, cat="Binary") #pi_k_j, 0 ou 1
                    

    # FONCTION OBJECTIF

    if sat:
        probleme += 0, "Objectif"
    else: # Forcer la reduction du nombre de transferts/dons et le fait qu'ils soient effectues dans les premieres etapes du processus
        probleme += pulp.lpSum((1 + (k/(n**2)))*variables[f"s_{k}"] for k in range(l)), "Objectif"


    # CONTRAINTES 
        
    for i in range(n):
        # (B.1) (vb est le vecteur de depart)
        probleme += variables[f"x_0_{i}"] == vb[i], f"Contrainte B.1 i={i}"

        # (B.2) (va est le vecteur a atteindre)
        probleme += variables[f"x_{l}_{i}"] == va[i], f"Contrainte B.2 i={i}"
            
    for i in range(n-1):
        for k in range(l+1): 
            # (B.3) (Conserver l'ordre sur les coordonnees des vecteurs x)
            probleme += variables[f"x_{k}_{i}"] <= variables[f"x_{k}_{i+1}"], f"Contrainte B.3 k={k},i={i}"
    
    for k in range(l): 
        # (B.4) (Quantite globale de richesse donnee = quantite globale de richesse recue)
        probleme += pulp.lpSum(variables[f"vp_{k}_{i}"] for i in range(n)) == pulp.lpSum(variables[f"vn_{k}_{i}"] for i in range(n)), f"Contrainte B.4 k={k}"

    M1: float = np.sum(va) + np.sum(vb) # borne superieure pour les quantites a redistribuer
    for i in range(n):
        for k in range(l): 
            # (B.5) (Quantite a recevoir d'un transfert limitee a la quantite de richesse totale disponible & gamma = 0 => v = 0)   
            probleme += M1 * variables[f"gammap_{k}_{i}"] - variables[f"vp_{k}_{i}"] >= 0, f"Contrainte B.5 k={k},i={i}"

            # (B.6) (Quantite a donner d'un transfert limitee a la quantite de richesse totale disponible & gamma = 0 => v = 0)
            probleme += M1 * variables[f"gamman_{k}_{i}"] - variables[f"vn_{k}_{i}"] >= 0, f"Contrainte B.6 k={k},i={i}"
                
    for k in range(l): 
        # (B.7) (Nombre de receveurs dans les transferts = nombre de donneurs dans les transferts)
        probleme += pulp.lpSum(variables[f"gammap_{k}_{i}"] for i in range(n)) == pulp.lpSum(variables[f"gamman_{k}_{i}"] for i in range(n)), f"Contrainte B.7 k={k}"
    
    for i in range(n):
        for j in range(i+1, n):
            for k in range(l):
                # (B.8) (S'il y a un transfert redistributif de j a i, alors j doit etre donneur et i doit etre receveur d'un transfert a l'etape k) 
                probleme += 2 * variables[f"t_{k}_{j}_{i}"] - variables[f"gamman_{k}_{j}"] - variables[f"gammap_{k}_{i}"] <= 0, f"Contrainte B.8 k={k},i={i},j={j}"

                # (B.9) (Si a l'etape k, j est donneur et i est receveur d'un transfert, alors il y a un transfert redistributif de j a i)
                probleme += 2 * variables[f"t_{k}_{j}_{i}"] - variables[f"gamman_{k}_{j}"] - variables[f"gammap_{k}_{i}"] >= -1, f"Contrainte B.9 k={k},i={i},j={j}"
                
    for k in range(l):
        # (B.10) (Nombre de transferts redistributifs = nombre de donneurs)
        probleme += pulp.lpSum(variables[f"t_{k}_{j}_{i}"] for i in range(n) for j in range(i+1, n)) == pulp.lpSum(variables[f"gamman_{k}_{j}"] for j in range(n)), f"Contrainte B.10 k={k}"

    # Borner les valeurs des dons
    if dominance != "restreinte": 
        for k in range(l):
            # (C.11) (Quantite a donner d'un don limitee a la quantite de richesse totale disponible & g = 0 => u = 0)
            # + ajout d'une contrainte (S'il y a un don, alors au moins un agent doit recevoir une quantite de richesse d'un don a l'etape k)
            probleme += M1 * variables[f"g_{k}"] - pulp.lpSum(variables[f"u_{k}_{i}"] for i in range(n)) >= 0, f"Contrainte C.11 k={k}"
            probleme += M1 * variables[f"g_{k}"] - pulp.lpSum(variables[f"u_{k}_{i}"] for i in range(n)) <= M1 - 10e-6, f"Contrainte C.11bis k={k}" # !!! version entiere

            if dominance == "owa":
                for j in range(m):
                    # (F.12)  (Quantite a donner d'une congruence limitee a la quantite de richesse totale disponible & pi = 0 => lambda = 0)
                    # + ajout d'une contrainte (S'il y a une congrunece, alors au moins un agent doit recevoir une quantite de richesse d'une congruence a l'etape k)  
                    probleme += M2 * variables[f"pi_{k}_{j}"] - variables[f"lambda_{k}_{j}"] >= 0, f"Contrainte F.12 k={k},j={j}"
                    probleme += M2 * variables[f"pi_{k}_{j}"] - variables[f"lambda_{k}_{j}"] <= M2 - 10e-6, f"Contrainte F.12bis k={k},j={j}"
                    
    # Une seule operation par etape 
    if sat:
        for k in range(l):
            operations = pulp.lpSum(variables[f"t_{k}_{j}_{i}"] for i in range(n) for j in range(i+1, n))
            if dominance == "restreinte":
                # (B.11) (Il n'y a qu'un transfert redistributif au maximum par etape)  
                probleme += operations <= 1, f"Contrainte B.11 k={k}"
                continue 

            operations += variables[f"g_{k}"]
            if dominance == "generalisee":
                # (C.12) (Il n'y a qu'un transfert redistributif ou don au maximum par etape)         
                probleme += operations <= 1, f"Contrainte C.12 k={k}"
                continue 

            operations += pulp.lpSum(variables[f"pi_{k}_{j}"] for j in range(m)) 
            # (F.13) (Il n'y a qu'un transfert redistributif ou don ou congruence au maximum par etape)         
            probleme += operations <= 1, f"Contrainte F.13 k={k}"
    else: 
        for k in range(l):
            # (B.24) (Il n'y a qu'une operation au maximum par etape) 
            probleme += variables[f"s_{k}"] <= 1, f"Contrainte B.24 k={k}"

    # Lier x_k+1 avec x_k                  
    for i in range(n):
        for k in range(l):
            valeur = variables[f"x_{k}_{i}"] + variables[f"vp_{k}_{i}"] - variables[f"vn_{k}_{i}"]
            if dominance == "restreinte":
                # (B.12) (La valeur de la coordonnee i d'un vecteur x a l'etape k+1 est mise a jour avec la quantite de recue et la quantite de richesse donnee a l'etape k)
                probleme += variables[f"x_{k+1}_{i}"] == valeur, f"Contrainte B.12 k={k},i={i}"
                continue
            
            valeur += variables[f"u_{k}_{i}"] 
            if dominance == "generalisee":
                # (C.13) (La valeur de la coordonnee i d'un vecteur x a l'etape k+1 est mise a jour avec la quantite de richesse recue (dont don) et la quantite de richesse donnee a l'etape k)
                probleme += variables[f"x_{k+1}_{i}"] == valeur, f"Contrainte C.13 k={k},i={i}"
                continue

            valeur += pulp.lpSum(variables[f"lambda_{k}_{j}"]*(aj[j][i]-bj[j][i]) for j in range(m))
            # (F.14) (La valeur de la coordonnee i d'un vecteur x a l'etape k+1 est mise a jour avec la quantite de richesse recue (dont don et congruences) et la quantite de richesse donnee (dont congruences) a l'etape k)        
            probleme += variables[f"x_{k+1}_{i}"] == valeur, f"Contrainte F.14 k={k},i={i}"
                
    # Optimisation 
    if not sat:
        # Relier s et les operations effectuees
        for k in range(l):
            valeur = pulp.lpSum(variables[f"t_{k}_{j}_{i}"] for i in range(n) for j in range(i+1, n))
            if dominance == "restreinte":
                # (B.23) (Nombre de transferts redistributifs effectues = nombre de transferts redistributifs autorises a l'etape k, i.e. 0 ou 1) 
                probleme += valeur == variables[f"s_{k}"], f"Contrainte B.23 k={k}"
                continue
            
            valeur += variables[f"g_{k}"]
            if dominance == "generalisee":
                # (C.25) (Nombre de dons + transferts redistributifs effectues = nombre de transferts redistributifs autorises a l'etape k, i.e. 0 ou 1) 
                probleme += valeur == variables[f"s_{k}"], f"Contrainte C.25 k={k}"
                continue 

            valeur += pulp.lpSum(variables[f"lambda_{k}_{j}"]*(aj[j][i]-bj[j][i]) for j in range(m))
            # (F.Bonus) (Nombre de dons + transferts redistributifs + congruences effectues = nombre de transferts redistributifs autorises a l'etape k, i.e. 0 ou 1) 
            probleme += valeur == variables[f"s_{k}"], f"Contrainte F.Bonus k={k}"            

        # Borner le nombre d'etapes 
        if dominance == "restreinte":
            r = np.where(va > vb)[0]
            d = np.where(va < vb)[0]
            maxi = max(len(d), len(r))
            try:
                # (B.25) (Nombre global de transferts redistributifs autorises)
                probleme += pulp.lpSum(variables[f"s_{k}"] for k in range(maxi)) == maxi, "Contrainte B.25"
            except:
                return False
            
        elif dominance == "generalisee":
            d = np.where(va < vb)[0]
            taille_d = len(d) + 1
            try:
                # (C.27)  (Nombre global de dons + transferts redistributifs autorises)
                probleme += pulp.lpSum(variables[f"s_{k}"] for k in range(taille_d)) == taille_d, "Contrainte C.27"
            except:
                return False

    # ECRITURE DU PL
    nom1: str = "sat" if sat else "opt"
    nom2: str = dominance[:3]
    probleme.writeLP(f"prog_lin/pl_atx_{nom1}_{nom2}.lp")

    return True


def pl_dominance_OWA_robuste(n: int, vb: npt.NDArray, va: npt.NDArray, 
                     m: int, aj: npt.NDArray, bj: npt.NDArray)-> None:
    ''' 
    Ecrit dans un fichier "pl_dominance_owa.lp" 
    le programme lineaire pour determiner si (vb,va) appartient a OWA_omega_I .  
    
    Programme lineaire de la figure 4.2 (page 76).

    Parametres
    ----------
        n: nombre de dimensions / d'agents
        vb: vecteur domine
        va: vecteur dominant
        m: nombre de preferences donnees par l'utilisateur
        aj: liste des vecteurs dominants (preferences utilisateurs)
        bj: liste des vecteurs domines (preferences utilisateurs)
    '''

    # CREATION DU PROBLEME
    probleme = pulp.LpProblem("", pulp.LpMinimize)

    # VARIABLES 

    variables: dict = dict()

    for i in range(n):
        # (w_i) : poids omega pour le i-eme agent
        variables[f"w_{i}"] = pulp.LpVariable(f"w_{i}", lowBound=0, cat="Continuous")

    # FONCTION OBJECTIF

    probleme += pulp.lpSum((va[i] - vb[i]) * variables[f"w_{i}"] for i in range(n)), "Objectif"

    # CONTRAINTES 

    for i in range(n-1):
        # (4.2b) (Poids omega ranges dans l'ordre decroissant)
        probleme += variables[f"w_{i}"] >= variables[f"w_{i+1}"], f"Contrainte 4.2b i={i}"

    # (4.2c) (Poids omega sommant a 1)
    probleme += pulp.lpSum(variables[f"w_{i}"] for i in range(n)) == 1, "Contrainte 4.2c"

    for j in range(m):
        # (4.2d) (Poids omega admissibles pour les preferences donnees par l'utilisateur)
        probleme += pulp.lpSum((aj[j][i] - bj[j][i]) * variables[f"w_{i}"] for i in range(n)) >= 0, f"Contrainte 4.2d j={j}"
    
    probleme.writeLP(f"prog_lin/pl_dominance_owa.lp")

# Certificats de Farkas

def pl_Farkas_1(n: int, vb: npt.NDArray, va: npt.NDArray, 
                entier: bool,
                m: int, aj: npt.NDArray, bj: npt.NDArray)-> None:
    '''
    Ecrit dans un fichier "pl_farkas_1.lp" 
    le programme lineaire qui donne le certificat de Farkas par la formule 4.10 pour le compromis (va - vb)
    (avec va qui domine vb du pdv de la dominance de Lorenz ou des OWAs robustes pour un ensemble de preferences I)
    en le decomposant en des transferts redistributifs 
    + des dons si version non restreinte
    + des congruences. 
    
    Programme lineaire de la formule 4.10 (page 84).

    Parametres
    ----------
        n: nombre de dimensions / d'agents
        vb: vecteur domine
        va: vecteur dominant 
        entier: vrai si les variables sont entieres, faux si reelles
        m: nombre de preferences donnees par l'utilisateur
        aj: liste des vecteurs dominants (preferences utilisateurs)
        bj: liste des vecteurs domines (preferences utilisateurs)
    '''

    # CREATION DU PROBLEME
    probleme = pulp.LpProblem("", pulp.LpMinimize)

    # VARIABLES

    variables: dict = dict()
    cat: str = "Integer" if entier else "Continuous"
        
    for j in range(m):
        # (lambda_j) : valeur du coefficient associe a la congruence avec la j-eme comparaison
        variables[f"lambda_{j}"] = pulp.LpVariable(f"lambda_{j}", lowBound=0, cat="Continuous") #lamba_j, >= 0

        
    for i in range(n):
        # (u_i) : quantite de richesse recue par l'agent i grace a un don
        variables[f"u_{i}"] = pulp.LpVariable(f"u_{i}", lowBound=0, cat=cat) #u_i

        
    for i in range(n-1):
            for j in range(i+1, n):
                # (tau_j_i) : quantite de richesse transferee de j a i 
                variables[f"tau_{j}_{i}"] = pulp.LpVariable(f"tau_{j}_{i}", lowBound=0, cat=cat) #tau_j_i

    # OBJECTIF 

    probleme += 0, "Objectif"

    # CONTRAINTES 

    for i in range(n):
        # (4.10) (Formule du certificat de Farkas)
        probleme += va[i] - vb[i] == variables[f"u_{i}"] + pulp.lpSum(variables[f"tau_{j}_{i}"] for j in range(i+1, n)) - pulp.lpSum(variables[f"tau_{i}_{h}"] for h in range(i)) + pulp.lpSum((aj[j][i] - bj[j][i])* variables[f"lambda_{j}"] for j in range(m)), f"Contrainte 4.10 i={i}"

    probleme.writeLP("prog_lin/pl_farkas_1.lp")


def pl_Farkas_2(n:int, vb: npt.NDArray, va: npt.NDArray, 
                entier: bool,
                m: int, aj: npt.NDArray, bj: npt.NDArray)-> None:
    '''
    Ecrit dans un fichier "pl_farkas_2.lp" 
    le programme lineaire qui donne le certificat de Farkas par la formule 4.9 pour le compromis (va - vb)
    (avec va qui domine vb du pdv de la dominance de Lorenz ou des OWAs robustes pour un ensemble de preferences I)
    en le decomposant en une somme de transferts (parties positive et negative)
    + des dons si version non restreinte
    + des congruences. 
    
    Programme lineaire de la formule 4.9 (page 83).

    Parametres
    ----------
        n: nombre de dimensions / d'agents
        vb: vecteur domine
        va: vecteur dominant 
        entier: vrai si les variables sont entieres, faux si reelles
        m: nombre de preferences donnees par l'utilisateur
        aj: liste des vecteurs dominants (preferences utilisateurs)
        bj: liste des vecteurs domines (preferences utilisateurs)
    '''

    # CREATION DU PROBLEME
    probleme = pulp.LpProblem("", pulp.LpMinimize)

    # VARIABLES

    variables: dict = dict()
    cat: str = "Integer" if entier else "Continuous"
        
    for j in range(m):
        # (lambda_j) : valeur du coefficient associe a la congruence avec la j-eme comparaison
        variables[f"lambda_{j}"] = pulp.LpVariable(f"lambda_{j}", lowBound=0, cat="Continuous") #lamba_j, >= 0

    for i in range(n):
        # (u_i) : quantite de richesse recue par l'agent i grace a un don
        variables[f"u_{i}"] = pulp.LpVariable(f"u_{i}", lowBound=0, cat=cat) #u_i 

       # (vp_i) : quantite de richesse recue par l'agent i grace a un transfert redistributif
        variables[f"vp_{i}"] = pulp.LpVariable(f"vp_{i}", lowBound=0, cat=cat) #vp_i 

        # (vn_i) : quantite de richesse donnee par l'agent i grace a un transfert redistributif
        variables[f"vn_{i}"] = pulp.LpVariable(f"vn_{i}", lowBound=0, cat=cat) #vn_i

    # OBJECTIF 

    probleme += 0, "Objectif"

    # CONTRAINTES 

    # (4.9a) (Formule du certificat de Farkas)
    for i in range(n):
        probleme += va[i] - vb[i] == variables[f"u_{i}"] + variables[f"vp_{i}"] - variables[f"vn_{i}"] + pulp.lpSum((aj[j][i] - bj[j][i])* variables[f"lambda_{j}"] for j in range(m)), f"Contrainte 4.9a i={i}"

    # (4.9b) (Quantite globale de richesse recue = quantite globale de richesse donnee)
    probleme += pulp.lpSum(variables[f"vp_{i}"] - variables[f"vn_{i}"] for i in range(n)) == 0, f"Contrainte 4.9b i={i}"
    
    # (4.9c) (Quantité globale de richesse reçue >= quantité globale de richesse donnee)
    for i in range(n-1):
        probleme += pulp.lpSum(variables[f"vp_{j}"] - variables[f"vn_{j}"] for j in range(i)) >= 0, f"Contrainte 4.9c i={i}"

    probleme.writeLP("prog_lin/pl_farkas_2.lp")


def pl_Farkas_optimal(n: int, vb: npt.NDArray, va: npt.NDArray,
                      entier: bool,
                      m: int, aj: npt.NDArray, bj: npt.NDArray)-> None: 
    ''' 
    Ecrit dans un fichier "pl_farkas_opt.lp" 
    le programme lineaire qui donne le certificat de Farkas optimal pour le compromis (va - vb)
    (avec va qui domine vb du pdv de la dominance de Lorenz ou des OWAs robustes pour un ensemble de preferences I)
    en le decomposant en des transferts redistributifs 
    + des dons si version non restreinte
    + des congruences. 
    
    Programme lineaire de la figure 4.5 (page 92).

    Parametres
    ----------
        n: nombre de dimensions / d'agents
        vb: vecteur domine
        va: vecteur dominant
        entier: vrai si les variables sont entieres, faux si reelles  
        m: nombre de preferences donnees par l'utilisateur    
        aj: liste des vecteurs dominants (preferences utilisateurs)
        bj: liste des vecteurs domines (preferences utilisateurs)
        
    '''
    # CREATION DU PROBLEME
    probleme = pulp.LpProblem("", pulp.LpMinimize)

    # VARIABLES 

    variables: dict = dict()
    cat: str = "Integer" if entier else "Continuous"

    for i in range(n):
        # (u_i) : quantite de richesse recue par l'agent i grace a un don
        variables[f"u_{i}"] = pulp.LpVariable(f"u_{i}", lowBound=0, cat=cat) #u_i

    # (g) = 1 si un don est effectue
    variables["g"] = pulp.LpVariable("g", lowBound=0, cat="Binary") #g, 0 ou 1
        
    for i in range(n-1):
        for j in range(i+1, n):
            # (tau_j_i) : quantite de richesse transferee de j a i 
            variables[f"tau_{j}_{i}"] = pulp.LpVariable(f"tau_{j}_{i}", lowBound=0, cat=cat) #tau_j_i

            # (t_j_i) = 1 s'il y a un transfert redistributif de j a i effectue 
            variables[f"t_{j}_{i}"] = pulp.LpVariable(f"t_{j}_{i}", lowBound=0, cat="Binary") #t_j_i, 0 ou 1
                
    for j in range(m):
        # (lambda_j) : valeur du coefficient associe a la congruence avec la j-eme comparaison
        variables[f"lambda_{j}"] = pulp.LpVariable(f"lambda_{j}", lowBound=0, cat="Continuous")

        # (pi_j) = 1 s'il y a une congruence avec la j-eme comparaison effectuee
        variables[f"pi_{j}"] = pulp.LpVariable(f"pi_{j}", lowBound=0, cat="Binary") #pi_j, 0 ou 1
    
    # FONCTION OBJECTIF

    probleme += pulp.lpSum(variables[f"pi_{j}"] for j in range(m)) + variables["g"] + pulp.lpSum(variables[f"t_{j}_{i}"] for i in range(n-1) for j in range(i+1, n)), "OBJECTIF"

    # CONTRAINTES 
        
    for i in range(n):
        # (4.19b) (Formule du certificat de Farkas)
        probleme += va[i] - vb[i] == variables[f"u_{i}"] + pulp.lpSum(variables[f"tau_{j}_{i}"] for j in range(i+1, n)) - pulp.lpSum(variables[f"tau_{i}_{h}"] for h in range(i)) + pulp.lpSum((aj[j][i] - bj[j][i])* variables[f"lambda_{j}"] for j in range(m)), f"Contrainte 4.19b {i}"

    M1: float = np.sum(va) + np.sum(vb) # borne superieure pour les quantites a redistribuer
    for i in range(n-1):
        for j in range(i+1, n):
            # (4.19c) (Quantite a recevoir d'un transfert limitee a la quantite de richesse totale disponible & t_j_i = 0 => v = 0) 
            probleme += M1 * variables[f"t_{j}_{i}"] - variables[f"tau_{j}_{i}"] >= 0, f"Contrainte 4.19c j={j},i={i}"

    # (4.19d) (Quantite a recevoir d'un don limitee a la quantite de richesse totale disponible & g = 0 => v = 0) 
    probleme += M1 * variables["g"] - pulp.lpSum(variables[f"u_{i}"] for i in range(n)) >= 0, "Contrainte 4.19d"
        
    for j in range(m):
        # (4.19e) (Quantite a recevoir d'une congruence quasi illimitee & lambda_j = 0 => v = 0) 
        probleme += M2 * variables[f"pi_{j}"] - variables[f"lambda_{j}"] >= 0, f"Contrainte 4.19e j={j}"

    probleme.writeLP("prog_lin/pl_farkas_opt.lp")

# Heuristiques

def pl_pi_Lorenz(n: int,  vb: npt.NDArray, va: npt.NDArray, 
                 entier: bool,
                 m: int, lambdas: npt.NDArray, aj: npt.NDArray, bj: npt.NDArray)-> None:
    '''
    Ecrit dans un fichier "pl_pi_lorenz.lp" 
    le programme lineaire qui donne le schema ATX pour passer du vecteur vb au vecteur va 
    (avec va qui domine vb du pdv de la dominance de Lorenz ou des OWAs robustes pour un ensemble de preferences I)
    en procedant a des alternances entre des blocs de transferts redistributifs/dons et des congruences. 

    Programme lineaire F.3 (page 214)

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
    '''
    l: int = 2*m + 2 # nombre d'etapes
    K1: list = [k for k in range(0, l-1, 2)] # dons ou transferts
    K0: list = [k for k in range(1, l-2, 2)] # congruences

    # CREATION DU PROBLEME
    probleme = pulp.LpProblem("", pulp.LpMinimize)

    # VARIABLES 

    variables: dict = dict()
    cat: str = "Integer" if entier else "Continuous"

    for k in range(l): 
        for i in range(n):
            # (x_k_i) vecteur de distribution a l'etape k
            variables[f"x_{k}_{i}"] = pulp.LpVariable(f"x_{k}_{i}", lowBound=0, cat=cat) #x_k_i 
    
    for k in K1: 
        # (beta_k) = 1 s'il y a une dominance de Lorenz a l'etape k
        variables[f"beta_{k}"] = pulp.LpVariable(f"beta_{k}", lowBound=0, cat="Binary") #beta_k, 0 ou 1

        for i in range(n):
            # (vp_k_i) : quantite de richesse recue par l'agent i grace a un transfert redistributif a l'etape k
            variables[f"vp_{k}_{i}"] = pulp.LpVariable(f"vp_{k}_{i}", lowBound=0, cat=cat) #vp_k_i   

            # (vn_k_i) : quantite de richesse donnee par l'agent i grace a un transfert redistributif a l'etape k
            variables[f"vn_{k}_{i}"] = pulp.LpVariable(f"vn_{k}_{i}", lowBound=0, cat=cat) #vn_k_i 

            # (u_k_i) : quantite de richesse recue par l'agent i grace a un don a l'etape k
            variables[f"u_{k}_{i}"] = pulp.LpVariable(f"u_{k}_{i}", lowBound=0, cat=cat) #u_k_i 

    for k in K0:
        for j in range(m):
            # (alpha_k_j) = 1 s'il y a une congruence avec la j-eme comparaison effectuee a l'etape k
            variables[f"alpha_{k}_{j}"] = pulp.LpVariable(f"alpha_{k}_{j}", lowBound=0, cat="Binary") # alpha_k_j, 0 ou 1

    # CONTRAINTES
    
    for i in range(n):
        # (F.15) (vb est le vecteur de depart)
        probleme += variables[f"x_0_{i}"] == vb[i], f"Contrainte F.15 i={i}"

        # (F.16) (va est le vecteur a atteindre)
        probleme += variables[f"x_{l-1}_{i}"] == va[i], f"Contrainte F.16 i={i}"        
        
    for i in range(n-1):
        for k in range(1, l-1):
            # (F.17) (Conserver l'ordre sur les coordonnees des vecteurs x)
            probleme += variables[f"x_{k}_{i}"] <= variables[f"x_{k}_{i+1}"], f"Contrainte F.17 k={k},i={i}"
    
    for i in range(n):
        for k in K1:
            # (F.18) (La valeur de la coordonnee i d'un vecteur x a l'etape k+1 est mise a jour avec la quantite de richesse recue (dont don et congruences) et la quantite de richesse donnee (dont congruences) a l'etape k)            
            probleme += variables[f"x_{k+1}_{i}"] == variables[f"x_{k}_{i}"] + variables[f"u_{k}_{i}"] + variables[f"vp_{k}_{i}"] - variables[f"vn_{k}_{i}"], f"Contrainte F.18 k={k},i={i}"

    M1: float = np.sum(va) + np.sum(vb) # borne superieure pour les quantites a redistribuer
    for k in K1:
        # (F.19) (Quantite globale de richesse recue = quantite globale de richesse donnee)
        probleme += pulp.lpSum(variables[f"vp_{k}_{i}"] - variables[f"vn_{k}_{i}"] for i in range(n)) == 0, f"Contrainte F.19 k={k}"

        # (F.21) (Quantite a donner d'un don et d'un transfert limitee a la quantite de richesse totale disponible & recue = 0 => u = 0)
        probleme += M1 * variables[f"beta_{k}"] - pulp.lpSum(variables[f"u_{k}_{i}"] + variables[f"vp_{k}_{i}"] for i in range(n)) >= 0, f"Contrainte F.21 k={k}"
        
        for i in range(n-1):
            # (F.20) (Quantite globale de richesse recue >= quantite globale de richesse donnee)
            probleme += pulp.lpSum(variables[f"vp_{k}_{j}"] - variables[f"vn_{k}_{j}"] for j in range(i)) >= 0, f"Contrainte F.20 k={k},i={i}"
  
    for i in range(n):
        for k in K0:
            # (F.22) (La valeur de la coordonnee i d'un vecteur x a l'etape k+1 est mise a jour avec la quantite de richesse recue (dont don) et la quantite de richesse donnee a l'etape k de K0)
            probleme += variables[f"x_{k+1}_{i}"] == variables[f"x_{k}_{i}"] + pulp.lpSum(variables[f"alpha_{k}_{j}"] * lambdas[j] * (aj[j][i] - bj[j][i]) for j in range(m)), f"Contrainte F.22 k={k},i={i}"

    for k in K0:
        # (F.23) (Il n'y a qu'une dominance de Lorenz par etape de K1) 
        probleme += pulp.lpSum(variables[f"alpha_{k}_{j}"] for j in range(m)) == 1 , f"Contrainte F.23 k={k}"
    
    for j in range(m):
        # (F.24) (Il n'y a qu'une congruence au maximum par etape de K0) 
        probleme += pulp.lpSum(variables[f"alpha_{k}_{j}"] for k in K0) == 1, f"Contrainte F.24 j={j}"
    
    probleme.writeLP("prog_lin/pl_pi_lorenz.lp")
