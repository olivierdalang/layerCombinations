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
from layercombinationspalette import LayerCombinationsPalette


class LayerCombinations:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # Create the dialog and keep reference
        self.dockWidget = LayerCombinationsPalette(iface)
        # initialize plugin directory
        
    def initGui(self):



        # Create action that will start plugin configuration
        self.action = QAction(QIcon(":/plugins/layercombinations/icon.png"), "Toggle layer combinations panel", self.iface.mainWindow())
        # connect the action to the run method
        QObject.connect(self.action, SIGNAL("triggered()"), self.toggle)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&Layer combination", self.action)


        self.iface.mainWindow().addDockWidget(Qt.LeftDockWidgetArea, self.dockWidget)


    def toggle(self):
        if self.dockWidget.isVisible():
            self.dockWidget.hide()
        else:
            self.dockWidget.show()


    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.mainWindow().removeDockWidget(self.dockWidget)
        
        self.iface.removePluginMenu("&Layer combination",self.action)
        self.iface.removeToolBarIcon(self.action)
        #self.dockWidget = None
