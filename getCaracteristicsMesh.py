from Node import *
from Line import *
from operator import attrgetter
import re
import os


# ####################################################
# On va s'occuper d'extraire les coordonées des arrêts
# ####################################################


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
    "nodes": 0,
    "links": 0
}

enteringNodeDefinition = False
enteringLinkDefinition = False

readSomeMoreData = 0
skip = 0
node = None
link = None
nodes = {}
links = {}

for row in open("output_GNE/Output.dta"):
    ligne = row.replace("\n", "")
    if skip:
        skip -= 1
        # print("pouf on saute :", ligne)
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
            if node:
                # print("node: ", node)
                nodes[node.name] = node
                countUp("nodes", node.typeLien, counts)
                sumUp("nodes", sums)
            node = Node(ligne)
            readSomeMoreData = node.nbLinesToRead
        else:
            readSomeMoreData -= 1
            node.addParam(ligne)
    if enteringLinkDefinition:  # On entre dans la définition des liens, le premier vide a été sauté skip = 2
        if not readSomeMoreData:  # On a un nouveau noeud
            if link:
                # print("link: ", link)
                links[link.id] = link
                countUp("links", link.typeLien, counts)
                sumUp("links", sums)
            link = Link(ligne, sums["links"]+1)
            readSomeMoreData = link.nbLinesToRead
        else:
            readSomeMoreData -= 1
            link.addParam(ligne)

if node:
    # print("node: ", node)
    nodes[node.name] = node
    countUp("nodes", node.typeLien, counts)
    sumUp("nodes", sums)
if link:
    # print("link: ", link)
    links[link.id] = link
    countUp("links", link.typeLien, counts)
    sumUp("links", sums)

print("RECAP:")
print("counts:", counts)
print("sums:", sums)

# ####################################################
# On récupère la charge sur les liens
# ####################################################

regex = re.compile("(  )+", re.IGNORECASE)
links2 = {}
for row in open("output_GNE/LinkLabl.txt"):
    ligne = row.replace("\n", "").strip()
    ligne = regex.sub(";", ligne)
    ligne = ligne.split(";")
    try:
        links2[ligne[0]]
        print("wow wow wow,", ligne[0], "existe déjà O.o")
    except Exception:
        pass
    links2[ligne[0]] = links[int(ligne[1])]
    # print(links2[ligne[0]])
print("len(links)", len(links))
links = {}
links = links2
print("len(links2)", len(links2))
skip = 4
for row in open("output_GNE/LinkVols.txt"):
    ligne = row.replace("\n", "").strip()
    if skip:
        skip -= 1
        # print("pouf on saute :", ligne)
        continue
    ligne = regex.sub(";", ligne)
    ligne = ligne.split(";")
    # print(ligne)
    links[ligne[0]].linkVolumes = {
        "AB": float(ligne[1]),
        "BA": float(ligne[2])
    }
    # print("link:",links[ligne[0]])

# ####################################################
# On exporte les arrêts et leurs coordonnées / params
# ####################################################

print("EXPORT Noeuds & Liens --> JSON")
nodes_json = open("output_json/nodes_json.js", "w")
links_json = open("output_json/links_json.js", "w")
print("var nodes_json = [", file=nodes_json)
print("var links_json = [", file=links_json)

nodesList = sorted(list(nodes.values()), key=attrgetter("typeLien"))
linksList = sorted(list(links.values()), key=attrgetter("typeLien"), reverse=True)

i = 0
for n in nodesList:
    print("    " + str(n) + ("," if i < len(nodesList)-1 else ""), file=nodes_json)
    i += 1
i = 0
for l in linksList:
    print("    " + str(l) + ("," if i < len(linksList)-1 else ""), file=links_json)
    i += 1

print("]", file=nodes_json)
print("]", file=links_json)
nodes_json.close()
links_json.close()
print(len(nodesList), "nodes dans output_json/nodes_json.js")
print(len(linksList), "links dans output_json/links_json.js")

