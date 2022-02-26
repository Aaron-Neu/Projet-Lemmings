"""
Auteurs : Dyami Neu et Andy How

Environnement pour le Projet Lemming en 3d
"""

from random import randint
from ursina import *


class Niveau():
    """
    Regroupement de classes qui sont utiliser pour construire les niveaux
    """

    def __init__(self, **kwargs):
        self.niveau00 = load_texture('niveau00')
        self.niveau01 = load_texture('niveau01')
        self.niveau02 = load_texture('niveau02')
        self.niveau03 = load_texture('niveau03')
        self.thème = {
            'bambou': ['grey_stone', ['Bamboo_Texture', 'Bamboo'], ['Bamboo_color', 'Iphone_Bamboo'], 'Bamboo_Forest'],
            'ville': ['concrete', ['Cracked_Asphalt', 'foot_Steel'], ['rebar', 'Shingles'], 'Macau']
        }
        self.hauteur_niveau = 0

    def generer_niveau(self, num):
        if num == 1:
            return self.créer_niveau(self.niveau01, self.thème['ville'])
        if num == 2:
            return self.créer_niveau(self.niveau02, self.thème['bambou'])
        elif num == 3:
            return self.créer_niveau(self.niveau03)
        else:
            return self.créer_niveau(self.niveau00, self.thème['bambou'])

    def créer_niveau(self, texture_niveau, thème=['erreur', ['erreur'], ['erreur'], 'erreur']):
        # creation d'un niveau a partir d'une image
        self.hauteur_niveau = texture_niveau.height

        bornes = thème[0]
        principale = thème[1]
        secondaire = thème[2]
        fond = thème[3]
        décalage = 10
        couleur_encadrement = color.rgb(252, 234, 196)
        niveau_cadre = [Entity(enabled=False, position=(-1, -1, -1))]

        for y in range(texture_niveau.height):
            for x in range(texture_niveau.width):
                if texture_niveau.get_pixel(x, y) == color.rgb(0, 0, 0):
                    niveau_cadre.append(Entity(model='cube', collider='box',
                                               position=(x, y,), origin=(
                                                   décalage, texture_niveau.height,), scale_z=3,
                                               texture=bornes))
                elif texture_niveau.get_pixel(x, y) == color.rgb(100, 100, 100):
                    niveau_cadre.append(Entity(model='cube', collider='box',
                                               position=(x, y,), origin=(
                                                   décalage, texture_niveau.height,), scale_z=2,
                                               texture=principale[randint(0, len(principale))-1]))
                elif texture_niveau.get_pixel(x, y) == color.rgb(150, 150, 150):
                    niveau_cadre.append(Entity(model='cube', collider='box',
                                               position=(x, y, -.9), origin=(
                                                   décalage, texture_niveau.height,), scale_z=.2,
                                               texture=secondaire[randint(0, len(secondaire)-1)]))
                    niveau_cadre.append(Entity(model='cube', collider='box',
                                               position=(x, y, .9), origin=(
                                                   décalage, texture_niveau.height,), scale_z=.2,
                                               texture=secondaire[randint(0, len(secondaire)-1)]))

        niveau_cadre.extend([Entity(model='plane', color=color.gray,
                                    scale=(1000, 1, 1000), rotation=(180),
                                    position=(0, -(texture_niveau.height)-1.5, 5)),
                            Entity(model='cube', texture=fond,
                                   scale=(texture_niveau.width-1,
                                          texture_niveau.height+1, 1),
                                   position=((texture_niveau.width-2*décalage)/2, -(texture_niveau.height)/2-.5, 5)),
                             Entity(model='cube', color=couleur_encadrement,
                                          scale=(texture_niveau.width,
                                                 texture_niveau.height+2, 1),
                                          position=((texture_niveau.width-2*décalage)/2, -(texture_niveau.height)/2-.5, 5.5)),
                             Entity(model='cube', color=couleur_encadrement.tint(-.05),
                                          scale=(texture_niveau.width/1.5,
                                                 texture_niveau.height/2, 4),
                                          position=((texture_niveau.width-2*décalage)/2, -(texture_niveau.height)/2-.5, 7)),
                             Entity(model='cube', color=color.rgb(15, 243, 60, 20),
                                          scale=(texture_niveau.width,
                                                 texture_niveau.height+1, 1),
                                          position=((texture_niveau.width-2*décalage)/2, -(texture_niveau.height)/2-.5, -5)),
                             Entity(model='cube', color=couleur_encadrement,
                                          scale=(texture_niveau.width, 1, 10),
                                          position=((texture_niveau.width-2*décalage)/2, -texture_niveau.height-1)),
                             Entity(model='cube', color=couleur_encadrement,
                                          scale=(texture_niveau.width, 1, 10),
                                    position=((texture_niveau.width-2*décalage)/2, 0)),
                            Entity(model='cube', color=couleur_encadrement,
                                   scale=(
                                       1, texture_niveau.height+2, 10),
                                   position=(-décalage, -texture_niveau.height/2-.5)),
                            Entity(model='cube', color=couleur_encadrement,
                                   scale=(
                                       1, texture_niveau.height+2, 10),
                                   position=(texture_niveau.width-décalage, -texture_niveau.height/2-.5))

                             ])
        return niveau_cadre

    class Death_block(Entity):
        def __init__(self, jeu, **kwargs):
            super().__init__(**kwargs)
            self.instance_jeu = jeu
            self.model = 'cube'
            self.collider = 'box'
            self.enabled = True
            self.double_sided = True
            self.color = color.red
            self.__dict__.update(kwargs)

        def update(self):
            ray = boxcast(origin=self.world_position, thickness=self.scale)
            if ray.entity in self.instance_jeu.lemmings_actif:
                self.instance_jeu.removelemming(ray.entity)

    class Win_block(Entity):
        def __init__(self, jeu, **kwargs):
            super().__init__(**kwargs)
            self.instance_jeu = jeu
            self.name = 'Win_block'
            self.model = 'cube'
            self.collider = 'box'
            self.enabled = True
            self.double_sided = True
            self.color = color.yellow
            self.__dict__.update(kwargs)

        def update(self):
            ray = boxcast(origin=self.world_position, thickness=self.scale)
            if ray.entity in self.instance_jeu.lemmings_actif:
                self.instance_jeu.win()
