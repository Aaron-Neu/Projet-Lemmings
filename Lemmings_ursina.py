"""

Auteurs : Dyami et Andy
Projet Lemming en 2.5d
"""
from random import randint
from ursina import curve
from ursina import *


fullscreen = False
development_mode = True
title = 'lemmings 2: Electric Boogaloo'
borderless = False
forced_aspect_ratio = 1.778
app = Ursina(fullscreen=fullscreen, development_mode=development_mode,
             title=title, borderless=borderless, forced_aspect_ratio=forced_aspect_ratio)
window.fps_counter.enabled = False
window.icon = 'icon.ico'


class Lemming(Entity):
    def __init__(self, **kwargs):
        super().__init__()

        self.model = 'lemming_model'
        self.origin_y = -.15
        self.scale_y = .4*randint(1, 3)*.4
        self.scale_z = .2*randint(1, 3)*.4
        self.scale_x = .4*randint(1, 3)*.4
        self.collider = 'lemming_model'
        self.color = color.white
        self.texture = 'walk.mov'

        self.vitesse = 1
        self.sens_mouvement = 1  # gauche = -1 droite = 1

        self.saut_hauteur = 2
        self.saut_duration = .5
        self.sauter = False

        self.gravity = 1
        self.grounded = True
        self.air_time = 0
        scene = scene
        self._start_fall_sequence = None

        # Verifie si un objet obstrut le lemming et modifie sa position
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

        target_gravity = self.gravity
        self.gravity = 0
        invoke(setattr, self, 'gravity', target_gravity, delay=1/60)

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
        if hit_info.hit == False or hit_info.entity in Jeu_.lemmings:
            self.x += self.sens_mouvement * time.dt * self.vitesse
        else:
            self.sens_mouvement *= -1
            self.look_at((self.x, self.y, self.sens_mouvement))

        ray = boxcast(
            self.world_position+Vec3(0, .1, 0),
            self.down,
            distance=max(.1, self.air_time * self.gravity),
            ignore=(self, ),
            traverse_target=scene,
            thickness=self.scale_x*.9
        )
        if ray.hit:
            if not self.grounded:
                self.land()
            self.grounded = True
            self.y = ray.world_point[1]
            return
        else:
            self.grounded = False

        if not self.grounded and not self.sauter:
            self.y -= min(self.air_time * self.gravity, ray.distance-.1)
            self.air_time += time.dt*4 * self.gravity
        if self.sauter:
            if boxcast(self.position+(0, .1, 0), self.up, distance=self.scale_y,
                       thickness=.95, ignore=(self,), traverse_target=scene).hit:
                self.y_animator.kill()
                self.air_time = 0
                self.start_fall()

    def jump(self):
        # Situation ou le saut est impossible
        if not self.grounded:
            return
        if self._start_fall_sequence:
            self._start_fall_sequence.kill()
        if boxcast(self.position+(0, .1, 0), self.up, distance=self.scale_y, thickness=.95,
                   ignore=(self,), traverse_target=scene).hit:
            return

        self.sauter = True
        self.grounded = False
        target_y = self.y + self.saut_hauteur
        duration = self.saut_duration

        hit_above = boxcast(self.position+(0, self.scale_y/2, 0), self.up,
                            distance=self.saut_hauteur-(self.scale_y/2), thickness=.9, ignore=(self,))

        if hit_above.hit:
            target_y = min(hit_above.world_point.y-self.scale_y, target_y)
            duration *= target_y / (self.y+self.saut_hauteur) + .0000001

        self.animate_y(target_y, duration, resolution=30, curve=curve.out_expo)
        self._start_fall_sequence = invoke(self.start_fall, delay=duration)

    def start_fall(self):
        self.y_animator.pause()
        self.sauter = False

    def land(self):
        self.air_time = 0
        self.grounded = True


class Camera(Entity):
    def __init__(self, **kwargs):
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

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.start_position = self.position
        self.perspective_fov = camera.fov
        self.on_destroy = self.on_disable
        self.hotkeys = {'focus': 'f', 'reset_center': 'shift+f'}

    def on_enable(self):
        camera.org_parent = camera.parent
        camera.org_position = camera.position
        camera.org_rotation = camera.rotation
        camera.parent = self
        camera.position = camera.editor_position
        camera.rotation = (0, 0, 0)
        self.target_z = camera.z

    def on_disable(self):
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


class Material():
    class Concrete(Entity):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.model = 'cube'
            self.collider = 'box'
            self.enabled = True
            self.texture = 'concrete'
            self.origin = (0, 0, 0)

    class Death_block(Entity):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.name = 'Death_block'
            self.model = 'cube'
            self.collider = 'box'
            self.enabled = True
            self.double_sided = True
            self.color = color.red

        def update(self):
            ray = boxcast(origin=self.world_position, thickness=self.scale)
            if ray.entity in Jeu_.lemmings:
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
            if ray.entity in Jeu_.lemmings:
                Jeu_.win()


