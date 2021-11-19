# -*- coding: utf-8 -*-
import numpy as np
import time
from random import shuffle

jeton = None  # token qui va permettre d'économiser du temps de calcul en gardant en mémoire un résultat


# définie un grille de morpion initialisée par défault avec que des None
class Morpion:
    def __init__(self, x=12, y=12, grille=None):
        if (grille is None) or grille.shape != (x, y):
            self.grille = np.full((x, y), None)
        else:
            self.grille = grille

    def __str__(self):
        msg = "     1  2  3  4  5  6  7  8  9  10 11 12\n    ------------------------------------\n"
        for i in range(self.grille.shape[0]):
            msg += str(i + 1)
            if (i + 1) < 10:
                msg += " "
            msg += " |"
            for j in range(self.grille.shape[1]):
                if self.grille[i][j] is None:
                    msg += " _ "
                else:
                    msg += " " + str(self.grille[i][j]) + " "
            msg += "\n"
        return msg

    def __repr__(self):
        return str(self)


# renvoie toutes les cases jouables, c'est à dire celle qui contiennent la valeur None
def cases_jouables(grille):
    cases = []
    for i in range(grille.shape[0]):
        for j in range(grille.shape[1]):
            if grille[i][j] is None:
                cases.append([i, j])
    return cases


# Renvoie une nouvelle grille ou modifie la grille en paramètre en rajoutant le coup spécifié
def applique_coup(grille, coup, modifier=False):
    if modifier:
        grille[coup[0]][coup[1]] = coup[2]
    copie_grille = np.copy(grille)
    copie_grille[coup[0]][coup[1]] = coup[2]
    return copie_grille


# Renvoie True si toutes les cases de la grille sont remplies (différent de None), False sinon
def grille_remplie(grille):
    for i in range(grille.shape[0]):
        for j in range(grille.shape[1]):
            if grille[i][j] is None:
                return False
    return True


# Vérifie si 4 pions consécutifs identiques sont présents sur une des colonnes de la grille, auquel cas la partie est
# terminée
def test_colonne(grille):
    global jeton
    for j in range(grille.shape[1]):
        for i in range(grille.shape[0] - 3):
            if grille[i][j] is not None and grille[i][j] == grille[i + 1][j] and grille[i][j] == grille[i + 2][j] \
                    and grille[i][j] == grille[i + 3][j]:
                jeton = grille[i][j]
                return True
    return False


# Vérifie si 4 pions consécutifs identiques sont présents sur une des lignes de la grille, auquel cas la partie est
# terminée
def test_ligne(grille):
    global jeton
    for i in range(grille.shape[0]):
        for j in range(grille.shape[1] - 3):
            if grille[i][j] is not None and grille[i][j] == grille[i][j + 1] and grille[i][j] == grille[i][j + 2] \
                    and grille[i][j] == grille[i][j + 3]:
                jeton = grille[i][j]
                return True
    return False


# Vérifie si 4 pions consécutifs identiques sont présents sur les deux diagonales de la grille, auquel cas la partie est
# terminée
def test_diagonale(grille):
    global jeton
    for i in range(grille.shape[0] - 3):
        for j in range(grille.shape[1] - 3):
            if grille[i][j] is not None and grille[i][j] == grille[i + 1][j + 1] \
                    and grille[i][j] == grille[i + 2][j + 2] and grille[i][j] == grille[i + 3][j + 3]:
                jeton = grille[i][j]
                return True
    return False


# Vérifie si la partie est terminée, c'est à dire un des cas suivants est vérifié :
# - la grille est entièrement remplie
# - 4 pions identiques consécutifs sont présents sur une ligne, une colonne ou une diagonale
def partie_terminee(grille):
    return grille_remplie(grille) or test_ligne(grille) or test_colonne(grille) or test_diagonale(grille) \
           or test_diagonale(np.rot90(grille))