print("EXPORT Noeuds & Liens --> CSV")
nodes_csv = open("output_csv/nodes.csv", "w")
links_csv = open("output_csv/links.csv", "w")
print("id,type,x,y,name,p1,p2,p3,p4,p5,p6,p7", file=nodes_csv)
print("id,type,ptAx,ptAy,ptBx,ptBy,name,linkVolAB,linkVolBA,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10", file=links_csv)

for n in nodesList:
    print(n.strForCsv(), file=nodes_csv)
for l in linksList:
    print(l.strForCsv(), file=links_csv)

nodes_csv.close()
links_csv.close()
print(len(nodesList), "nodes dans output_json/nodes.csv")
print(len(links), "links dans output_json/links.csv")

# ####################################################
# On va fusioner les résultats des zones
# ####################################################
print("On va fusioner les résultats des zones:")

zones = {}
readSomeMoreData = 0
skip = 4
count = 0
zone = None
for row in open("output_GNE/PsAndAs.txt"):
    ligne = row.replace("\n", "").replace("Ps:", "").replace("As:", "").strip()
    if skip:
        skip -= 1
        # print("pouf on saute :", ligne)
        continue
    if not readSomeMoreData:  # On a un nouveau noeud
        if zone:
            # print("zone: ", zone)
            zones[zone['name']] = zone
            count += 1
        ligne = regex.sub(";", ligne)
        ligne = ligne.split(";")
        # print(ligne)
        zone = {
            "name": ligne[0],
            "productions": {
                "HBW": float(ligne[1]),
                "HBNW": float(ligne[2]),
                "HBnoIdea": float(ligne[3]),
                "NHB": float(ligne[4])
            },
            "attractions": {
                "HBW": 0,
                "HBNW": 0,
                "HBnoIdea": 0,
                "NHB": 0
            }
        }
        readSomeMoreData = 1
    else:
        ligne = regex.sub(";", ligne)
        ligne = ligne.split(";")
        # print(ligne)
        readSomeMoreData -= 1
        zone['attractions'] = {
            "HBW": float(ligne[0]),
            "HBNW": float(ligne[1]),
            "HBnoIdea": float(ligne[2]),
            "NHB": float(ligne[3])
        }
if zone:
    # print("zone: ", zone)
    zones[zone['name']] = zone
    count += 1
skip = 4
for row in open("output_GNE/VehTrips.txt"):
    ligne = row.replace("\n", "").strip()
    if skip:
        skip -= 1
        # print("pouf on saute :", ligne)
        continue
    ligne = regex.sub(";", ligne)
    ligne = ligne.split(";")
    # print(ligne)
    zones[ligne[0]]["vehiculeTripsByZone"] = {
        "Leaving": float(ligne[1]),
        "Entering": float(ligne[2]),
        "IntraZonal": float(ligne[3])
    }


# ####################################################
# On exporte les zones et leurs counts
# ####################################################

print("EXPORT Zones Counts --> JSON")
zones_json = open("output_json/zones_json.js", "w")
print("var zones_json = [", file=zones_json)

zonesList = sorted(list(zones.values()), key=lambda t: t["name"])

i = 0
for l in zonesList:
    print("    " + json.dumps(l) + ("," if i < len(zones)-1 else ""), file=zones_json)
    i += 1

print("]", file=zones_json)
zones_json.close()
print(len(zones), "zones dans output_json/zones_json.js")

print("EXPORT Zones Counts --> CSV")
zones_csv = open("output_csv/zones.csv", "w")
print("name,prodHBW,prodHBNW,prodHBnoIdea,prodNHB,attracHBW,attracHBNW,attracHBnoIdea,attracNHB,vehTripsLeaving,vehTripsEntering,vehTripsIntraZonal", file=zones_csv)

