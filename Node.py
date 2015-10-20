import json


class Node:

    def __init__(self, line):
        """
            1 483 622 1 72 4 0 0 0 0
                => je suis du type 4, j'ai 0 lignes de définition + 1 pour le titre anyway
            1 488 671 2 73 2 7 0 0 0
                => je suis du type 2, j'ai 7 lignes de définition + 1 pour le titre
        """
        arg = line.split(" ")
        self.x = int(arg[1])
        self.y = int(arg[2])
        self.layer = int(arg[3])
        self.id = int(arg[4])
        self.typeLien = int(arg[5])
        self.nbLinesToRead = self.remainingNbLinesToRead = int(arg[6]) + 1  # On oublie pas +1 pour la ligne du nom de l'item
        self.name = ""
        self.params = []

    def addParam(self, line):
        if self.nbLinesToRead == self.remainingNbLinesToRead:
            self.name = line.strip()
        else:
            try:
                self.params.append(float(line))
            except Exception:
                self.params.append(line)
        self.nbLinesToRead -= 1

    def __repr__(self):
        """Représentation de notre objet. C'est cette chaîne qui sera affichée
        quand on saisit directement le dictionnaire dans l'interpréteur, ou en
        utilisant la fonction 'repr'"""

        lineJson = json.dumps({
            "id": self.id,
            "type": self.typeLien,
            "coords": [self.x, self.y],
            "nom": self.name,
            "params": self.params
        })
        return lineJson

    def __str__(self):
        """Fonction appelée quand on souhaite afficher le dictionnaire grâce
        à la fonction 'print' ou le convertir en chaîne grâce au constructeur
        'str'. On redirige sur __repr__"""

        return repr(self)

    def strForCsv(self):
        """ id,type,x,y,name,p1,p2,p3,p4,p5,p6,p7 """
        chaine = '{},{},{},{},"{}",'.format(self.id, self.typeLien, self.x, self.y, self.name)
        i = 0
        for p in self.params:
            if i > 0:
                chaine += ","
            chaine += str(p)
            i += 1
        return chaine
