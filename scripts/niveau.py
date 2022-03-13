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

    def __init__(self, jeu, **kwargs):
        self.niveau01 = load_texture('niveau01')
        self.niveau02 = load_texture('niveau02')
        self.niveau03 = load_texture('niveau03')
        self.niveau04 = load_texture('niveau04')
        self.niveau05 = load_texture('niveau05')
        self.niveau06 = load_texture('niveau06')
        self.thème = {
            'sous_terrain': ([['stone_0', 'stone_1', 'stone_2', 'stone_3', 'stone_4'],
                              ['terre_0', 'terre_1', 'terre_2',
                                  'terre_3', 'terre_4'],
                              ['village_0', 'village_1', 'village_2']], 'cube'),

            'bambou': ([['bamboo_holder_0', 'bamboo_holder_1', 'bamboo_holder_2', 'bamboo_holder_3', 'bamboo_holder_4'],
                        ['bamboo_ground_0', 'bamboo_ground_1', 'bamboo_ground_2',
                            'bamboo_ground_3', 'bamboo_ground_4'],
                        ['bamboo_texture_0', 'bamboo_texture_1']], 'bamboo_model'),

            'ville': ([['concrete_rough_0', 'concrete_rough_1', 'concrete_rough_2', 'concrete_rough_3', 'concrete_rough_4'],
                       ['concrete_0', 'concrete_1', 'concrete_2',
                           'concrete_3', 'concrete_4'],
                       ['rebar_0', 'rebar_1', 'rebar_2', 'rebar_3', 'rebar_4']], 'rebar_model')
        }
        self.hauteur_niveau = 0
        self.instance_jeu = jeu

    def generer_niveau(self, num):
        if num == 0:
            return [Entity(model='quad', scale=(100, 100,), color=color.yellow),
            Text(
                """La guerre civile chinoise décrit la lutte entre les nationalistes du Guomindang\n 
                et le Parti communiste chinois (PCC) pour le contrôle de la Chine.\n 
                Elle s’est terminée par la fuite de Jiang Jieshi vers Taïwan,\n
                la victoire à Mao Zedong et au PCC et la formation de la République populaire de Chine.""", background=True,x=-.7, y=.3)
            ]

        if num == 1:
            self.instance_jeu.music.jouer_music('gameplay')
            self.instance_jeu.lemmings_cap += 5
            self.instance_jeu.spawn_position = (-8, -4,)
            lvl = self.créer_niveau(
                self.niveau01, self.thème['sous_terrain'], 'cave')
            lvl.append(self.trophée(self.instance_jeu, position=(4, -3,)))
            lvl.append(self.pointes(self.instance_jeu, position=(0, -5,)))
            lvl.append(self.pointes(self.instance_jeu, position=(3, -5,)))
            return lvl

        elif num == 2:
            self.instance_jeu.lemmings_cap += 5
            self.instance_jeu.spawn_position = (0, 0,)
            lvl = self.créer_niveau(
                self.niveau02, self.thème['bambou'], 'Bamboo_Forest')
            lvl.append(self.trophée(self.instance_jeu, position=(57.5, -22,)))
            return lvl

        elif num == 3:
            self.instance_jeu.lemmings_cap += 5
            self.instance_jeu.spawn_position = (0, 0,)
            lvl = self.créer_niveau(
                self.niveau03, self.thème['sous_terrain'], 'The_Chinese_Village')
            lvl.append(self.trophée(self.instance_jeu, position=(37.5, -14,)))
            return lvl

        elif num == 4:
            self.instance_jeu.lemmings_cap += 5
            self.instance_jeu.spawn_position = (0, 0,)
            lvl = self.créer_niveau(
                self.niveau04, self.thème['ville'], 'basement')
            lvl.append(self.trophée(self.instance_jeu, position=(28, -24,)))
            return lvl

        elif num == 5:
            self.instance_jeu.lemmings_cap += 5
            self.instance_jeu.spawn_position = (0, 0,)
            lvl = self.créer_niveau(
                self.niveau05, self.thème['bambou'], 'Mica_dam')
            lvl.append(self.trophée(self.instance_jeu, position=(49, -11,)))
            return lvl

        elif num == 6:
            self.instance_jeu.lemmings_cap += 10
            self.instance_jeu.spawn_position = (0, 0,)
            lvl = self.créer_niveau(
                self.niveau06, self.thème['ville'], 'HK_Victoria_Harbour')
            lvl.append(self.trophée(self.instance_jeu, position=(130, -40,)))
            lvl.append(self.instance_jeu.char(
                self.instance_jeu, position=(20, -40,)))
            return lvl
        
        elif num == 7:
            self.instance_jeu.music.jouer_music('out')
            return []
        
        else:
            return []

    def créer_niveau(self, texture_niveau, thème=(['erreur', ['erreur'], ['erreur']], 'cube'), background='erreur'):
        # creation d'un niveau a partir d'une image
        self.hauteur_niveau = texture_niveau.height

        bornes = thème[0][0]
        principale = thème[0][1]
        secondaire = thème[0][2]
        secondaire_model = thème[1]
        fond = background
        décalage = 10
        couleur_encadrement = color.rgb(252, 234, 196)
        niveau_cadre = [Entity(enabled=False, position=(0, 0,))]

        for y in range(texture_niveau.height):
            for x in range(texture_niveau.width):
                if texture_niveau.get_pixel(x, y) == color.rgb(0, 0, 0):
                    niveau_cadre.append(Entity(model='cube', collider='box',
                                               position=(x, y,), origin=(
                                                   décalage, texture_niveau.height,), scale_z=2.5,
                                               texture=bornes[randint(0, len(bornes))-1]))
                elif texture_niveau.get_pixel(x, y) == color.rgb(100, 100, 100):
                    niveau_cadre.append(Entity(model='cube', collider='box',
                                               position=(x, y,), origin=(
                                                   décalage, texture_niveau.height,), scale_z=2,
                                               texture=principale[randint(0, len(principale))-1]))
                elif texture_niveau.get_pixel(x, y) == color.rgb(150, 150, 150):
                    niveau_cadre.append(Entity(model=secondaire_model,
                                               position=(x, y,), origin=(
                                                   décalage, texture_niveau.height,),
                                               texture=secondaire[randint(0, len(secondaire)-1)]))
        # Cadre autour du niveau
        niveau_cadre.extend([Entity(model='cube', texture=fond,
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
                                   scale=(1, texture_niveau.height+2, 10),
                                   position=(-décalage, -texture_niveau.height/2-.5)),
                            Entity(model='cube', color=couleur_encadrement,scale=(1, texture_niveau.height+2, 10),
                                   position=(texture_niveau.width-décalage, -texture_niveau.height/2-.5)),
                            Entity(model='plane', color=color.gray,
                                   scale=(1000, 1, 1000), rotation=(180),
                                   position=(0, -(texture_niveau.height*2.5)-1.5, 5)),
                            Entity(model='crt_model', texture='crt_texture', scale=(texture_niveau.width/1.2, texture_niveau.height*1.5, 20),
                                   position=((texture_niveau.width-2*décalage)/2, -texture_niveau.height, -5), rotation_y=180, double_sided=True),
                            Entity(model='clavier_model', color=couleur_encadrement,
                                   scale=(30, 30, 30),
                                   position=(0, -(texture_niveau.height*2.5), -20),rotation_y=180),
                            
                             ])
        return niveau_cadre

    class pointes(Entity):
        def __init__(self, jeu, **kwargs):
            super().__init__(**kwargs)
            self.instance_jeu = jeu
            self.model = 'pointes_model'
            self.collider = 'box'
            self.scale = (.5, .5, .5)
            self.enabled = True
            self.double_sided = True
            self.__dict__.update(kwargs)

        def update(self):
            ray = boxcast(self.world_position, self.up,
                          distance=self.scale_y, thickness=self.scale_x)
            if ray.entity in self.instance_jeu.lemmings_actif:
                self.instance_jeu.retire_lemming(ray.entity)

    class trophée(Entity):
        def __init__(self, jeu, **kwargs):
            super().__init__(**kwargs)
            self.instance_jeu = jeu
            self.model = 'trophee_model'
            self.collider = 'box'
            self.scale = (.5, .5, .5)
            self.enabled = True
            self.double_sided = True
            self.texture = 'trophee_texture'
            self.color = color.yellow
            self.__dict__.update(kwargs)

        def update(self):
            ray = boxcast(self.world_position, self.left,
                          distance=self.scale_y, thickness=self.scale_x)
            if ray.entity in self.instance_jeu.lemmings_actif:
                self.instance_jeu.gagner()
            if self in self.instance_jeu.scene_active:
                self.rotation_y += .5
