"""
Fichier Principal
Auteurs : Dyami Neu et Andy How

Projet Lemming en 3d et 2d

Ce projet est un jeu en 3d qui utilise la librairie Ursina.
Documentation: https://www.ursinaengine.org/documentation.html
Toutes licenses associes sont mentionnes dans le fichier texte 'credit.txt'
"""
import jeu_2d
from niveaux import *

class Lemming(Entity):
    """
    Objet lemming, controler par le joueur, on instacie cette classe pour creer un lemming
    """

    def __init__(self, jeu, **kwargs):
        super().__init__()

        nb_hasard = randint(1, 3)

        self.instance_jeu = jeu
        self.model = 'lemming_model'
        self.origin_y = -.15
        self.origin_z = 1+2*randint(-1, 1)
        self.scale_y = nb_hasard*.16
        self.scale_z = randint(1, 2)*.1
        self.scale_x = nb_hasard*.12
        self.collider = 'lemming_model'
        self.color = color.white
        self.texture = 'walk.mov'

        self.__dict__.update(kwargs)

        self.vitesse = 5-nb_hasard
        self.sens_mouvement = 1  # gauche = -1 droite = 1

        self.saut_hauteur = 1+nb_hasard*.16*3
        self.saut_duration = nb_hasard*.12*1.5
        self.sauter = False

        self.précipité_duration = nb_hasard*.17
        self.précipité_refroidir = False

        self.atterri = True
        self.air_temps = 0
        self.gravité = .5
        self._sequence_atterrissage = None

        # vérifie si un objet obstrue le lemming et modifie la position du lemming
        ray_up = boxcast(self.world_position, self.down, distance=10, ignore=(
            self, ), traverse_target=scene, thickness=.9)
        if ray_up.hit:
            self.y = ray_up.world_point[1] - 1

        ray_down = boxcast(self.world_position, self.up, distance=10, ignore=(
            self, ), traverse_target=scene, thickness=.9)
        if ray_down.hit:
            self.y = ray_down.world_point[1] + 1

        ray_right = boxcast(self.world_position, self.right, distance=10, ignore=(
            self, ), traverse_target=scene, thickness=.9)
        if ray_right.hit:
            self.x = ray_right.world_point[0] - 1

        ray_left = boxcast(self.world_position, self.left, distance=10, ignore=(
            self, ), traverse_target=scene, thickness=.9)
        if ray_left.hit:
            self.x = ray_left.world_point[0] + 1


    def update(self):
        # vérifie si le lemming touche un objet
        hit_info = boxcast(
            self.position+Vec3(self.sens_mouvement * time.dt *
                               self.vitesse, self.scale_y/2, 0),
            direction=Vec3(self.sens_mouvement, 0, 0),
            distance=abs(self.scale_x/2),
            ignore=(self, ),
            traverse_target=scene,
            thickness=(self.scale_x*.9, self.scale_y*.9),
        )
        if hit_info.hit == False or hit_info.entity in self.instance_jeu.lemmings:
            self.x += self.sens_mouvement * time.dt * self.vitesse
        else:
            self.sens_mouvement *= -1
            self.look_at((self.x, self.y, self.sens_mouvement))
            self.y += .1
            self.x -= .01

        # vérifie si le lemming a atterrie
        ray = boxcast(
            self.world_position+Vec3(0, .1, 0),
            self.down,
            distance=max(.1, self.air_temps * self.gravité),
            ignore=(self, ),
            traverse_target=scene,
            thickness=self.scale_x*.9
        )
        if ray.hit:
            if not self.atterri:
                self.atterrissage()
            self.atterri = True
            self.y = ray.world_point[1]
            return
        else:
            self.atterri = False

        # si le lemming n'as pas atterrie
        if not self.atterri and not self.sauter:
            self.y -= min(self.air_temps * self.gravité, ray.distance-.1)
            self.air_temps += time.dt*4 * self.gravité
            if self.y < -200:
                self.instance_jeu.removelemming(self)

        # si le lemming saute
        if self.sauter:
            if boxcast(self.position+(0, .1, 0), self.up, distance=self.scale_y,
                       thickness=.95, ignore=(self,), traverse_target=scene).hit:
                self.y_animator.kill()
                self.air_temps = 0
                self.tombe()

    def saut(self):
        # situation ou le saut est impossible
        if not self.atterri:
            return
        if boxcast(self.position+(0, .1, 0), self.up, distance=self.scale_y, thickness=.95,
                   ignore=(self,), traverse_target=scene).hit:
            return

        self.sauter = True
        self.atterri = False
        target_y = self.y + self.saut_hauteur
        duration = self.saut_duration

        hit_dessus = boxcast(self.position+(0, self.scale_y/2, 0), self.up,
                             distance=self.saut_hauteur-(self.scale_y/2), thickness=.9, ignore=(self,))

        if hit_dessus.hit:
            target_y = min(hit_dessus.world_point.y-self.scale_y, target_y)
            duration *= target_y / (self.y+self.saut_hauteur)

        # séquence de saut
        self.animate_y(target_y, duration, curve=curve.out_expo)
        self._sequence_atterrissage = invoke(self.tombe, delay=duration)

    def tombe(self):
        self.y_animator.pause()
        self.sauter = False

    def atterrissage(self):
        self.air_temps = 0
        self.atterri = True

    def précipité(self):
        if self.précipité_refroidir:
            return
        if boxcast(self.position+(0, self.scale_y/2, 0), self.forward,
                   distance=self.scale_y*self.vitesse+self.précipité_duration, thickness=.1,
                   ignore=(self,), traverse_target=scene).hit:
            return

        self.précipité_refroidir = True
        target_x = self.x + self.vitesse * self.sens_mouvement
        duration = self.précipité_duration

        self.animate_x(target_x, duration, curve=curve.linear)
        invoke(self.précipité_a_zero, delay=2)

    def précipité_a_zero(self):
        self.précipité_refroidir = False