class Sound(Audio):
    def __init__(self):
        self.mute = False
        self.__music_start = Audio('music_start', autoplay=False, loop=True)
        self.__music_gameplay = Audio(
            'music_gameplay', autoplay=False, loop=True)
        self.__last_played = None

    def play_music(self, music):
        for e in [self.__music_start, self.__music_gameplay]:
            if e.playing == True:
                Sound.pause(e)
        if not self.mute and self.__last_played != music:
            if music == 'start':
                Sound.play(self.__music_start)
                self.__last_played = 'start'
            if music == 'gameplay':
                Sound.play(self.__music_gameplay)
                self.__last_played = 'gameplay'
        else:
            self.set_unmute()

    def set_mute(self):
        self.mute = True
        for e in [self.__music_start, self.__music_gameplay]:
            if e.playing == True:
                Sound.pause(e)

    def set_unmute(self):
        self.mute = False
        if self.__last_played == 'start':
            Sound.resume(self.__music_start)
            self.__last_played = 'start'
        if self.__last_played == 'gameplay':
            Sound.resume(self.__music_gameplay)
            self.__last_played = 'gameplay'


class Jeu():
    def __init__(self):
        self.music = Sound()
        self.active_scene = []
        self.lemmings = []
        self.lemmings_cap = 0
        self.level = 0
        self.camera = Camera()
        self.strike = Entity(model='cube', texture='mute', scale_x=.75, scale_y=.75,
                             x=-6.6, y=-3.5, enabled=False, eternal=False)

    def start_menu(self):
        self.level = 0
        [destroy(self.active_scene.pop())
         for _ in range(len(self.active_scene))]
        self.music.play_music('start')
        Camera.disable(self.camera)
        lemmings_start = Entity(model='quad', texture='lemmings_start.mp4',
                                scale=(14.5, 8.2))
        start_button = Button(parent=camera.ui, model='cube',
                              x=-.33, y=.024, scale=(.325, .1, 1))
        quit_button = Button(parent=camera.ui, model='cube',
                             x=.33, y=.024, scale=(.325, .1, 1))
        mute_button = Button(parent=camera.ui, model='quad', scale_x=.095, scale_y=.095, x=-.825,
                             y=-.44)
        mute_button.on_click = self.mute
        start_button.on_click = self.start_game
        quit_button.on_clic = application.quit
        [self.active_scene.append(x) for x in [
            lemmings_start, start_button, quit_button, mute_button, self.strike]]

    def mute(self):
        if not self.music.mute:
            self.music.set_mute()
            self.strike.enabled = True
        else:
            self.music.set_unmute()
            self.strike.enabled = False

    def start_game(self):
        [destroy(self.active_scene.pop())
         for _ in range(len(self.active_scene))]

        Camera.enable(self.camera)
        help_tip = Text(text='hold "tab" for help', origin=(0, 0), y=-.45)
        sky = Sky()
        self.music.play_music('gameplay')

        [self.active_scene.append(x) for x in [
            help_tip, sky]]

        if self.level == 0:
            self.lemmings_cap += 5

            ground = Material.Concrete(y=-3, scale=(30, 1, 10))
            wall = Entity(model='cube', color=color.azure, origin=(-.5, .5),
                          scale=(5, 10), x=10, y=.5, collider='box')
            wall_2 = duplicate(wall, x=-10)
            ceiling = Entity(model='cube', color=color.white33,
                             origin_y=-.5, scale=(1, 1, 1), y=1, collider='box')
            win_block = Material.Win_block(scale=(20, 1, 10))
            [self.active_scene.append(x) for x in [
                ground, wall, wall_2, ceiling, win_block]]

            self.addlemming()

        if self.level == 1:
            self.lemmings_cap += 7
            lvl = [
                Material.Concrete(scale=(1, 3), position=(-.5, 1.5)),
                Material.Concrete(scale=(4, 1), position=(1, -.5)),
                Material.Concrete(scale=(1, 5), position=(2.5, -3.5)),
                Material.Concrete(scale=(4, 1), position=(4, -6.5)),
                Material.Concrete(scale=(1, 3), position=(5.5, -8.5)),
                Material.Death_block(scale=(1, 1), position=(6.5, -3.5)),
                Material.Death_block(scale=(1, 1), position=(6.5, -10.5)),
                Material.Concrete(scale=(3, 1), position=(8.5, -9.5)),
                Material.Concrete(scale=(2, 1), position=(11, -8.5)),
                Material.Concrete(scale=(2, 1), position=(13, -7.5)),
                Material.Concrete(scale=(1, 10), position=(17.5, -3)),
                Material.Win_block(scale=(3, 1), position=(15.5, -8.5)),
                Material.Concrete(scale=(2, 1), position=(6, -.5)),
                Material.Concrete(scale=(2, 1), position=(8, .5)),
                Material.Concrete(scale=(2, 1), position=(10, 1.5))
            ]
            [self.active_scene.append(x) for x in lvl]

        if self.level == 2:
            self.lemmings_cap += 15
            lvl = [
                Material.Concrete(scale=(5, 1), position=(0, -2)),
                Material.Concrete(scale=(1, 3), position=(3, -2)),
                Material.Concrete(scale=(1, 2), position=(-3, -1.5)),
                Material.Concrete(scale=(1, 6), position=(6, -1.5)),
                Material.Concrete(scale=(7, 1), position=(3, -5)),
                Material.Concrete(scale=(1, 6), position=(-3, -5.5)),
                Material.Concrete(scale=(4, 1), position=(-1.5, -9)),
                Material.Concrete(scale=(1, 1), position=(0, -8)),
                Material.Death_block(scale=(1, 0.5), position=(1, -9.25)),
                Material.Concrete(scale=(5, 1), position=(4, -9)),
                Material.Concrete(scale=(1, 1), position=(7, -8)),
                Material.Concrete(scale=(1, 1), position=(8, -7)),
                Material.Concrete(scale=(1, 1), position=(9, -6)),
                Material.Concrete(scale=(1, 1), position=(10, -5)),
                Material.Win_block(scale=(3, 1), position=(12, -50)),
            ]
            [self.active_scene.append(x) for x in lvl]

        if self.level == 3:
            destroy(help_tip)
            Camera.disable(self.camera)
            lvl = [
                Entity(model='quad', scale=(100, 100,), color=color.red),
                Text('''
                You win!
                -------------------------------------
                Created by Dyami Neu and Andy How
                This work is marked with CC0 1.0 Universal.
                
                Built in Python with the Ursina engine.
                -----------assets credited-----------
                Anji bamboo forest (title screen) - Clerkwheel (modified) | CC 3.0
                Golden.ttf (title font) - imagex | CC 3.0
                Pixel.ttf (CC font) - Markus Schröppel | CC 3.0
                Mao zedong propaganda music Trap remix (title screen music) - Vosi
                Without the Communist Party, There Would Be No New China (gameplay music) - Communist Party of China
                Concrete wall texture - texturepalace.com | CC 4.0
                -------------------------------------
                press "escape" to exit to main menu
                ''', background=True, x=-.7, y=.3)
            ]

            [self.active_scene.append(x) for x in lvl]

    def addlemming(self, position=(0, 0, 0)):
        gamespeed = self.gamespeed
        self.lemmings.append(Lemming(gamespeed, position=position))

    def removelemming(self, lemming):
        lemming.enabled = False
        if len(self.lemmings) >= self.lemmings_cap:
            self.game_over()

    def win(self):
        self.level += 1
        self.start_game()

    def game_over(self):
        Camera.disable(self.camera)
        game_over_screen = [
            Entity(model='quad', scale=(100, 100, 1), color=color.black, z=-3),
            Text('''You lost!,\n\n press "escape"''')
        ]
        [self.active_scene.append(x) for x in game_over_screen]


Jeu_ = Jeu()

help_panel = WindowPanel(
    title='Help',
    content=(
        Text('''use "+" to add a lemming \n\n 
                use keys "0" to "9"\n 
                to change walking speed of lemming(s) \n\n 
                use "space"\n 
                to make the lemming(s) jump\n\n
                use mouse to navigate\n\n
                use "shift"+"f" to recenter camera'''),
    ),
    popup=True,
    enabled=False
)


def input(key, help_panel=help_panel):
    try:
        if len(Jeu_.lemmings) > 0:
            if key == '+' and len(Jeu_.lemmings) < Jeu_.lemmings_cap:
                Jeu_.addlemming()

            if key in [str(x) for x in range(10)]:
                Jeu_.gamespeed = int(key)
                for e in Jeu_.lemmings:
                    e.vitesse = Jeu_.gamespeed

            if key == 'space':
                for e in Jeu_.lemmings:
                    e.jump()

            if held_keys['tab']:
                help_panel.enabled = True
            else:
                help_panel.enabled = False

            if key == Keys.escape:
                Jeu_.start_menu()

            print(key)

    except:
        print('input error')


def main():
    Jeu_.start_menu()
    app.run()


if __name__ == '__main__':
    main()
