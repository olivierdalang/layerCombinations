# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LayerCombinations
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
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from layercombinationsmanager import LayerCombinationsManager
from layercombinationspalette import LayerCombinationsPalette
from layercombinationspaletteforcomposer import LayerCombinationsPaletteForComposer


class LayerCombinations(QObject):

    combinationsListChanged = pyqtSignal()


    def __init__(self, iface):
        QObject.__init__(self)

        #QgsMessageLog.logMessage('Loading...','LayerCombinations')

        # Save reference to the QGIS interface
        self.iface = iface

        # this will hold the combinations list
        self.manager = LayerCombinationsManager(self.iface)

        # Create the dock widget and keep reference
        self.dockWidget = LayerCombinationsPalette(self.manager)

        # we have to reload the list when a project is opened/closed
        QObject.connect(self.iface, SIGNAL("projectRead()"), self.manager.loadCombinations) #we have to reload the list when a project is opened/closed

        #and we start by reloading the list
        self.manager.loadCombinations()

        
    def initGui(self):
        """
        Creates the GUI for the main window
        """

        # Create the action that will toggle the plugin panel
        self.action = QAction(QIcon(":/plugins/layercombinations/icon.png"), "Show/hide the Layer Combinations panel", self.iface.mainWindow())
        QObject.connect(self.action, SIGNAL("triggered()"), self.dockWidget.toggle)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&Layer Combinations", self.action)

        # Add the plugin panel to the mainWindow
        self.iface.mainWindow().addDockWidget(Qt.LeftDockWidgetArea, self.dockWidget)  

    def unload(self):
        self.iface.mainWindow().removeDockWidget(self.dockWidget)
        self.iface.removePluginMenu("&Layer Combinations",self.action)
        self.iface.removeToolBarIcon(self.action)