class Char(Entity):
    """
    Objet Char, ennemie
    """

    def __init__(self, jeu, position, **kwargs):
        super().__init__()

        self.instance_jeu = jeu
        self.model = 'char_model'
        self.origin_y = -.15
        self.scale = (.4, .6, .5)
        self.collider = 'char_model'
        self.color = color.white
        self.texture = 'char'
        self.position = position

        self.__dict__.update(kwargs)

        self.tire_refroidir = False
        self.obus = []
        self.vitesse = .5
        self.sens_mouvement = 1  # gauche = -1 droite = 1

        self.atterri = True
        self.air_temps = 0
        self.gravité = .5

    def update(self):
        hit_info = boxcast(
            self.position+Vec3(self.sens_mouvement * time.dt *
                               self.vitesse, self.scale_y/2, 0),
            direction=Vec3(self.sens_mouvement, 0, 0),
            distance=abs(self.scale_x/2),
            ignore=(self, ),
            traverse_target=scene,
            thickness=(self.scale_x*.9, self.scale_y*.9),
        )
        if hit_info.hit == False:
            self.x += self.sens_mouvement * time.dt * self.vitesse
        else:
            self.sens_mouvement *= -1
            self.look_at((self.x, self.y, self.sens_mouvement))
            self.y += .1
            self.x -= .01

        ray = boxcast(
            self.world_position+Vec3(0, .1, 0),
            direction=Vec3(self.sens_mouvement, 0, 0),
            distance=5,
            ignore=(self, ),
            traverse_target=scene,
            thickness=2
        )
        if ray.hit:
            if ray.entity in self.instance_jeu.lemmings_actif:
                self.tire(ray.entity.world_position)
        
        ray = boxcast(
            self.world_position+Vec3(0, .1, 0),
            self.down,
            distance=max(.1, self.air_temps * self.gravité),
            ignore=(self, ),
            traverse_target=scene,
            thickness=self.scale_x*.9
        )
        if ray.hit:
            if not self.atterri:
                self.atterrissage()
            self.atterri = True
            self.y = ray.world_point[1]
            return
        else:
            self.atterri = False

        if not self.atterri:
            self.y -= min(self.air_temps * self.gravité, ray.distance-.1)
            self.air_temps += time.dt*4 * self.gravité
            if self.y < -200:
                self.instance_jeu.removelemming(self)

    def tire(self, target):
        if self.tire_refroidir:
            return
        obus_ind = Entity(model='cube', colider='cube', origin=self.origin,
                      position=(self.x+2*self.sens_mouvement,self.y+.5,self.z), scale=(.1, .1, .1), color=color.gray)
        obus_ind.animate_position(target, duration=1, curve=curve.in_out_quad)
        ray = boxcast(obus_ind.world_position, distance=.5, thickness=.5)
        if ray.entity in self.instance_jeu.lemmings_actif:
            self.instance_jeu.removelemming(ray.entity)
        self.obus.append(obus_ind)
        invoke(self.tire_a_zero, delay=2)

    def tire_a_zero(self):
        [destroy(x) for x in self.obus]
        self.tire_refroidir = False
    
    def atterrissage(self):
        self.air_temps = 0
        self.atterri = True


