# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

class LcManager(QObject):
    """
                    <VisibleLayers type="QStringList">
                        <value>A20130316224139550</value>
                        <value>B20130316224214241</value>
                        <value>C20130316224244007</value>
                    </VisibleLayers>
                    <ExpandedGroups type="QStringList"/>
                    <ExpandedLayers type="QStringList">
                        <value>A20130316224139550</value>
                    </ExpandedLayers>
                    <Name type="QString">6876</Name>
        This class manages the saving, the loading, the deleting and the applying of the layer combinations.

        It stores the following settings in the project's file :
        - Active (QString) : the name of the last active combination (will be restored on file open)
        - <Combinations>
        -   <{combination_name}>
        -       <VisibleLayers> (QStringList): list of visible layers ids in the combination {combination_name}
        -       <ExpandedGroups> (QStringList): list of expanded layers ids in the combination {combination_name}
        -       <ExpandedLayers> (QStringList): list of expanded groups ids in the combination {combination_name}
        -   </{combination_name}>
        -   ...
        - </Combinations>
        - <Assignations>
        -   <{mapItemUUID}> (QString): the name of the assigned combination
        - </Assignations>

        It emits the combinationsListChanged(Qstring) signal whenever the combination list changed.
        The QString sent is the name of the added layer (if a layer was added) or the NONE_NAME if a layer was removed.
        Widgets that display the list of layer combinations should be connected to that signal.

        When a combination is updated, the plugin iterates through all the ComposerMaps, and if it has an assigned combination, it updates it.
    """

    combinationsListChanged = pyqtSignal('QString')

    NONE_NAME = '- NONE -'
    INVALID_NAMES = ['', NONE_NAME]

    def __init__(self, iface):
        QObject.__init__(self)

        self.iface = iface

        # this will hold the combinations list
        self.combinationsList = QStringList()

        # this will hold the visible layers before a combination was applied
        self.previousVisibleLayerList = None


    def loadCombinations(self):
        """
        Loads all the combinations from the file, applies the saved Active combination and emits the combinationsListChanged signal.
        """

        #QgsMessageLog.logMessage('Manager : loading combinations','LayerCombinations')

        self.combinationsList = self._loadCombinations()

        self.combinationsList.sort()

        self.applyCombination( self._loadActive() ) 
        self.combinationsListChanged.emit( self._loadActive() )
    def saveCombination(self, name, saveFolding = True):
        """
        Saves the all the visible layers in the combination, and if the combination is new, changes the combinations list
        """

        #QgsMessageLog.logMessage('Manager : adding combination '+name,'LayerCombinations')

        if not self.nameIsValid(name):
            return

        #We compute the actual combination by looping through all the layers, and storing all the visible layers' name
        layers = self.iface.legendInterface().layers()

        if saveFolding:
            self._saveCombination(name, self._getVisibleLayersIds(), self._getExpandedLayersIds(), self._getExpandedGroupsIds())
        else:
            self._saveCombination(name, self._getVisibleLayersIds())

        self.loadCombinationToMaps(name)

        if self.nameIsNew(name):
            self.combinationsList.append(name)
            self.combinationsList.sort()
            self.combinationsListChanged.emit(name)
    def deleteCombination(self, name):
        """
        Deletes the combination and changes the combinationsList (removing the combination)
        """

        self._deleteCombination(name)
        self.combinationsList.remove(name)
        self.combinationsListChanged.emit(self.NONE_NAME)

    def applyCombination(self, name, withFolding = True):
        """
        Applies a combination by setting the layers to visible if they are in the selected layer combination and hiding it if absent from the layer combination
        """

        #QgsMessageLog.logMessage('Manager : applying combination '+name,'LayerCombinations')

        self._saveActive( name )

        if not self.nameIsValid(name) or self.nameIsNew(name):
            if self.previousVisibleLayerList is not None:
                self._applyVisibleLayersIds(self.previousVisibleLayerList)
                self.previousVisibleLayerList = None
            #We don't do anything if the name is not valid or if it does not exist...
            return

        # We store the current combination as being the previous combination
        if self.previousVisibleLayerList is None:
            self.previousVisibleLayerList = self._getVisibleLayersIds()
        

        # We loop through all the layers in the project
        self._applyVisibleLayersIds(self._loadCombination(name))
        if withFolding:
            self._applyExpandedLayersIds(self._loadCombinationLayerFolding(name))
            self._applyExpandedGroupsIds(self._loadCombinationGroupFolding(name))


    def applyCombinationToMap(self, name, mapItem):
        """
        This applies a combination to a map.
        It changes the layerSet to the give combination name and saves the combination's name in the MapItem's layerSet
        """

        #QgsMessageLog.logMessage('Manager : applying combination to a mapItem '+name,'LayerCombinations')


        if not self.nameIsValid(name) or self.nameIsNew(name):
            mapItem.setKeepLayerSet( False )
            self._deleteForMap( mapItem )
        else:        
            # We set the layerSet
            visibleLayers = self._loadCombination(name)

            mapItem.setLayerSet( visibleLayers )
            mapItem.setKeepLayerSet( True )


            self._saveForMap( mapItem, name )

        # We refresh the image
        mapItem.updateCachedImage()
        mapItem.itemChanged.emit()
        #mapItem.updateCachedImage()
    def loadCombinationToMaps(self, name):
        """
        This loops through all maps in all composers and if the map has the given layer combinations, it updates it.
        This is called when a layer combination is modified, so all maps are dynamically updated.
        """

        composers = self.iface.activeComposers()
        for composer in composers:
            items = composer.composition().items()

            for item in items:
                if item.type() == 65641:

                    assignedComposition = self._loadForMap( item )
                    if assignedComposition is not None:
                        self.applyCombinationToMap( assignedComposition, item )
    
    def nameIsNew(self, name):
        return name not in self.combinationsList
    def nameIsValid(self, name):
        return name not in self.INVALID_NAMES

    #Helper
    def _getVisibleLayersIds(self):
        visibleLayerIds = QStringList()
        layers = self.iface.legendInterface().layers()
        for layer in layers:
            if self.iface.legendInterface().isLayerVisible( layer ):
                visibleLayerIds.append( layer.id() )  #id() is a QSTRING
            else:
                pass
        return visibleLayerIds
    def _getExpandedLayersIds(self):
        expandedLayerIds = QStringList()
        if QGis.QGIS_VERSION_INT<10900:
            #we skip, because legendInterface().isLayerExpanded() does not exist in 1.8
            return expandedLayerIds
        layers = self.iface.legendInterface().layers()
        for layer in layers:
            if self.iface.legendInterface().isLayerExpanded( layer ):
                expandedLayerIds.append( layer.id() )  #id() is a QSTRING
            else:
                pass
        return expandedLayerIds
    def _getExpandedGroupsIds(self):
        expandedGroupsIds = QStringList()
        groups = self.iface.legendInterface().groups()
        i=0
        for group in groups:
            if self.iface.legendInterface().isGroupExpanded( i ): # /!\ THIS SEEMS TO BE BUGGY IN 1.8 !!! Does not work with subgroups !
                #expandedGroupsIds.append( QString(str(i)) )  #id() is a QSTRING
                expandedGroupsIds.append( group )  #id() is a QSTRING
            else:
                pass
            i+=1
        return expandedGroupsIds
    def _applyVisibleLayersIds(self, visibleLayersIds):
        # We loop through all the layers in the project
        layers = QgsMapLayerRegistry.instance().mapLayers()
        for key in layers:
            # And for each layer, we set it's visibility, depending if it was in the combination
            if key in visibleLayersIds:
                self.iface.legendInterface().setLayerVisible( layers[key], True )
            else:
                self.iface.legendInterface().setLayerVisible( layers[key], False )
    def _applyExpandedLayersIds(self, expandedLayersIds):
        if QGis.QGIS_VERSION_INT<10900:
            #we skip, because legendInterface().setLayerExpanded() does not exist in 1.8
            return

        # We loop through all the layers in the project
        layers = QgsMapLayerRegistry.instance().mapLayers()
        for key in layers:
            # And for each layer, we set it's visibility, depending if it was in the combination
            if key in expandedLayersIds:
                self.iface.legendInterface().setLayerExpanded( layers[key], True )
            else:
                self.iface.legendInterface().setLayerExpanded( layers[key], False )
    def _applyExpandedGroupsIds(self, expandedGroupsIds):
        
        groups = self.iface.legendInterface().groups()
        i=0
        for group in groups:
            #if expandedGroupsIds.indexOf(QString(str(i))) > -1:
            if expandedGroupsIds.indexOf(group) > -1:
                self.iface.legendInterface().setGroupExpanded( i, True ) # /!\ THIS SEEMS TO BE BUGGY IN 1.8 !!! Does not work with subgroups !
            else:
                self.iface.legendInterface().setGroupExpanded( i, False ) # /!\ THIS SEEMS TO BE BUGGY IN 1.8 !!! Does not work with subgroups !
            i+=1

    #These funtions actually do the saving and loading in the project's files
    def _deleteForMap(self, mapId):
        QgsProject.instance().removeEntry('LayerCombinations','Assignations/'+mapId.uuid())
    def _saveForMap(self, mapId, name):
        QgsProject.instance().writeEntry('LayerCombinations','Assignations/'+mapId.uuid(),name)
    def _loadForMap(self, mapId):
        return QgsProject.instance().readEntry('LayerCombinations','Assignations/'+mapId.uuid())[0]
    def _saveActive(self, name):
        QgsProject.instance().writeEntry('LayerCombinations','Active',name)
    def _loadActive(self):
        return QgsProject.instance().readEntry('LayerCombinations','Active')[0]
    def _saveCombination(self, name, visibleLayerList, folderLayerList=None, foldedGroupsList=None):
        QgsProject.instance().writeEntry('LayerCombinations','Combinations/'+name+'/Name',name)
        QgsProject.instance().writeEntry('LayerCombinations','Combinations/'+name+'/VisibleLayers',visibleLayerList)
        if folderLayerList is not None:
            QgsProject.instance().writeEntry('LayerCombinations','Combinations/'+name+'/ExpandedLayers',folderLayerList)
        if foldedGroupsList is not None:
            QgsProject.instance().writeEntry('LayerCombinations','Combinations/'+name+'/ExpandedGroups',foldedGroupsList)
    def _deleteCombination(self,name):
        QgsProject.instance().removeEntry('LayerCombinations','Combinations/'+name)
    def _loadCombination(self, name):
        return QgsProject.instance().readListEntry('LayerCombinations','Combinations/'+name+'/VisibleLayers')[0]
    def _loadCombinationLayerFolding(self, name):
        return QgsProject.instance().readListEntry('LayerCombinations','Combinations/'+name+'/ExpandedLayers')[0]
    def _loadCombinationGroupFolding(self, name):
        return QgsProject.instance().readListEntry('LayerCombinations','Combinations/'+name+'/ExpandedGroups')[0]
    def _loadCombinations(self):
        combinationsNames = []
        combEntries = QgsProject.instance().subkeyList('LayerCombinations','Combinations')
        for combEntry in combEntries:
            combName = QgsProject.instance().readEntry('LayerCombinations','Combinations/'+combEntry+'/Name')[0]
            combinationsNames.append( combName )
        return combinationsNames


