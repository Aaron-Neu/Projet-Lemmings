"""
Auteurs : Dyami Neu et Andy How

Projet Lemming en 3d

Ce projet est un jeu en 3d qui utilise la librairie Ursina.
Documentation: https://www.ursinaengine.org/documentation.html
Toutes licenses associes sont mentionnes dans le fichier texte 'credit.txt'
"""
from random import randint
from turtle import pos, position
from ursina import curve
from ursina import *

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


class Lemming(Entity):
    """
    Objet lemming, controler par le joueur, on instacie cette classe pour creer un lemming
    """

    def __init__(self, **kwargs):
        super().__init__()

        nb_hasard = randint(1, 3)

        self.model = 'lemming_model'
        self.origin_y = -.15
        self.origin_z = nb_hasard*.01
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

        self.atterri = True
        self.air_temps = 0
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

        self.gravité = .5

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
        if hit_info.hit == False or hit_info.entity in Jeu_.lemmings:
            self.x += self.sens_mouvement * time.dt * self.vitesse
        else:
            self.sens_mouvement *= -1
            self.look_at((self.x, self.y, self.sens_mouvement))

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


class Camera(Entity):
    """
    Camera basic avec une limite max et min sur le zoom
    inspire par: https://github.com/pokepetter/ursina/blob/master/ursina/prefabs/editor_camera.py
    """

    def __init__(self):
        camera.editor_position = camera.position
        super().__init__(name='camera', eternal=True)

        self.rotation_speed = 200
        self.pan_speed = Vec2(5, 5)
        self.move_speed = 10
        self.zoom_speed = 1.25
        self.zoom_smoothing = 8
        self.rotate_around_mouse_hit = False
        self.max_zoom = 100
        self.min_zoom = 20

        self.start_position = self.position
        self.perspective_fov = camera.fov
        self.on_destroy = self.on_disable
        self.hotkeys = {'focus': 'f', 'reset_center': 'shift+f'}

    def on_enable(self):
        # fonction pour utiliser la 3d
        camera.org_parent = camera.parent
        camera.org_position = camera.position
        camera.org_rotation = camera.rotation
        camera.parent = self
        camera.position = camera.editor_position
        camera.rotation = (0, 0, 0)
        self.target_z = camera.z

    def on_disable(self):
        # fonction pour utiliser la 2d
        camera.editor_position = camera.position
        camera.parent = camera.org_parent
        camera.position = camera.org_position
        camera.rotation = camera.org_rotation

    def input(self, key):
        combined_key = ''.join(
            e+'+' for e in ('control', 'shift', 'alt') if held_keys[e] and not e == key) + key

        if combined_key == self.hotkeys['reset_center']:
            self.animate_position(self.start_position,
                                  duration=.1, curve=curve.linear)

        elif combined_key == self.hotkeys['focus'] and mouse.world_point:
            self.animate_position(
                mouse.world_point, duration=.1, curve=curve.linear)

        elif key == 'scroll up' and abs(self.target_z) > self.min_zoom:
            target_position = self.world_position
            self.world_position = lerp(
                self.world_position, target_position, self.zoom_speed * time.dt * 10)
            self.target_z += self.zoom_speed * (abs(self.target_z)*.1)

        elif key == 'scroll down' and abs(self.target_z) < self.max_zoom:
            self.target_z -= self.zoom_speed * (abs(camera.z)*.1)

        elif key == 'right mouse down' or key == 'middle mouse down':
            if mouse.hovered_entity and self.rotate_around_mouse_hit:
                org_pos = camera.world_position
                self.world_position = mouse.world_point
                camera.world_position = org_pos

    def update(self):
        if mouse.right:
            self.rotation_x -= mouse.velocity[1] * self.rotation_speed
            self.rotation_y += mouse.velocity[0] * self.rotation_speed

            self.direction = Vec3(
                self.forward * (held_keys['w'] - held_keys['s'])
                + self.right * (held_keys['d'] - held_keys['a'])
                + self.up * (held_keys['e'] - held_keys['q'])
            ).normalized()

            self.position += self.direction * (self.move_speed + (
                self.move_speed * held_keys['shift']) - (self.move_speed*.9 * held_keys['alt'])) * time.dt

            if self.target_z < 0:
                self.target_z += held_keys['w'] * (self.move_speed + (
                    self.move_speed * held_keys['shift']) - (self.move_speed*.9 * held_keys['alt'])) * time.dt
            else:
                self.position += camera.forward * held_keys['w'] * (self.move_speed + (
                    self.move_speed * held_keys['shift']) - (self.move_speed*.9 * held_keys['alt'])) * time.dt

            self.target_z -= held_keys['s'] * (self.move_speed + (
                self.move_speed * held_keys['shift']) - (self.move_speed*.9 * held_keys['alt'])) * time.dt

        if mouse.middle:
            zoom_compensation = -self.target_z * .1

            self.position -= camera.right * \
                mouse.velocity[0] * self.pan_speed[0] * zoom_compensation
            self.position -= camera.up * \
                mouse.velocity[1] * self.pan_speed[1] * zoom_compensation

        camera.z = lerp(camera.z, self.target_z, time.dt*self.zoom_smoothing)