# Renvoie True si la case spécifiée en paramètre possède un voisin (8 cases autour) du type ordinateur ou joueur
# Le paramètre ordinateur contient True dans le cas où l'on souhaite savoir si un des voisins de la case contient le
# symbole de l'ordinateur. False dans le cas du symbole du joueur
def a_un_voisin_joueur(grille, x, y, ordinateur):
    if ordinateur:
        symbole = symbole_ordinateur
    else:
        symbole = symbole_joueur
    if x + 1 < taille:
        if grille[x + 1][y] == symbole:
            return True
    if y + 1 < taille:
        if grille[x][y + 1] == symbole:
            return True
    if x + 1 < taille and y + 1 < taille:
        if grille[x + 1][y + 1] == symbole:
            return True
    if x - 1 >= 0:
        if grille[x - 1][y] == symbole:
            return True
    if y - 1 >= 0:
        if grille[x][y - 1] == symbole:
            return True
    if x - 1 >= 0 and y - 1 >= 0:
        if grille[x - 1][y - 1] == symbole:
            return True
    if x - 1 >= 0 and y + 1 < taille:
        if grille[x - 1][y + 1] == symbole:
            return True
    if y - 1 >= 0 and x + 1 < taille:
        if grille[x + 1][y - 1] == symbole:
            return True
    return False


# Renvoie les cases de la grille qui sont encore vides et "intéressantes". Une case "intéressante" est une case qui
# possède un voisin du type spécifié en paramètre (ordinateur / joueur)
def cases_jouables_interessantes(grille, ordinateur):
    tableau = cases_jouables(grille)
    res = []
    for coup in tableau:
        if a_un_voisin_joueur(grille, coup[0], coup[1], ordinateur):
            res.append(coup)
    shuffle(res)
    return res


# C'est la fonction "Utility". Elle va donner une note entre -1 et 1 de la grille qu'on lui envoie. Plus la note est
# proche de -1, plus la grille est à l'avantage du joueur. Plus la note est proche de 1, plus la grille est à l'avantage
# de l'ordinateur. Seulement 5 valeurs peuvent être renvoyé par la fonction :
# - Les valeurs 0.99 et -0.99 indiquent que l'ordinateur / le joueur possède sur la grille une suite de pions qui font
# qu'il gagnera forcément au prochain coup
# - Les valeurs 0.80 et -0.80 indiquent que l'ordinateur / le joueur aura une occasion de gagner au prochain coup si
# l'adversaire ne remplie pas la case gagnante
# - La valeur 0 indique que l'ordinateur et le joueur n'ont pas d'avantage particulier sur la grille
def evaluation_grille(grille):
    if jeton is not None:
        return notation[jeton]  # permet d'économiser du temps de calcul en récupérant les résultats obtenues avec la
                                # fonction partie_terminee utilisé dans la fonction minimax
    nb_coup_critique = 0
    cases_interessantes = cases_jouables_interessantes(grille, ordinateur_commence)
    if not ordinateur_commence:
        cases_interessantes += cases_jouables_interessantes(grille, True)
    for case in cases_interessantes:
        grille2 = applique_coup(grille, case + [symbole_ordinateur])
        if test_ligne(grille2) or test_colonne(grille2) or test_diagonale(grille2) or test_diagonale(np.rot90(grille2)):
            nb_coup_critique += 1
    if nb_coup_critique > 0:
        if nb_coup_critique >= 2:
            return 0.99
        else:
            return 0.80
    for case in cases_jouables_interessantes(grille, False):
        grille2 = applique_coup(grille, case + [symbole_joueur])
        if test_ligne(grille2) or test_colonne(grille2) or test_diagonale(grille2) or test_diagonale(np.rot90(grille2)):
            nb_coup_critique += 1
    if nb_coup_critique > 0:
        if nb_coup_critique >= 2:
            return -0.99
        else:
            return -0.80
    return 0


# C'est la fonction qui réalise le minimax et l'élagage alpha-beta.
def minimax(grille, ordinateur, alpha, beta, profondeur):
    global jeton
    jeton = None
    if partie_terminee(grille) or profondeur < 1:  # on a atteint la feuille de l'arbre
        return evaluation_grille(grille)
    elif ordinateur:  # maximisation du coup de l'ordinateur
        max_evaluation = - np.Inf
        cases_interessantes = cases_jouables_interessantes(grille, ordinateur_commence)
        if not ordinateur_commence:
            cases_interessantes += cases_jouables_interessantes(grille, True)
        for coup in cases_interessantes:
            coup.append(symbole_ordinateur)
            evaluation = minimax(applique_coup(grille, coup), False, alpha, beta, profondeur - 1)
            max_evaluation = max(max_evaluation, evaluation)
            if max_evaluation >= beta or max_evaluation >= 1:  # élagage
                break
            alpha = max(alpha, max_evaluation)
        return max_evaluation
    else:  # minisation du coup du joueur
        min_evaluation = np.Inf
        for coup in cases_jouables_interessantes(grille, False):
            coup.append(symbole_joueur)
            evaluation = minimax(applique_coup(grille, coup), True, alpha, beta, profondeur - 1)
            min_evaluation = min(min_evaluation, evaluation)
            if min_evaluation <= alpha or min_evaluation <= -1:  # élagage
                break
            beta = min(beta, min_evaluation)
        return min_evaluation


