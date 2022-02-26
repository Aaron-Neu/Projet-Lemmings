"""
Auteurs : Dyami Neu et Andy How

Entites pour le Projet Lemming en 3d
"""

from random import randint
from ursina import curve
from ursina import *



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
                self.instance_jeu.retire_lemming(self)

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
                self.instance_jeu.retire_lemming(self)

    def tire(self, target):
        if self.tire_refroidir:
            return
        obus_ind = Entity(model='cube', colider='cube', origin=self.origin,
                      position=(self.x+2*self.sens_mouvement,self.y+.5,self.z), scale=(.1, .1, .1), color=color.gray)
        obus_ind.animate_position(target, duration=1, curve=curve.in_out_quad)
        ray = boxcast(obus_ind.world_position, distance=.5, thickness=.5)
        if ray.entity in self.instance_jeu.lemmings_actif:
            self.instance_jeu.retire_lemming(ray.entity)
        self.obus.append(obus_ind)
        invoke(self.tire_a_zero, delay=2)

    def tire_a_zero(self):
        [destroy(x) for x in self.obus]
        self.tire_refroidir = False
    
    def atterrissage(self):
        self.air_temps = 0
        self.atterri = True
