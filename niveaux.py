"""
Auteurs : Dyami Neu et Andy How

environements pour le Projet Lemming en 3d

Ce projet est un jeu en 3d qui utilise la librairie Ursina.
Documentation: https://www.ursinaengine.org/documentation.html
Toutes licenses associes sont mentionnes dans le fichier texte 'credit.txt'
"""

from random import randint
from ursina import curve
from ursina import *

dimensions_niveau = None


class Camera(Entity):
    """
    Camera basic avec une limite max et min sur le zoom
    inspire par: https://github.com/pokepetter/ursina/blob/master/ursina/prefabs/editor_camera.py
    """

    def __init__(self, jeu, **kwargs):
        camera.editor_position = camera.position
        super().__init__(name='camera', eternal=True)
        self.instance_jeu = jeu
        self.rotation_speed = 200
        self.pan_speed = Vec2(5, 5)
        self.move_speed = 10
        self.zoom_speed = 1.25
        self.zoom_smoothing = 8
        self.rotate_around_mouse_hit = False
        self.max_zoom = 200
        self.min_zoom = 20

        self.start_position = self.position
        self.perspective_fov = camera.fov
        self.on_destroy = self.on_disable
        self.focus = True
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

        elif combined_key == self.hotkeys['focus'] and self.focus:
            self.focus = False

        elif combined_key == self.hotkeys['focus'] and not self.focus:
            self.focus = True

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
        global dimensions_niveau
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

        if self.focus:
            if len(self.instance_jeu.lemmings_actif) > 0:
                if self.instance_jeu.lemmings_actif[-1].Y > -dimensions_niveau[0]:
                    self.position = self.instance_jeu.lemmings_actif[-1].position
        
        camera.z = lerp(camera.z, self.target_z, time.dt*self.zoom_smoothing)


class Niveaux():
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
        global dimensions_niveau
        bornes = thème[0]
        principale = thème[1]
        secondaire = thème[2]
        fond = thème[3]

        décalage = 10
        couleur_encadrement = color.rgb(252, 234, 196)
        niveau_cadre = [Entity(enabled=False, position=(-1, -1, -1))]
        dimensions_niveau = (texture_niveau.height,texture_niveau.width)

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


class Sound(Audio):
    """
    Gère les sons du jeu
    """

    def __init__(self, **kwargs):
        self.muet = False
        self.__music_trap_remix = Audio(
            'music_trap_remix', autoplay=False, loop=True)
        self.__music_without_communist = Audio(
            'music_without_communist', autoplay=False, loop=True)
        self.dernier_joué = []
        self.liste_music = [self.__music_trap_remix,
                            self.__music_without_communist]

    def jouer_music(self, music):
        for e in self.liste_music:
            if e.playing == True:
                Sound.pause(e)
        if not self.muet and music not in self.dernier_joué:
            if music == 'start':
                Sound.play(self.__music_trap_remix)
                self.dernier_joué.append('start')
            if music == 'gameplay00':
                Sound.play(self.__music_without_communist)
                self.dernier_joué.append('gameplay00')
        else:
            self.set_unmuet()

    def set_muet(self):
        self.muet = True
        for e in self.liste_music:
            if e.playing == True:
                Sound.pause(e)

    def set_unmuet(self):
        # reactive le dernier son
        self.muet = False
        if self.dernier_joué[-1] == 'start':
            Sound.resume(self.__music_trap_remix)
            self.dernier_joué.append('start')
        if self.dernier_joué[-1] == 'gameplay00':
            Sound.resume(self.__music_without_communist)
            self.dernier_joué.append('gameplay00')
