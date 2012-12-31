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

class LayerCombinationsPaletteForComposer(QDockWidget):
    """
    This palette is the interfae for saving and restoring layers visibilities.

    """


    def __init__(self, manager, composer):
        QDockWidget.__init__(self, "Layer combinations")

        #Keep reference of QGis' instances
        self.manager = manager
        self.composer = composer


        #Setup the DockWidget
        mainWidget = QWidget()
        self.layout = QGridLayout()
        self.layout.setColumnStretch( 0, 10 )
        self.layout.setRowStretch( 1, 10 )
        mainWidget.setLayout(self.layout)
        self.setWidget(mainWidget)

        #Create the main UI elements
        self.combBox = QComboBox()

        #Layout the main UI elements
        self.layout.addWidget(self.combBox,0,0)

        #Connect the main UI elements
        QObject.connect(self.combBox, SIGNAL("activated(QString)"), self.combBoxActivated)
        QObject.connect(self.manager, SIGNAL("combinationsListChanged(QString)"), self.combinationsListChanged )


        QObject.connect( self.composer, SIGNAL('selectedItemChanged(QgsComposerItem*)'), self.selectedItemChanged )
        #QObject.connect( qgsComposerView.composition(), SIGNAL('selectedItemChanged(QgsComposerItem*)'), dockWidgetForComposer.selectedItemChanged )

        self.combinationsListChanged(self.manager.NONE_NAME)



    def toggle(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def combinationsListChanged(self, name):
        """
        When the combinationsList has changed, we have to update the comboBox...
        """

        previousName = self.combBox.currentText()
        #Empty the comboBox
        self.combBox.clear()      
        #For each combination name, add it to the comboBox
        self.combBox.addItem( self.manager.NONE_NAME )

        for combination in self.manager.combinationsList:
            self.combBox.addItem( combination )

        search = self.combBox.findText(previousName)
        if search == -1 :
            self.combBox.setCurrentIndex( 0 )
        else:
            self.combBox.setCurrentIndex( search )
            
            
    def selectedItemChanged(self,qgsComposerItem):

        #QgsMessageLog.logMessage('SELECTION CHANGED','LayerCombinations')


        self.combBox.setEnabled(False)
        self.combBox.setCurrentIndex( 0 )

        selectedItems = self.composer.composition().selectedComposerItems()
        firstItem = None
        for item in selectedItems:
            if item.type() ==  65641: #this is the type of ComposerMap 
                firstItem = item
                break

        if firstItem is not None:
            self.combBox.setEnabled(True)

            layerSet = firstItem.layerSet()

            if len(layerSet) > 0:
                markedCombinationName = self.manager._markedCombinationKey( layerSet[0] )

                if markedCombinationName is not None:
                    search = self.combBox.findText(markedCombinationName)
                    if search != -1 :
                        self.combBox.setCurrentIndex( search )


    def combBoxActivated(self, name):

        selectedItems = self.composer.composition().selectedComposerItems()
        for item in selectedItems:
            if item.type() ==  65641: #this is the type of ComposerMap 
                self.manager.applyCombinationToMap(name, item)





