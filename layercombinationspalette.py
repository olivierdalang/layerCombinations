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
    def __init__(self, iface):
        QDockWidget.__init__(self, "Layer combinations")

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
        QObject.connect(self.saveBtn, SIGNAL("pressed()"), self.save)
        QObject.connect(self.deleBtn, SIGNAL("pressed()"), self.delete)
        QObject.connect(self.nameEdt, SIGNAL("textChanged(QString)"), self.textChanged)
        QObject.connect(self.combBox, SIGNAL("currentIndexChanged(int)"), self.changed)
        QObject.connect(self.proj, SIGNAL("readProject(QDomDocument)"), self.load)

        #Do the initial load of the entries
        self.load()

    def textChanged(self, text):
        if text == '' or text == '- NONE -':
            self.saveBtn.setEnabled(False)
        else:
            self.saveBtn.setEnabled(True)
            if self.combBox.findText(text) == -1:
                self.saveBtn.setText('Save')
            else:
                self.saveBtn.setText('Update')


    def load(self):
        """
        Loads the saved combinations in the combobox
        """

        self.combBox.clear()

        data = self.getEntryAsList('combinations')

        self.combBox.addItem( '- NONE -' )
        for combination in data:
            self.combBox.addItem( combination )


    def save(self):
        """
        Saves a the combination
        """

        text = self.nameEdt.text()
        if text == '- NONE -' or text == '':
            return

        layers = QgsMapLayerRegistry.instance().mapLayers()
        data = []
        for key in layers:
            if self.legend.isLayerVisible( layers[key] ):
                data.append( str(key) )
            else:
                pass

        self.saveListAsEntry(text, data)


        search = self.combBox.findText(text)

        if search == -1 : # The entry does not already exist...
            self.combBox.addItem( text )
            self.combBox.setCurrentIndex( self.combBox.count()-1 )

            data = []
            for i in range(0,self.combBox.count()):
                combName = str( self.combBox.itemText(i) )
                if combName != '- NONE -':
                    data.append( combName )
            self.saveListAsEntry('combinations', data)
                
           
            #TODO : add the entry to the combination list
        else:   # The entry already exists...
            #TODO : ask for confirmation (replace)
            self.combBox.setCurrentIndex( search )

    def delete(self):
        text = self.combBox.currentText()
        if text == '- NONE -':
            return

        self.combBox.removeItem( self.combBox.currentIndex() )
        #TODO : remove the entry to the combination list

    def changed(self, int):
        text = self.combBox.currentText()
        self.nameEdt.setText(text)

        if text == '- NONE -':
            self.deleBtn.setEnabled(False)
            return
            
        self.deleBtn.setEnabled(True)

        data = self.getEntryAsList(text)
        layers = QgsMapLayerRegistry.instance().mapLayers()
        for key in layers:
            if key in data:
                self.legend.setLayerVisible( layers[key], True )
            else:
                self.legend.setLayerVisible( layers[key], False )



    def saveListAsEntry(self, key, data):
        """
        Saves a list as an project settings entry
        """
        #TODO : serialize this in a cleaner way (we'll have a bug if the key contains the separator)
        serializedData = "|".join(data)
        self.proj.writeEntry('LayerCombinations',key,serializedData)
        #QgsMessageLog.logMessage('SAVE : '+key+" => "+serializedData, 'LayerCombinations')
    def getEntryAsList(self, key):
        """
        Retrieves a project settings entry as a list
        """
        serializedData = str(self.proj.readEntry("LayerCombinations", key, "")[0]).strip()
        #QgsMessageLog.logMessage('READ : '+key+" => "+serializedData, 'LayerCombinations')
        if len(serializedData) == 0:
            #QgsMessageLog.logMessage('this is no data', 'LayerCombinations')
            return []
        else:
            #TODO : unserialize this in a cleaner way (we'll have a bug if the key contains the separator)
            data = serializedData.split('|')
            #QgsMessageLog.logMessage('this is '+str(len(data)) + ' items', 'LayerCombinations')
            return data

