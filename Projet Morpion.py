# -*- coding: utf-8 -*-
"""
Created on Wed May  5 10:33:29 2021

@author: Marius
"""
import numpy as np
import time
from random import shuffle

jeton = None


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


def cases_jouables(grille):
    cases = []
    for i in range(grille.shape[0]):
        for j in range(grille.shape[1]):
            if grille[i][j] is None:
                cases.append([i, j])
    return cases


def applique_coup(grille, coup, modifier=False):
    if modifier:
        grille[coup[0]][coup[1]] = coup[2]
    copie_grille = np.copy(grille)
    copie_grille[coup[0]][coup[1]] = coup[2]
    return copie_grille


def grille_remplie(grille):
    for i in range(grille.shape[0]):
        for j in range(grille.shape[1]):
            if grille[i][j] is None:
                return False
    return True


def test_colonne(grille):
    global jeton
    for j in range(grille.shape[1]):
        for i in range(grille.shape[0] - 3):
            if grille[i][j] is not None and grille[i][j] == grille[i + 1][j] and grille[i][j] == grille[i + 2][j] \
                    and grille[i][j] == grille[i + 3][j]:
                jeton = grille[i][j]
                return True
    return False


def test_ligne(grille):
    global jeton
    for i in range(grille.shape[0]):
        for j in range(grille.shape[1] - 3):
            if grille[i][j] is not None and grille[i][j] == grille[i][j + 1] and grille[i][j] == grille[i][j + 2] \
                    and grille[i][j] == grille[i][j + 3]:
                jeton = grille[i][j]
                return True
    return False


def test_diagonale(grille):
    global jeton
    for i in range(grille.shape[0] - 3):
        for j in range(grille.shape[1] - 3):
            if grille[i][j] is not None and grille[i][j] == grille[i + 1][j + 1] \
                    and grille[i][j] == grille[i + 2][j + 2] and grille[i][j] == grille[i + 3][j + 3]:
                jeton = grille[i][j]
                return True
    return False


def partie_terminee(grille):
    return grille_remplie(grille) or test_ligne(grille) or test_colonne(grille) or test_diagonale(grille) \
           or test_diagonale(np.rot90(grille))


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


def cases_jouables_interessantes(grille, ordinateur):
    tableau = cases_jouables(grille)
    res = []
    for coup in tableau:
        if a_un_voisin_joueur(grille, coup[0], coup[1], ordinateur):
            res.append(coup)
    shuffle(res)
    return res


def evaluation_grille(grille):
    if jeton is not None:
        return notation[jeton]
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


def minimax(grille, ordinateur, alpha, beta, profondeur):
    global jeton
    jeton = None
    if partie_terminee(grille) or profondeur < 1:
        return evaluation_grille(grille)
    elif ordinateur:
        max_evaluation = - np.Inf
        cases_interessantes = cases_jouables_interessantes(grille, ordinateur_commence)
        if not ordinateur_commence:
            cases_interessantes += cases_jouables_interessantes(grille, True)
        for coup in cases_interessantes:
            coup.append(symbole_ordinateur)
            evaluation = minimax(applique_coup(grille, coup), False, alpha, beta, profondeur - 1)
            max_evaluation = max(max_evaluation, evaluation)
            if max_evaluation >= beta or max_evaluation >= 1:
                break
            alpha = max(alpha, max_evaluation)
        return max_evaluation
    else:
        min_evaluation = np.Inf
        for coup in cases_jouables_interessantes(grille, False):
            coup.append(symbole_joueur)
            evaluation = minimax(applique_coup(grille, coup), True, alpha, beta, profondeur - 1)
            min_evaluation = min(min_evaluation, evaluation)
            if min_evaluation <= alpha or min_evaluation <= -1:
                break
            beta = min(beta, min_evaluation)
        return min_evaluation


# commence la partie
def jeu(mp, tour_ordinateur=True):
    print("\nLe jeu commence ! \\(^ヮ^)/\n~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print(mp)
    while not partie_terminee(mp.grille):
        if tour_ordinateur:
            t = time.time()
            coup = []
            if len(cases_jouables(mp.grille)) == taille * taille:
                coup = [taille // 2, taille // 2]
            elif len(cases_jouables(mp.grille)) == taille * taille - 1:
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
                if not ordinateur_commence:
                    cases_interessantes += cases_jouables_interessantes(mp.grille, True)
                profondeur_minimax = 1
                print(len(cases_interessantes))
                if len(cases_interessantes) <= 9:
                    profondeur_minimax = 3
                for i in cases_interessantes:
                    minimax_valeur = minimax(applique_coup(mp.grille, i + [symbole_ordinateur]), False,
                                             alpha, beta, profondeur_minimax)
                    if valeur <= minimax_valeur:
                        print("minimax : ", minimax_valeur, i)
                        valeur = minimax_valeur
                        coup = i
                    compteur += 1
                    temps_par_coup = (time.time() - t) / compteur
                    if temps_par_coup * (compteur + 1.5) > 10:
                        break
                    if valeur == 1:
                        break
            print("\nMon coup (⌐■_■) : [", str(coup[1] + 1) + ", " + str(coup[0] + 1), "]\n")
            applique_coup(mp.grille, coup + [symbole_ordinateur], True)
            print(mp)
            tour_ordinateur = not tour_ordinateur
            print("Temps de réflexion : ", time.time() - t)
        else:
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
    notation = {symbole_ordinateur: 1, symbole_joueur: -1}
    taille = 12
    morpion = Morpion(x=taille, y=taille)
    jeu(morpion, ordinateur_commence)
