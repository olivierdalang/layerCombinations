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
import qgis.utils
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from LcManager import LcManager
from LcComposerPalette import LcComposerPalette
from LcCanvasDockWidget import LcCanvasDockWidget
from LcCanvasToolBar import LcCanvasToolBar
from LcAbout import LcAbout


class LcMain(QObject):

    DOCKWIDGET = 0
    TOOLBAR = 1

    def __init__(self, iface):
        QObject.__init__(self)

        # Save reference to the QGIS interface
        self.iface = iface

        # this will hold the combinations list
        self.manager = LcManager(self.iface)


        # Create the dock widget and keep reference
        if QSettings().value('plugins/LayerCombinations/WidgetType',self.DOCKWIDGET) == self.TOOLBAR:
            self.widget = LcCanvasToolBar(self.manager)
        else:
            self.widget = LcCanvasDockWidget(self.manager)

        # This will hold the composers dock widgets
        self.compDockWidgets = []

        # Create the GUI in the map composer window when a Composer is added (also works for composers that are loaded at project opening)
        self.iface.composerAdded.connect( self.initComposerGui )

        # we have to reload the list when a project is opened/closed
        self.iface.projectRead.connect( self.manager.loadCombinations ) #we have to reload the list when a project is opened/closed
        self.iface.newProjectCreated.connect( self.manager.loadCombinations ) #we have to reload the list when a project is opened/closed

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

        # Create help action 
        self.helpAction = QAction( QIcon(":/plugins/layercombinations/about.png"), u"Help", self.iface.mainWindow())
        # connect the action 
        self.helpAction.triggered.connect( self.showHelp )
        # Add menu item
        self.iface.addPluginToMenu(u"&Layer Combinations", self.helpAction)

        # Create the action that allows to change the widget type
        self.changeWidgetAction = QAction("Change widget type", self.iface.mainWindow())
        self.changeWidgetAction.triggered.connect( self.changeWidget )
        self.iface.addPluginToMenu(u"&Layer Combinations", self.changeWidgetAction)

        # Create the action that will toggle the plugin panel
        self.action = QAction(QIcon(":/plugins/layercombinations/icon.png"), "Show/hide the Layer Combinations widgets", self.iface.mainWindow())
        self.action.triggered.connect( self.widget.toggle )
        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&Layer Combinations", self.action)


        # Add the widget to the mainWindow
        self.widget.addToiFace(self.iface)


    def changeWidget(self):
        """
        Reloads the plugin after changing the settings
        """

        if QSettings().value('plugins/LayerCombinations/WidgetType',self.TOOLBAR) == self.TOOLBAR:
            QSettings().setValue('plugins/LayerCombinations/WidgetType',self.DOCKWIDGET)
        else:
            QSettings().setValue('plugins/LayerCombinations/WidgetType',self.TOOLBAR)

        qgis.utils.reloadPlugin("layerCombinations")


    def showHelp(self):
        # Simply show the help window
        self.aboutWindow = LcAbout()  

    def initComposerGui(self, qgsComposerZoom):
        """
        Creates the GUI for the given Composer Main Window
        """

        dockWidgetForComposer = LcComposerPalette(self.manager, qgsComposerZoom)

        self.compDockWidgets.append(dockWidgetForComposer)

        qgsComposerZoom.composerWindow().addDockWidget(Qt.RightDockWidgetArea, dockWidgetForComposer )



    def unload(self):
        self.widget.removeFromiFace(self.iface)

        self.iface.removePluginMenu(u"&Layer Combinations", self.helpAction)
        self.iface.removePluginMenu(u"&Layer Combinations",self.changeWidgetAction)
        self.iface.removePluginMenu(u"&Layer Combinations",self.action)

        self.iface.removeToolBarIcon(self.action)


        #For all the composers, remove the layer combitionations dock window !
        if self.iface is not None:
            for compDockWidget in self.compDockWidgets:
                try:
                    # This throws a "RuntimeError: underlying C/C++ object has been deleted" when one quits QGIS... Not sure why ? But it does not matter...
                    compDockWidget.setParent(None)
                except RuntimeError:
                    continue
        self.compDockWidgets=[]


