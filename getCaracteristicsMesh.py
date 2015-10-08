class Node:

    def __init__(self, line):
        """
            1 483 622 1 72 4 0 0 0 0
                => je suis du type 4, j'ai 0 lignes de définition + 1 pour le titre anyway
            1 488 671 2 73 2 7 0 0 0
                => je suis du type 2, j'ai 7 lignes de définition + 1 pour le titre
        """
        arg = line.split(" ")
        # print(arg)
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
            self.name = line
        else:
            try:
                self.params.append(float(line))
            except Exception:
                self.params.append(line)


class Link(Node):

    def __init__(self, line):
        """ on est pas mal comme un Noeud O.o
            1 331 196 414 268 2 4 27 10 0
                => je suis du type 2, j'ai 10 lignes de définition + 1 pour le titre anyway
            1 434 196 485 233 3 6 23 6 0
                => je suis du type 3, j'ai 6 lignes de définition + 1 pour le titre
        """
        arg = line.split(" ")
        # print(arg)
        self.PtA = [int(arg[1]), int(arg[2])]
        self.PtB = [int(arg[3]), int(arg[4])]
        self.typeLien = int(arg[5])
        self.nbLinesToRead = self.remainingNbLinesToRead = int(arg[8]) + 1  # On oublie pas +1 pour la ligne du nom de l'item
        self.name = ""
        self.params = []


def countUp(elem, typeLien, counts):
    try:
        counts[elem][typeLien] += 1
    except Exception:
        counts[elem][typeLien] = 1


def sumUp(elem, sums):
    try:
        sums[elem] += 1
    except Exception:
        sums[elem] = 1

counts = {
    "nodes": {},
    "links": {}
}
sums = {
    "nodes": {},
    "links": {}
}

enteringNodeDefinition = False
enteringLinkDefinition = False

readSomeMoreData = 0
skip = 0
for row in open("Grenoble.DTA"):
    ligne = row.replace("\n", "")
    if skip:
        skip -= 1
        print("pouf on saute :", ligne)
        continue
    if ligne == "END OF APPLICATION":
        print("On entre dans la définition des noeuds du réseau")
        enteringNodeDefinition = True
        skip = 2
        continue
    if enteringNodeDefinition and ligne == "0 0 0 0 0 0 0 0 0 0":  # On entre dans la définition des points, le premier, on peut le sauter
        print("On a fini la définition des Noeuds")
        print("On entre dans la définition des liens du réseau")
        enteringNodeDefinition = False
        enteringLinkDefinition = True
        skip = 2
        continue
    if enteringLinkDefinition and ligne == "0 0 0 0 0 0 0 0 0 0":  # On entre dans la définition des points, le premier, on peut le sauter
        print("On a fini la définition des Liens")
        enteringLinkDefinition = False
        continue

    if enteringNodeDefinition:  # On entre dans la définition des points, le premier vide a été sauté skip = 2
        if not readSomeMoreData:  # On a un nouveau noeud
            node = Node(ligne)
            countUp("nodes", node.typeLien, counts)
            sumUp("nodes", sums)
            readSomeMoreData = node.nbLinesToRead
        else:
            readSomeMoreData -= 1
            node.addParam(ligne)
    if enteringLinkDefinition:  # On entre dans la définition des liens, le premier vide a été sauté skip = 2
        if not readSomeMoreData:  # On a un nouveau noeud
            link = Link(ligne)
            countUp("links", link.typeLien, counts)
            sumUp("links", sums)
            readSomeMoreData = link.nbLinesToRead
        else:
            readSomeMoreData -= 1
            link.addParam(ligne)

print("counts:", counts)
print("sums:", sums)
