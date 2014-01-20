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

class LcComposerPalette(QDockWidget):
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
        self.combBox.activated[str].connect(self.combBoxActivated)
        self.manager.combinationsListChanged[str].connect(self.combinationsListChanged)

        self.composer.selectedItemChanged[QgsComposerItem].connect(self.selectedItemChanged)
        #QObject.connect( qgsComposerView.composition(), SIGNAL('selectedItemChanged(QgsComposerItem*)'), dockWidgetForComposer.selectedItemChanged )

        self.combinationsListChanged(self.manager.NONE_NAME)


    def combinationsListChanged(self, name):
        """
        This is called when the manager updates the combinations list.
        We refrsh the comboBox's content...
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
        """
        This is called when the selection changed in the composer.
        Unfortunately, it is not called when the user deselects an element.
        Basically, we enable the comboBox if the selection contains at least a ComposerMap.
        If it contains a ComposerMap, we set the comboBox's current value tu this ComposerMap's saved layer combination (or to "no combination" if it has no layerCombination)
        """

        #QgsMessageLog.logMessage('SELECTION CHANGED','LayerCombinations')

        # By default, disable the comboBox and choose "- NONE -"
        self.combBox.setEnabled(False)
        self.combBox.setCurrentIndex( 0 )

        # Loop thourgh the selected items in search of a ComposerMap Item
        selectedItems = self.composer.composition().selectedComposerItems()
        firstItem = None
        for item in selectedItems:
            if item.type() ==  65641: #this is the type of ComposerMap 
                firstItem = item
                break

        # If a composer map was found in the selection
        if firstItem is not None:
            # Enable the comboBox
            self.combBox.setEnabled(True)

            assignedCombination = self.manager._assignedCombForMap( firstItem )
            if assignedCombination is not None:

                # We set the ComboBox's current item to that combination's name
                search = self.combBox.findText( assignedCombination )
                if search != -1 :
                    self.combBox.setCurrentIndex( search )
        else:
            # Disable the comboBox
            self.combBox.setEnabled(False)



    def combBoxActivated(self, name):
        """
        This is called when the user makes a choice in the ComboBox.
        It applies the combination to the map.
        """

        selectedItems = self.composer.composition().selectedComposerItems()
        for item in selectedItems:
            if item.type() ==  65641: #this is the type of ComposerMap 
                self.manager.applyCombinationToMap(name, item)





