"""
Fichier Principal
Auteurs : Dyami Neu et Andy How

Projet Lemming en 3d et 2d

Ce projet est un jeu en 3d qui utilise la librairie Ursina.
Documentation: https://www.ursinaengine.org/documentation.html
Toutes licenses associes sont mentionnes dans le fichier texte 'credit.txt'
"""
from scripts.jeu_2d import Jeu_2d
from scripts.jeu_3d import Jeu_3d

def jeu3d():
    Jeu3 = Jeu_3d()
    Jeu3.demarrer()
    Jeu3.app.run()

def jeu2d():
    Jeu2 = Jeu_2d(10) 
    Jeu2.demarrer()

if __name__ == '__main__':
    rep = 0
    while True:    
        if rep == 2:
            jeu2d()
        elif rep == 3:
            jeu3d()
        else:
            rep = int(input('entrer 2 pour le jeu en 2d et 3 pour le jeu en 3d\nchoix: '))