class Niveaux():
    """
    Regroupement de classes qui sont utiliser pour construire les niveaux
    """

    def __init__(self):
        self.niveau00 = load_texture('niveau00')
        self.niveau01 = load_texture('niveau01')
        self.niveau02 = load_texture('niveau02')
        self.niveau03 = load_texture('niveau03')
        self.niveau04 = load_texture('niveau04')
        self.niveau05 = load_texture('niveau05')
        self.niveau06 = load_texture('niveau06')
        self.niveau07 = load_texture('niveau07')
        self.niveau08 = load_texture('niveau08')

    def generer_niveau(self, num):
        if num == 1:
            return self.créer_niveau(self.niveau01)
        elif num == 2:
            return self.créer_niveau(self.niveau02)
        elif num == 3:
            return self.créer_niveau(self.niveau03)
        elif num == 4:
            return self.créer_niveau(self.niveau04)
        elif num == 5:
            return self.créer_niveau(self.niveau05)
        elif num == 6:
            return self.créer_niveau(self.niveau06)
        elif num == 7:
            return self.créer_niveau(self.niveau07)
        elif num == 8:
            return self.créer_niveau(self.niveau08)
        else:
            return self.créer_niveau(self.niveau00)

    def créer_niveau(self, texture_niveau):
        niveau_cadre = [Entity(enabled=False,position=(-1,-1,-1))]
        for y in range(texture_niveau.height):
            for x in range(texture_niveau.width):
                if texture_niveau.get_pixel(x, y) == color.black:
                    niveau_cadre.append(Entity(model='cube', collider='box',  
                    position=(x, y,), origin=(10, texture_niveau.height,), scale_z = 2,
                    color=color.random_color()))
        return niveau_cadre

    class Death_block(Entity):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.model = 'cube'
            self.collider = 'box'
            self.enabled = True
            self.double_sided = True
            self.color = color.red
            self.__dict__.update(kwargs)

        def update(self):
            ray = boxcast(origin=self.world_position, thickness=self.scale)
            if ray.entity in Jeu_.lemmings_actif:
                Jeu_.removelemming(ray.entity)

    class Win_block(Entity):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.name = 'Win_block'
            self.model = 'cube'
            self.collider = 'box'
            self.enabled = True
            self.double_sided = True
            self.color = color.yellow

        def update(self):
            ray = boxcast(origin=self.world_position, thickness=self.scale)
            if ray.entity in Jeu_.lemmings_actif:
                Jeu_.win()


class Sound(Audio):
    """
    Gère les sons du jeu
    """

    def __init__(self):
        self.muet = False
        self.__music_trap_remix = Audio(
            'music_trap_remix', autoplay=False, loop=True)
        self.__music_without_communist = Audio(
            'music_without_communist', autoplay=False, loop=True)
        self.dernier_joué = None

    def jouer_music(self, music):
        for e in [self.__music_trap_remix, self.__music_without_communist]:
            if e.playing == True:
                Sound.pause(e)
        if not self.muet and self.dernier_joué != music:
            if music == 'start':
                Sound.play(self.__music_trap_remix)
                self.dernier_joué = 'start'
            if music == 'gameplay':
                Sound.play(self.__music_without_communist)
                self.dernier_joué = 'gameplay'
        else:
            self.set_unmuet()

    def set_muet(self):
        self.muet = True
        for e in [self.__music_trap_remix, self.__music_without_communist]:
            if e.playing == True:
                Sound.pause(e)

    def set_unmuet(self):
        # reactive le dernier son
        self.muet = False
        if self.dernier_joué == 'start':
            Sound.resume(self.__music_trap_remix)
            self.dernier_joué = 'start'
        if self.dernier_joué == 'gameplay':
            Sound.resume(self.__music_without_communist)
            self.dernier_joué = 'gameplay'


