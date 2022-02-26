"""
Auteurs : Dyami Neu et Andy How

Camera pour le Projet Lemming en 3d
"""

from ursina import curve
from ursina import *


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
        self.hauteur_niveau = 0

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
                if self.instance_jeu.lemmings_actif[-1].Y > -self.hauteur_niveau:
                    self.position = self.instance_jeu.lemmings_actif[-1].position

        camera.z = lerp(camera.z, self.target_z, time.dt*self.zoom_smoothing)