class Jeu(Entity):
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
        self.music = Sound()
        self.niveaux = Niveaux()
        self.camera = Camera(self)

        self.scene_active = []
        self.num_niveaux = 0
        self.vue_menu = True

        self.lemmings = {}
        self.lemmings_actif = []
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

    def demarer(self):
        # le menu d'entre du jeu
        [destroy(self.scene_active.pop())
         for _ in range(len(self.scene_active))]
        [self.removelemming(x)
         for x in self.lemmings_actif]
        self.num_niveaux = 1

        self.music.jouer_music('start')
        Camera.disable(self.camera)
        lemmings_start = Entity(model='quad', texture='lemmings_start.mp4',
                                scale=(14.5, 8.2))
        boutton_demarer = Button(parent=camera.ui, model='cube',
                                 x=-.33, y=.024, scale=(.325, .1, 1))
        boutton_quitter = Button(parent=camera.ui, model='cube',
                                 x=.33, y=.024, scale=(.325, .1, 1))
        boutton_muet = Button(parent=camera.ui, model='quad', scale_x=.095, scale_y=.095, x=-.825,
                              y=-.44)
        boutton_muet.on_click = self.muet
        boutton_demarer.on_click = self.jeu
        boutton_quitter.on_clic = application.quit
        [self.scene_active.append(x) for x in [
            lemmings_start, boutton_demarer, boutton_quitter, boutton_muet, self.croix_muet]]

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
        [self.removelemming(x)
         for x in self.lemmings_actif]

        Camera.enable(self.camera)
        help_tip = Text(
            text="maintenez 'tab' pour obtenir de l'aide", origin=(0, 0), y=-.45, color=color.black)
        sky = Sky()

        [self.scene_active.append(x) for x in [
            help_tip, sky]]

        if self.num_niveaux == 0:
            self.music.jouer_music('gameplay00')
            self.lemmings_cap += 5
            lvl = self.niveaux.generer_niveau(0)
            lvl.append(self.niveaux.Win_block(self, position=(57.5, -22,)))
            [self.scene_active.append(x) for x in lvl]

        if self.num_niveaux == 1:
            self.music.jouer_music('gameplay00')
            self.lemmings_cap += 10
            lvl = self.niveaux.generer_niveau(1)
            lvl.append(self.niveaux.Win_block(self, position=(130, -40,)))
            lvl.append(Char(self, (20, -40,)))
            [self.scene_active.append(x) for x in lvl]

        if self.num_niveaux == 2:
            self.music.jouer_music('gameplay00')
            self.lemmings_cap += 10
            lvl = self.niveaux.generer_niveau(2)
            lvl.append(self.niveaux.Win_block(self, position=(200, -50,)))
            [self.scene_active.append(x) for x in lvl]

        if self.num_niveaux == 3 :
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

    def addlemming(self, position=(2, -5, 0)):
        # ajoute un lemming a la position position
        if len(self.lemmings_actif) > self.lemmings_cap:
            Text("vous ne pouvez plus ajoutes de lemming, si vous etre bloquer, recomencer avec 'escape'")
            return

        lemming_nom = 'lemming-'+str(len(self.lemmings)+1)
        self.lemmings[lemming_nom] = Lemming(self, position=position)
        self.lemmings_actif = [
            lemming for lemming in self.lemmings.values() if lemming.enabled == True]

    def removelemming(self, lemming_supprimer):
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
            self.game_over()

    def win(self):
        # condition de passage
        self.num_niveaux += 1
        self.jeu()

    def game_over(self):
        # condition de perte
        Camera.disable(self.camera)
        game_over_screen = [
            Entity(model='quad', scale=(100, 100, 1), color=color.black, z=-3),
            Text('''Tu as perdu!,\n\n presse "escape"''')
        ]
        [self.scene_active.append(x) for x in game_over_screen]

    def input(self, key):
        if not self.vue_menu:
            if key in ('+', '=') and len(self.lemmings) < self.lemmings_cap:
                self.addlemming()

            if held_keys['space']:
                for lemming in self.lemmings_actif:
                    lemming.saut()

            if key in 'shift':
                for lemming in self.lemmings_actif:
                    lemming.précipité()

            if held_keys['tab']:
                self.panneau_aide.enabled = True
            else:
                self.panneau_aide.enabled = False

            if key == Keys.escape:
                self.demarer()


def jeu3d():
    Jeu3 = Jeu()
    Jeu3.demarer()
    Jeu3.app.run()

def jeu2d():
    Jeu2 = jeu_2d.Jeu_2d(10)
    Jeu2.demarre()

if __name__ == '__main__':
    jeu3d()
    # rep = 0
    # while True:    
    #     if rep == 2:
    #         jeu2d()
    #     elif rep == 3:
    #         jeu3d()
    #     else:
    #         rep = int(input('entrer 2 pour le jeu en 2d et 3 pour le jeu en 3d\nchoix: '))
