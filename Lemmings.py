"""
Auteurs : Dyami et Andy
Projet Lemming avec ASCII
"""



class Lemming():
    def __init__(self, l, c, d):
        self.l = l
        self.c = c
        self.d = d

    def action(self, l, c, d, grotte, erase=True):
        if erase == True:
            grotte[self.l][0] = grotte[self.l][0][:self.c] + \
                ' ' + grotte[self.l][0][self.c+1:]
        self.l = l
        self.c = c
        self.d = d
        if self.d == 1:
            x = '>'
        else:
            x = '<'
        if not (self.l ,self.c ,self.d) == (0,0,0):
            grotte[self.l][0] = grotte[self.l][0][:self.c] + \
                x + grotte[self.l][0][self.c+1:]


class Case():
    def libre(grotte, l, c):
        if grotte[l][0][c] in ['#', '<', '>']:
            return False
        return True


class Jeu():
    def __init__(self, nblem):
        self.grotte = [['#🚪############'],
                       ['#            #'],
                       ['#####  #######'],
                       ['#      #     #'],
                       ['#   ######   #'],
                       ['#            🔓'],
                       ['####### ######'],
                       ['      # #     '],
                       ['      ###     ']]
        self.lemmings = [Lemming(1, 1, 1) for _ in range(nblem)]
        self.running = True
        self.nblem = nblem
        self.nbexit = 0

    def affiche(self):
        [print(i) for i in self.grotte]

    def tour(self):
        if self.nbexit > self.nblem *.5:
            print('🎆🎇🎆🎇🎆🎇\n Vous avez gangne')
            self.running = False
        else:
            self.affiche()
        for e in self.lemmings:
            if self.grotte[e.l][0][e.c] == '🚪':
                Lemming.action(e, 1, 1, 1, self.grotte,False)
            elif self.grotte[e.l][0][e.c+e.d] == '🔓':
                Lemming.action(e,0,0,0, self.grotte)
                self.nbexit += 1
                self.lemmings.remove(e)
            else:
                if Case.libre(self.grotte, e.l+1, e.c):
                    Lemming.action(e, e.l+1, e.c, e.d, self.grotte)
                if e.d == 1:
                    if Case.libre(self.grotte, e.l, e.c+1):
                        Lemming.action(e, e.l, e.c+1, e.d, self.grotte)
                    else:
                        Lemming.action(e, e.l, e.c, -1, self.grotte)
                else:
                    if Case.libre(self.grotte, e.l, e.c-1):
                        Lemming.action(e, e.l, e.c-1, e.d, self.grotte)
                    else:
                        Lemming.action(e, e.l, e.c, 1, self.grotte)
        

    def demarre(self):
        while self.running:
            x = input(
                'appuyez sur 1 pour ajouter un lemming,q pour quitter ou tout autre touche pour continuez: ')
            if x == 'q':
                break
            elif x == '1':
                self.lemmings.append(Lemming(0, 1, 1))
            self.tour()


def main():
    Jeu1 = Jeu(10)
    Jeu.demarre(Jeu1)


if __name__ == '__main__':
    main()
