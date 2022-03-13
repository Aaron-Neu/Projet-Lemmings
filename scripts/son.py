"""
Auteurs : Dyami Neu et Andy How

Son pour le Projet Lemming en 3d
"""

from ursina import Audio


class Son(Audio):
    """
    Gère les sons du jeu
    """

    def __init__(self, **kwargs):
        self.muet = False
        self.__music_trap_remix = Audio(
            'music_trap_remix', autoplay=False, loop=True)
        self.__music_without_communist = Audio(
            'music_without_communist', autoplay=False, loop=True)
        self.__us_army_song = Audio(
            'When_Johnny', autoplay=False, loop=True)
        self.dernier_joué = []
        self.liste_music = [self.__music_trap_remix,
                            self.__music_without_communist]

    def jouer_music(self, music):
        for e in self.liste_music:
            if e.playing == True:
                Son.pause(e)
        if not self.muet and music not in self.dernier_joué:
            if music == 'start':
                Son.play(self.__music_trap_remix)
                self.dernier_joué.append('start')
            if music == 'gameplay':
                Son.play(self.__music_without_communist)
                self.dernier_joué.append('gameplay')
            if music == 'out':
                Son.play(self.__us_army_song)
                self.dernier_joué.append('out')
        else:
            self.set_unmuet()

    def set_muet(self):
        self.muet = True
        for e in self.liste_music:
            if e.playing == True:
                Son.pause(e)

    def set_unmuet(self):
        # reactive le dernier son
        self.muet = False
        if self.dernier_joué[-1] == 'start':
            Son.resume(self.__music_trap_remix)
            self.dernier_joué.append('start')
        if self.dernier_joué[-1] == 'gameplay':
            Son.resume(self.__music_without_communist)
            self.dernier_joué.append('gameplay')
        if self.dernier_joué[-1] == 'out':
            Son.resume(self.__us_army_song)
            self.dernier_joué.append('out')
