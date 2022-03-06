"""
Auteurs : Dyami Neu et Andy How

Environnement pour le Projet Lemming en 3d
"""
from ursina import *

from scripts.camera import Camera
from scripts.entite import Lemming, Char
from scripts.niveau import Niveau
from scripts.son import Son


class Jeu_3d(Entity):
    # configure la fenêtre d'affichage
    fullscreen = False
    development_mode = True
    title = 'lemmings 2: Electric Boogaloo'
    borderless = False
    forced_aspect_ratio = 1.778
    app = Ursina(fullscreen=fullscreen, development_mode=development_mode,
                 title=title, borderless=borderless, forced_aspect_ratio=forced_aspect_ratio)
    window.fps_counter.enabled = True
    window.icon = 'icon.ico'

    """
    Class principale, qui gère le jeu
    """

    def __init__(self):
        super().__init__()
        self.music = Son()
        self.niveaux = Niveau(self)
        self.camera = Camera(self)
        self.char = Char

        self.scene_active = []
        self.num_niveaux = 0
        self.vue_menu = True

        self.lemmings = {}
        self.lemmings_actif = []
        self.spawn_position = (0, 0,)
        self.lemmings_cap = 0
        self.croix_muet = Entity(model='cube', texture='mute', scale_x=.75, scale_y=.75,
                                 x=-6.6, y=-3.5, enabled=False, eternal=False)
        self.panneau_aide = WindowPanel(
            position=(0, 0),
            title='Aide',
            content=(
                Text('utiliser "+" pour ajouter un lemming\n'),
                Text('utiliser "espace" pour faire sauter\n le(s) lemming(s)'),
                Text('utiliser "shift" pour faire précipité\n le(s) lemming(s)'),
                Text('utiliser la souris pour naviguer\n'),
                Text('utiliser "shift" + "f" pour recentrer\n la caméra')
            ),
            popup=True,
            enabled=False
        )

    def demarrer(self):
        # le menu d'entre du jeu
        [destroy(self.scene_active.pop())
         for _ in range(len(self.scene_active))]
        [self.retire_lemming(x)
         for x in self.lemmings_actif]
        self.num_niveaux = 0

        self.music.jouer_music('start')
        Camera.disable(self.camera)
        lemmings_start = Entity(model='quad', texture='lemmings_start.mp4',
                                scale=(14.5, 8.2))
        boutton_demarrer = Button(parent=camera.ui, model='cube',
                                  x=-.33, y=.024, scale=(.325, .1, 1))
        boutton_quitter = Button(parent=camera.ui, model='cube',
                                 x=.33, y=.024, scale=(.325, .1, 1))
        boutton_muet = Button(parent=camera.ui, model='quad', scale_x=.095, scale_y=.095, x=-.825,
                              y=-.44)
        boutton_muet.on_click = self.muet
        boutton_demarrer.on_click = self.jeu
        boutton_quitter.on_clic = application.quit
        [self.scene_active.append(x) for x in [
            lemmings_start, boutton_demarrer, boutton_quitter, boutton_muet, self.croix_muet]]

    def muet(self):
        if not self.music.muet:
            self.music.set_muet()
            self.croix_muet.enabled = True
        else:
            self.music.set_unmuet()
            self.croix_muet.enabled = False

    def jeu(self):
        self.vue_menu = False
        [destroy(self.scene_active.pop())
         for _ in range(len(self.scene_active))]
        [self.retire_lemming(x)
         for x in self.lemmings_actif]

        Camera.enable(self.camera)

        help_tip = Text(
            text="maintenez 'tab' pour obtenir de l'aide", origin=(0, 0), y=-.45, color=color.black)
        sky = Sky()
        [self.scene_active.append(x) for x in [
            help_tip, sky]]

        lvl = self.niveaux.generer_niveau(self.num_niveaux)
        self.camera.hauteur_niveau = self.niveaux.hauteur_niveau
        [self.scene_active.append(x) for x in lvl]
        print(lvl)

        if self.num_niveaux == 0:
            invoke(self.gagner, delay=3)

        if self.num_niveaux == 7:
            destroy(help_tip)
            Camera.disable(self.camera)

            with open('credits.txt', 'r') as file:
                credits_ = file.read()

            lvl = [
                Entity(model='quad', scale=(100, 100,), color=color.red),
                Text(text=credits_, background=True,
                     x=-.7, y=.3)
            ]
            lvl[-1].appear(speed=.025)

            [self.scene_active.append(x) for x in lvl]

    def ajout_lemming(self):
        # ajoute un lemming a la position position
        position = self.spawn_position
        if len(self.lemmings_actif) > self.lemmings_cap:
            Text("vous ne pouvez plus ajoutes de lemming, si vous êtes bloquer, recommencer avec 'escape'")
            return

        lemming_nom = 'lemming-'+str(len(self.lemmings)+1)
        self.lemmings[lemming_nom] = Lemming(self, position)
        self.lemmings_actif = [
            lemming for lemming in self.lemmings.values() if lemming.enabled == True]

    def retire_lemming(self, lemming_supprimer):
        # supprimer un lemming
        if lemming_supprimer == None:
            return

        lemming_chercher = None

        for key, value in self.lemmings.items():
            if value == lemming_supprimer:
                lemming_chercher = key
                break
        if lemming_chercher:
            self.lemmings[lemming_chercher].disable()
        self.lemmings_actif = [
            lemming for lemming in self.lemmings.values() if lemming.enabled == True]

        if len(self.lemmings) >= self.lemmings_cap:
            self.perdu()

    def gagner(self):
        # condition de passage
        self.num_niveaux += 1
        self.jeu()

    def perdu(self):
        # condition de perte
        Camera.disable(self.camera)
        perdu_screen = [
            Entity(model='quad', scale=(100, 100, 1), color=color.black, z=-3),
            Text('''Tu as perdu!,\n\n "escape" pour repartir au menu principale \n\n "r" pour recommencer''')
        ]
        [self.scene_active.append(x) for x in perdu_screen]

    def input(self, key):
        if not self.vue_menu:
            if key in ('+', '=') and len(self.lemmings) < self.lemmings_cap:
                self.ajout_lemming()

            if held_keys['space']:
                for lemming in self.lemmings_actif:
                    lemming.saut()

            if held_keys['shift']:
                for lemming in self.lemmings_actif:
                    lemming.précipité()

            if key == 'r':
                self.jeu()

            if held_keys['tab']:
                self.panneau_aide.enabled = True
            else:
                self.panneau_aide.enabled = False

            if key == 's':
                self.gagner()

            if key == Keys.escape:
                self.demarrer()
