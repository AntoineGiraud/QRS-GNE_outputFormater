import json
from Node import *


class Link(Node):

    def __init__(self, line, id):
        """ on est pas mal comme un Noeud O.o
            1 331 196 414 268 2 4 27 10 0
                => je suis du type 2, j'ai 10 lignes de définition + 1 pour le titre anyway
            1 434 196 485 233 3 6 23 6 0
                => je suis du type 3, j'ai 6 lignes de définition + 1 pour le titre
        """
        arg = line.split(" ")
        # print(arg)
        self.id = id
        self.PtA = [int(arg[1]), int(arg[2])]
        self.PtB = [int(arg[3]), int(arg[4])]
        self.typeLien = int(arg[5])
        self.nbLinesToRead = self.remainingNbLinesToRead = int(arg[8]) + 1  # On oublie pas +1 pour la ligne du nom de l'item
        self.name = ""
        self.linkLabel = ""
        self.linkVolumes = {
            "AB": 0,
            "BA": 0
        }
        self.params = []

    def __repr__(self):
        """Représentation de notre objet. C'est cette chaîne qui sera affichée
        quand on saisit directement le dictionnaire dans l'interpréteur, ou en
        utilisant la fonction 'repr'"""

        lineJson = json.dumps({
            "id": self.id,
            "type": self.typeLien,
            "ptA": [self.PtA[0], self.PtA[1]],
            "ptB": [self.PtB[0], self.PtB[1]],
            "linkVolumes": self.linkVolumes,
            "nom": self.name,
            "params": self.params
        }, sort_keys=True)
        return lineJson

    def strForCsv(self):
        """ id,type,ptAx,ptAy,ptBx,ptBy,name,linkVolAB,linkVolBA,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10 """

        chaine = '{},{},{},{},{},{},"{}",{},{},'.format(self.id, self.typeLien, self.PtA[0], self.PtA[1], self.PtB[0], self.PtB[1], self.name, self.linkVolumes["AB"], self.linkVolumes["BA"])
        i = 0
        for p in self.params:
            if i > 0:
                chaine += ","
            chaine += str(p)
            i += 1
        return chaine
