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
from LcCanvasBase import LcCanvasBase

# create the dialog for zoom to point

class LcCanvasToolBar(QToolBar, LcCanvasBase):
    """
    This palette is an interface for saving and restoring layers visibilities.

    """


    def __init__(self, manager):
        QToolBar.__init__(self, "Layer combinations")
        LcCanvasBase.__init__(self, manager)

        self.nameEdt.setMaximumWidth(100)

        #Layout the main UI elements
        self.addWidget(self.combBox)
        self.addWidget(self.deleBtn)
        self.addWidget(self.nameEdt)
        self.addWidget(self.saveBtn)
        self.addWidget(self.foldChk)

    def addToiFace(self, iface):
        iface.mainWindow().addToolBar(Qt.TopToolBarArea,self)
    def removeFromiFace(self, iface):
        iface.mainWindow().removeToolBar(self)