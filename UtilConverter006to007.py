# -*- coding: utf-8 -*-
"""
/***************************************************************************

 LayerCombinationsDialog

This util converts the combinations from version 0.6 to 0.7 (only the combinations are converted, not their application on maps).
Names with strange characters won't display well...

"""

import sys
import xml.dom.minidom

testOnly = False

try:
    f = open(sys.argv[1], 'r')
    dom = xml.dom.minidom.parseString(f.read())
    f.close()
except Exception as e:
    print( 'Error reading file : '+str(e) )
    sys.exit(0)



class Combi(object):
    def __init__(self):
        self.layers = []
        self.layersFold = []
        self.groupsFold = []


inputLayerCombiNode = dom.getElementsByTagName('LayerCombinations')[0]

combinations = {}

for childNode in inputLayerCombiNode.childNodes:

    if childNode.nodeName.startswith('Combination'):
        combName = childNode.nodeName[len('Combination')+1:]
        if not combName in combinations:
            combinations[combName] = Combi()
        combinations[combName].layers = childNode.childNodes

    if childNode.nodeName.startswith('LayerFolding'):
        combName = childNode.nodeName[len('LayerFolding')+1:]
        if not combName in combinations:
            combinations[combName] = Combi()
        combinations[combName].layersFold = childNode.childNodes

    if childNode.nodeName.startswith('GroupFolding'):
        combName = childNode.nodeName[len('GroupFolding')+1:]
        if not combName in combinations:
            combinations[combName] = Combi()
        combinations[combName].groupsFold = childNode.childNodes



outputLayerCombiNode = dom.createElement('LayerCombinations')

combisNode = dom.createElement('Combinations')
outputLayerCombiNode.appendChild( combisNode )

for name in combinations:

    inputNode = combinations[name]

    combiNode = dom.createElement(name)
    combisNode.appendChild( combiNode )

    nameNode = dom.createElement('Name')
    nameNode.setAttribute('type','QString')
    nameNode.appendChild( dom.createTextNode(name) )
    combiNode.appendChild( nameNode )

    layersNode = dom.createElement('VisibleLayers')
    layersNode.setAttribute('type','QStringList')
    for layer in inputNode.layers:
        if layer.nodeType == xml.dom.Node.ELEMENT_NODE:
            layersNode.appendChild( layer )
    combiNode.appendChild( layersNode )

    groupsFoldNode = dom.createElement('ExpandedGroups')
    groupsFoldNode.setAttribute('type','QStringList')
    for layer in inputNode.layersFold:
        if layer.nodeType == xml.dom.Node.ELEMENT_NODE:
            groupsFoldNode.appendChild( layer )
    combiNode.appendChild( groupsFoldNode )

    layersFoldNode = dom.createElement('ExpandedLayers')
    layersFoldNode.setAttribute('type','QStringList')
    for layer in inputNode.groupsFold:
        if layer.nodeType == xml.dom.Node.ELEMENT_NODE:
            layersFoldNode.appendChild( layer )
    combiNode.appendChild( layersFoldNode )

propertiesNode = dom.getElementsByTagName('properties')[0]
propertiesNode.replaceChild( outputLayerCombiNode,inputLayerCombiNode )

if testOnly:
    print( outputLayerCombiNode.toprettyxml() )
    exit(0)

try:
    f = open(sys.argv[1], 'w')
    f.write( dom.toprettyxml() )
    f.close()
except Exception as e:
    print( 'Error writing file : '+str(e) )
    sys.exit(0)


print( 'Conversion successful !' )
sys.exit(0)

