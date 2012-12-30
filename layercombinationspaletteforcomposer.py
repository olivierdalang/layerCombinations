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
    This palette manage the storage and retrieval of layer's visibilities combinations.

    It stores the following settings in the project file :

    KEY                     VALUE
    CombinationsList            serialized list of all layer combination's names (should reflect the ComboBox's content)
    Combination[combination's name]    serialized list of all visible layer's names (the key corresponds to the combination's name)

    """

    NONE_NAME = '- NONE -'
    INVALID_NAMES = ['', NONE_NAME]

    def __init__(self):
        QDockWidget.__init__(self, "Layer combinations")

        #Keep reference of QGis' instances
        #self.legend = iface.legendInterface()
        #self.proj = QgsProject.instance()

        #Setup the DockWidget
        mainWidget = QWidget()
        self.layout = QGridLayout()
        self.layout.setColumnStretch( 0, 10 )
        self.layout.setRowStretch( 2, 10 )
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

