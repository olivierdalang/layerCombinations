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


    def __init__(self, manager):
        QDockWidget.__init__(self, "Layer combinations")

        #Keep reference of QGis' instances
        self.manager = manager


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
        #QObject.connect(self.combBox, SIGNAL("currentIndexChanged(QString)"), self.nameEdt.setText)

        QObject.connect(self.combBox, SIGNAL("activated(QString)"), self.manager.applyCombination)
        QObject.connect(self.manager, SIGNAL("combinationsListChanged(QString)"), self.combinationsListChanged )

        self.combinationsListChanged(self.manager.NONE_NAME)



    def toggle(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def combinationsListChanged(self, name):
        #Empty the comboBox
        self.combBox.clear()      
        #For each combination name, add it to the comboBox
        self.combBox.addItem( self.manager.NONE_NAME )

        for combination in self.manager.combinationsList:
            self.combBox.addItem( combination )

        search = self.combBox.findText(name)
        if search == -1 :
            self.combBox.setCurrentIndex( self.combBox.count()-1 )
        else:
            self.combBox.setCurrentIndex( search )


