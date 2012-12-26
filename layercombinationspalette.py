# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LayerCombinationsDialog
                                 A QGIS plugin
 Store and restore layer visibilities
                             -------------------
        begin                : 2012-12-26
        copyright            : (C) 2012 by Olivier Dalang
        email                : olivier.dalang@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

# create the dialog for zoom to point


class LayerCombinationsPalette(QDockWidget):
    """
    This palette manage the storage and retrieval of layer's visibilities combinations.

    It stores the following settings in the project file :

    KEY                     VALUE
    combinations            serialized list of all layer combination's names (should reflect the ComboBox's content)
    [combination's name]    serialized list of all visible layer's names (the key corresponds to the combination's name)

    """

    NONE_NAME = '- NONE -'
    INVALID_NAMES = ['', NONE_NAME]

    def __init__(self, iface):
        QDockWidget.__init__(self, "Layer combinations")

        #Keep reference of QGis' instances
        self.legend = iface.legendInterface()
        self.proj = QgsProject.instance()

        #Setup the DockWidget
        mainWidget = QWidget()
        self.layout = QGridLayout()
        mainWidget.setLayout(self.layout)
        self.setWidget(mainWidget)

        #Create the main UI elements
        self.combBox = QComboBox()
        self.nameEdt = QLineEdit("New layer combination")
        self.saveBtn = QPushButton("Save")
        self.deleBtn = QPushButton("Delete")

        #Layout the main UI elements
        self.layout.addWidget(self.combBox,0,0)
        self.layout.addWidget(self.deleBtn,0,1)
        self.layout.addWidget(self.nameEdt,1,0)
        self.layout.addWidget(self.saveBtn,1,1)

        #Connect the main UI elements
        QObject.connect(self.saveBtn, SIGNAL("pressed()"), self.saveCombination)
        QObject.connect(self.deleBtn, SIGNAL("pressed()"), self.deleteCombination)
        QObject.connect(self.nameEdt, SIGNAL("textChanged(QString)"), self.nameChanged)
        QObject.connect(self.combBox, SIGNAL("currentIndexChanged(int)"), self.selectionChanged)

        QObject.connect(self.proj, SIGNAL("readProject(QDomDocument)"), self.loadCombinationsList) #we have to reload the list when a project is opened/closed

        #Do the initial load of the entries
        self.loadCombinationsList()


    def nameChanged(self, name):
        """
        This is called when the combination's name changes.
        It updates the buttons regarding to the new name.
        If the name is invalid, it disables the save button.
        If the name is valid but does not already exist, the save button is set to "Save". If it already exists, it is set to "Update"
        """

        if name in self.INVALID_NAMES:
            self.saveBtn.setEnabled(False)
        else:
            self.saveBtn.setEnabled(True)
            if self.combBox.findText(name) == -1:
                self.saveBtn.setText('Save')
            else:
                self.saveBtn.setText('Update')

    def saveCombination(self):
        """
        Saves the current combination.
        If it's new, adds it to the comboBox and saves the combinations list.
        """

        #Get the name 
        name = self.nameEdt.text()

        #If the name is invalid, we don't save it
        if name in self.INVALID_NAMES:
            return

        #We compute the actuel combination by looping through all the layers, and storing all the visible layers' name
        layers = QgsMapLayerRegistry.instance().mapLayers()
        data = []
        for key in layers:
            if self.legend.isLayerVisible( layers[key] ):
                data.append( str(key) )
            else:
                pass

        #We save that in the settings under the name of the combination
        self.saveList(name, data)


        #We check if the combination already exists...
        search = self.combBox.findText(name)

        if search == -1 :
            #The combination was new, so we have to add it to the combobox
            self.combBox.addItem( name )
            self.combBox.setCurrentIndex( self.combBox.count()-1 )

            #And we save the combinations to the project's file
            self.saveCombinationsList()
        else:
            #The combination already existed, so there's nothing to save
            self.combBox.setCurrentIndex( search )

    def deleteCombination(self):
        """
        Removes the current combination list and saves the list
        """

        #TODO : remove the combination itself also !

        name = self.combBox.currentText()
        if name in self.INVALID_NAMES:
            #We don't delete invalid names
            return

        #We remove the current item from the comboBox
        self.combBox.removeItem( self.combBox.currentIndex() )

        #And we save the combinations to the project's file
        self.saveCombinationsList()

    def selectionChanged(self, int):
        """
        When the selection changes from the comboBox, we have to update the layer's visibilities
        """

        name = self.combBox.currentText()
        self.nameEdt.setText(name)

        if name in self.INVALID_NAMES:
            #We don't update anywhing for invalid names
            self.deleBtn.setEnabled(False)
            return


        self.deleBtn.setEnabled(True)

        # We get the store layer combination, which contains actually the list of visible layers
        visibleLayers = self.getList(name)

        # We loop through all the layers in the project
        layers = QgsMapLayerRegistry.instance().mapLayers()
        for key in layers:
            # And for each layer, we set it's visibility, depending if it was in the combination
            if key in visibleLayers:
                self.legend.setLayerVisible( layers[key], True )
            else:
                self.legend.setLayerVisible( layers[key], False )

    def loadCombinationsList(self):
        """
        Loads the saved combinations list from the project's file into the comboBox
        """

        #Empty the comboBox
        self.combBox.clear()

        #Get all combinations' names in a list from the settings
        storedCombinations = self.getList('combinations')

        #For each combination name, add it to the comboBox
        self.combBox.addItem( '- NONE -' )
        for combination in storedCombinations:
            self.combBox.addItem( combination )

    def saveCombinationsList(self):
        """
        Saves the combinations from the comboBox to the project's file
        """

        #Store all the combinations' names in a list
        combinations = []
        for i in range(0,self.combBox.count()):
            combinationName = str( self.combBox.itemText(i) )
            if combinationName != '- NONE -':
                combinations.append( combinationName )

        #Save that list in the project's file
        self.saveList('combinations', combinations)

    def saveList(self, key, data):
        """
        Commodity function.
        Saves a list as an project settings entry
        """

        serializedData = "|".join(data) #TODO : serialize this in a cleaner way (we'll have a bug if the key contains the separator)
        self.proj.writeEntry('LayerCombinations',key,serializedData)
    def getList(self, key):
        """
        Commodity function.
        Retrieves a project settings entry as a list
        """

        serializedData = str(self.proj.readEntry("LayerCombinations", key, "")[0]).strip()
        if len(serializedData) == 0:
            return []
        else:
            data = serializedData.split('|')    #TODO : unserialize this in a cleaner way (we'll have a bug if the key contains the separator)
            return data