class Jeu():
    def __init__(self):
        self.music = Sound()
        self.niveaux = Niveaux()
        self.camera = Camera()

        self.scene_active = []
        self.num_niveaux = 0

        self.lemmings = {}
        self.lemmings_actif = []
        self.lemmings_cap = 0
        self.croix_muet = Entity(model='cube', texture='mute', scale_x=.75, scale_y=.75,
                                 x=-6.6, y=-3.5, enabled=False, eternal=False)

    def demarer(self):
        self.num_niveaux = 0
        [destroy(self.scene_active.pop())
         for _ in range(len(self.scene_active))]
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
        [destroy(self.scene_active.pop())
         for _ in range(len(self.scene_active))]

        Camera.enable(self.camera)
        help_tip = Text(
            text="maintenez 'tab' pour obtenir de l'aide", origin=(0, 0), y=-.45)
        sky = Sky()
        self.music.jouer_music('gameplay')

        [self.scene_active.append(x) for x in [
            help_tip, sky]]

        if self.num_niveaux == 0:
            self.lemmings_cap += 7
            self.addlemming()
            self.niveaux.generer_niveau(0)
            lvl = []
            [self.scene_active.append(x) for x in lvl]

        if self.num_niveaux == 1:
            self.lemmings_cap += 15
            lvl = [self.niveaux.generer_niveau(1)]
            [self.scene_active.append(x) for x in lvl]

        if self.num_niveaux == 2:
            destroy(help_tip)
            Camera.disable(self.camera)

            with open('credits.txt', 'r') as file:
                credits_ = file.read().replace('\n', '')

            lvl = [
                Entity(model='quad', scale=(100, 100,), color=color.red),
                Text(text=credits_, background=True,
                     x=-.7, y=.3).appear(speed=.025)
            ]

            [self.scene_active.append(x) for x in lvl]

    def addlemming(self, position=(0, 0, 0)):
        # ajoute un lemming a la position position
        if len(self.lemmings) > self.lemmings_cap:
            return

        lemming_nom = 'lemming-'+str(len(self.lemmings)+1)
        self.lemmings[lemming_nom] = Lemming(position=position)
        self.lemmings_actif = [
            lemming for lemming in self.lemmings.values() if lemming.enabled == True]

    def removelemming(self, lemming_supprimer):
        # supprimer un lemming
        if lemming_supprimer == None:
            return

        for key, value in self.lemmings.items():
            if value == lemming_supprimer:
                lemming_chercher = key
                break

        self.lemmings[lemming_chercher].disable()
        self.lemmings_actif = [
            lemming for lemming in self.lemmings.values() if lemming.enabled == True]

        if len(self.lemmings) >= self.lemmings_cap:
            self.game_over()

    def win(self):
        # condition de victoire
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


Jeu_ = Jeu()

panneau_aide = WindowPanel(
    title='Aide',
    content=(
        Text('''utilisez "+" pour ajouter un lemming \n\n
                 utiliser "espace" pour\n
                 faire sauter le(s) lemming(s)\n\n
                 utilisez la souris pour naviguer\n\n
                 utilisez "shift" + "f" pour recentrer la caméra'''),
    ),
    popup=True,
    enabled=False
)


def input(key, help_panel=panneau_aide):
    if len(Jeu_.lemmings) > 0:
        if key == '+' and len(Jeu_.lemmings) < Jeu_.lemmings_cap:
            Jeu_.addlemming()

        if 'space' in key:
            for lemming in Jeu_.lemmings_actif:
                lemming.saut()

        if held_keys['tab']:
            panneau_aide.enabled = True
        else:
            panneau_aide.enabled = False

        if key == Keys.escape:
            Jeu_.demarer()

        print(key)


def main():
    Jeu_.demarer()
    app.run()


if __name__ == '__main__':
    main()