for l in zonesList:
    print("{},{},{},{},{},{},{},{},{},{},{},{}".format(l["name"], l["productions"]["HBW"], l["productions"]["HBNW"], l["productions"]["HBnoIdea"], l["productions"]["NHB"], l["attractions"]["HBW"], l["attractions"]["HBNW"], l["attractions"]["HBnoIdea"], l["attractions"]["NHB"], l["vehiculeTripsByZone"]["Leaving"], l["vehiculeTripsByZone"]["Entering"], l["vehiculeTripsByZone"]["IntraZonal"]), file=zones_csv)

zones_csv.close()
print(len(zones), "zones dans output_json/zones.csv")


# ####################################################
# On va créer les matrices OD de temps entre les zones
# ####################################################
print("On va créer les matrices OD de temps entre les zones:")
# CTimes

zonesODkeys = []
zonesOD = []
isIdTxt = False
for row in open("output_GNE/NodeLabl.txt"):
    zoneName = row.replace("\n", "").replace("C ", "").strip()
    zoneOD = {
        "zoneName": zoneName,
        "id": zoneName.replace("Zone", "").replace(" - Universityy", ""),
        "od": ""
    }
    try:
        zoneOD["id"] = int(zoneOD["id"])
    except Exception:
        isIdTxt = True
    zonesODkeys.append(zoneOD["zoneName"])
    zonesOD.append(zoneOD)
# print(zonesOD)
zonesODorderQRS = []
for file in os.listdir("output_GNE"):
    if file.startswith("CTimes"):
        # print(file)
        for row in open("output_GNE/"+file):
            zoneOD = row.replace("\n", "").replace("C ", "").strip()
            zonesODorderQRS.append(zoneOD)
            zoneODarray = zoneOD.split(" ")
            idQRS = int(zoneODarray[0])-1
            thisZoneOD = zonesOD[idQRS]
            zoneODarray[0] = str(thisZoneOD["id"])
            # print(zoneODarray)
            thisZoneOD["od"] = ",".join(zoneODarray)
if isIdTxt:
    zonesOD = sorted(zonesOD, key=lambda t: t["zoneName"])
else:
    zonesOD = sorted(zonesOD, key=lambda t: t["id"])
# print(zonesOD)

newOrder = {}
i = 0
for z in zonesOD:
    newOrder[z["zoneName"]] = i
    i += 1
print(zonesODkeys)
print(newOrder)
for z in zonesOD:
    zoneOD = z["od"].split(',')
    # print(z["od"])
    id = zoneOD.pop(0)
    tempZoneOD = [0] * len(zoneOD)
    i = 0
    for k in zonesODkeys:
        tempZoneOD[newOrder[k]] = zoneOD[i]
        i += 1
    z["od"] = ",".join([id] + tempZoneOD)
    print(z["od"])


# ####################################################
# On exporte les zones et leurs counts
# ####################################################

print("EXPORT Zones OD --> JSON")
zonesODCTimes_json = open("output_json/zonesODCTimes_json.js", "w")
print("var zonesODCTimes_json = [", file=zonesODCTimes_json)

i = 0
for l in zonesOD:
    print("    " + json.dumps(l) + ("," if i < len(zones)-1 else ""), file=zonesODCTimes_json)
    i += 1

print("]", file=zonesODCTimes_json)
zonesODCTimes_json.close()
print(len(zonesOD), "paires OD dans output_json/zonesODCTimes_json.js")

print("EXPORT Zones OD ordered by zone name --> CSV")
zonesODCTimes_csv = open("output_csv/zonesODCTimes.csv", "w")

for z in zonesOD:
    print(z["od"], file=zonesODCTimes_csv)

zonesODCTimes_csv.close()
print(len(zonesOD), "paires OD dans output_json/zonesODCTimes.csv")

print("EXPORT Zones OD order QRS --> CSV")
zonesODCTimes_orderQRS_csv = open("output_csv/zonesODCTimes_orderQRS.csv", "w")

for z in zonesODorderQRS:
    print(z, file=zonesODCTimes_orderQRS_csv)

zonesODCTimes_orderQRS_csv.close()
print(len(zonesODorderQRS), "paires OD dans output_json/zonesODCTimes_orderQRS.csv")
