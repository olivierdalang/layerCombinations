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
from LcManager import LcManager
from LcCompPalette import LcCompPalette
from LcPalette import LcPalette
from LcAbout import LcAbout


class LcMain(QObject):


    def __init__(self, iface):
        QObject.__init__(self)

        # Save reference to the QGIS interface
        self.iface = iface

        # this will hold the combinations list
        self.manager = LcManager(self.iface)

        # Create the dock widget and keep reference
        self.dockWidget = LcPalette(self.manager)
        # This will hold the composers dock widgets
        self.compDockWidgets = []

        # Create the GUI in the map composer window when a Composer is added (also works for composers that are loaded at project opening)
        QObject.connect(self.iface, SIGNAL("composerAdded(QgsComposerView*)") ,self.initComposerGui)

        # we have to reload the list when a project is opened/closed
        QObject.connect(self.iface, SIGNAL("projectRead()"), self.manager.loadCombinations) #we have to reload the list when a project is opened/closed

        #and we start by reloading the list
        self.manager.loadCombinations()

        #and by loading the GUI for already loaded composers (should be usefull only when the plugin is loaded while composers are already existing)
        composers = self.iface.activeComposers()
        for composer in composers:
            self.initComposerGui(composer)

        
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

        self.initHelp()


    def initHelp(self):
        # Help Action
        # Create action 
        self.helpAction = QAction( QIcon(":/plugins/layercombinations/about.png"), u"Help", self.iface.mainWindow())
        # connect the action 
        QObject.connect(self.helpAction, SIGNAL("triggered()"), self.showHelp)
        # Add menu item
        self.iface.addPluginToMenu(u"&Layer Combinations", self.helpAction)

    def showHelp(self):
        # Simply show the help window
        self.aboutWindow = LcAbout()  

    def initComposerGui(self, qgsComposerView):
        """
        Creates the GUI for the given Composer Main Window
        """

        dockWidgetForComposer = LcCompPalette(self.manager, qgsComposerView)

        self.compDockWidgets.append(dockWidgetForComposer)

        qgsComposerView.composerWindow().addDockWidget(Qt.RightDockWidgetArea, dockWidgetForComposer )



    def unload(self):
        self.iface.mainWindow().removeDockWidget(self.dockWidget)
        self.iface.removePluginMenu("&Layer Combinations",self.action)
        self.iface.removeToolBarIcon(self.action)


        #For all the composers, remove the layer combitionations dock window !
        for compDockWidget in self.compDockWidgets:
            # This throws
            # RuntimeError: underlying C/C++ object has been deleted
            # So I disable it... Not sure wheter the plugin is well unloaded... But it shouldn't matter too much....
            #compDockWidget.close()
            #compDockWidget.setParent(None)
            pass
        self.compDockWidgets=[]


        self.iface.removePluginMenu(u"&Layer Combinations", self.helpAction)