# commence la partie
def jeu(mp, tour_ordinateur=True):
    print("\nLe jeu commence ! \\(^ヮ^)/\n~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print(mp)
    while not partie_terminee(mp.grille):
        if tour_ordinateur:  # coup de l'ordinateur
            t = time.time()
            coup = []
            if len(cases_jouables(mp.grille)) == taille * taille:  # cas où l'ordinateur joue le premier coup
                coup = [taille // 2, taille // 2]
            elif len(cases_jouables(mp.grille)) == taille * taille - 1:  # cas où l'ordinateur joue le deuxième coup
                for i in range(taille):
                    for j in range(taille):
                        if mp.grille[i, j] is not None:
                            if i != taille - 1:
                                coup = [i + 1, j]
                            else:
                                coup = [i - 1, j]
            else:
                compteur = 0
                alpha = - np.Inf
                beta = np.Inf
                valeur = - np.Inf
                cases_interessantes = cases_jouables_interessantes(mp.grille, ordinateur_commence)
                # dans le cas où le joueur commence, les cases jouables intéressantes sont toutes les cases adjacentes
                # aux pions déjà en jeu
                if not ordinateur_commence:
                    cases_interessantes += cases_jouables_interessantes(mp.grille, True)
                profondeur_minimax = 1
                # print(len(cases_interessantes))
                # on adapte la profondeur en fonction du nombre de cases jouables interessantes
                if len(cases_interessantes) <= 9:
                    profondeur_minimax = 3
                # on lance le minimax en commencant par une maximisation du coup de l'ordinateur
                for i in cases_interessantes:
                    minimax_valeur = minimax(applique_coup(mp.grille, i + [symbole_ordinateur]), False,
                                             alpha, beta, profondeur_minimax)
                    if valeur <= minimax_valeur:
                        # print("minimax : ", minimax_valeur, i)
                        valeur = minimax_valeur
                        coup = i
                    compteur += 1
                    temps_par_coup = (time.time() - t) / compteur  # vérification que l'on dépasse pas les 10 secondes
                    if temps_par_coup * (compteur + 1.5) > 10:
                        break
                    if valeur == 1:  # élagage dans le cas où l'on a déjà atteint une évaluation maximum (1)
                        break
            print("\nMon coup (⌐■_■) : [", str(coup[1] + 1) + ", " + str(coup[0] + 1), "]\n")
            applique_coup(mp.grille, coup + [symbole_ordinateur], True)
            print(mp)
            tour_ordinateur = not tour_ordinateur
            print("Temps de réflexion : ", time.time() - t)
        else:  # coup du joueur
            print("\nA toi de jouer ヽ(♡‿♡)ノ \n")
            y = int(input("Ta colonne stp (⌒_⌒;) :")) - 1
            x = int(input("Ta ligne maintenant (つ✧ω✧)つ :")) - 1
            if mp.grille[x, y] is None:
                mp.grille = applique_coup(mp.grille, [x, y, symbole_joueur])
                print('\n')
                print(mp)
                tour_ordinateur = not tour_ordinateur
            else:
                print("\nTu n'as pas le droit tricheur ((╬◣﹏◢)) rejoue!")
    if evaluation_grille(mp.grille) == 1:
        print("\nJ'ai gagné !!! 	＼(٥⁀▽⁀ )／ ")
    if evaluation_grille(mp.grille) == -1:
        print("\nTu as gagné 	(╯︵╰,)")


if __name__ == '__main__':
    if input("L'ordinateur commence ? (Y/N)") == "Y":
        ordinateur_commence = True
    else:
        ordinateur_commence = False
    symbole_joueur = "O"
    symbole_ordinateur = "X"
    notation = {symbole_ordinateur: 1, symbole_joueur: -1}  # permet le calcul des scores dans la fonction d'évaluation
    taille = 12
    morpion = Morpion(x=taille, y=taille)
    jeu(morpion, ordinateur_commence)
