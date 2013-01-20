# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

class LayerCombinationsManager(QObject):
    """
        This class manages the saving, the loading, the deleting and the applying of the layer combinations.

        It stores the following settings in the project's file :
        - List (QStringList) : list of the combination's names
        - Active (QString) : the name of the last active combination (will be restored on file open)
        - Combination-{mycomb1} (QStringList): list of visible layers ids in the combination {mycomb1}
        - Combination-{mycomb2}
        - Combination-...

        - LayerFolding-{mycomb1} (QStringList): list of expanded layers ids in the combination {mycomb1}
        - LayerFolding-{mycomb2}
        - LayerFolding-...

        - GroupFolding-{mycomb1} (QStringList): list of expanded group names in the combination {mycomb1}
        - GroupFolding-{mycomb2}
        - GroupFolding-... : 

        It emits the combinationsListChanged(Qstring) signal whenever the combination list changed.
        The QString sent is the name of the added layer (if a layer was added) or the NONE_NAME if a layer was removed.
        Widgets that display the list of layer combinations should be connected to that signal.

        When a combination is applied to a map, it stores the commbination's name as the map's layerset first item.
        The combination's named is marked with a '*' so it can be recognized as being a combination name and not a layer.tion name corresponding to the updated combination, it is refreshed.

        <ComposerMap keepLayerSet="true"
            <LayerSet>
                <Layer>*mycomb1</Layer>
                <Layer>a20121227214219700</Layer>
                <Layer>c20121227214219715</Layer>
                ...
            </LayerSet>
        </ComposerMap>

        This is not very clean and should be made in a better way if there is a better way...
        TODO : It seems than on some occasions, this layer list is refreshed, and the *mycomb1 element is removed (since it is not an existing layer)

        When a combination is updated, the plugin iterates through all the ComposerMaps, and if it's first layer is a combina
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

        self.applyCombination( self._loadActive() ) 
        self.combinationsListChanged.emit( self._loadActive() )

    def saveCombination(self, name):
        """
        Saves the all the visible layers in the combination, and if the combination is new, changes the combinations list
        """

        #QgsMessageLog.logMessage('Manager : adding combination '+name,'LayerCombinations')

        if not self.nameIsValid(name):
            return

        #We compute the actual combination by looping through all the layers, and storing all the visible layers' name
        layers = self.iface.legendInterface().layers()


        self._saveCombination(name, self._getVisibleLayersIds(), self._getExpandedLayersIds(), self._getExpandedGroupsIds())

        self.loadCombinationToMaps(name)

        if self.nameIsNew(name):
            self.combinationsList.append(name)
            self.combinationsList.sort()
            self._saveCombinations()
            self.combinationsListChanged.emit(name)

    def deleteCombination(self, name):
        """
        Deletes the combination and changes the combinationsList (removing the combination)
        """

        #QgsMessageLog.logMessage('Manager : deleting combination '+name,'LayerCombinations')

        self._deleteCombination(name)

        index = self.combinationsList.indexOf(name)
        if index != -1:
            self.combinationsList.removeAt(index)
            self._saveCombinations()
            self.combinationsListChanged.emit(self.NONE_NAME)

    def applyCombination(self, name):
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
        self._applyExpandedLayersIds(self._loadCombinationLayerFolding(name))
        self._applyExpandedGroupsIds(self._loadCombinationGroupFolding(name))


    def applyCombinationToMap(self, name, mapItem):
        """
        This applies a combination to a map.
        It changes the layerSet to the give combination name and saves the combination's name in the MapItem's layerSet
        """

        #QgsMessageLog.logMessage('Manager : applying combination to a mapItem '+name,'LayerCombinations')


        #self._saveForMap( mapItem.id(), name )

        if not self.nameIsValid(name) or self.nameIsNew(name):
            #We don't do anything if the name is not valid or if it does not exist...
            
            mapItem.setKeepLayerSet( False )
            mapItem.updateCachedImage()

        else:
        
            # We set the layerSet
            visibleLayers = self._loadCombination(name)

            mapItem.setLayerSet( visibleLayers )
            mapItem.setKeepLayerSet( True )
            # We refresh the image
            mapItem.updateCachedImage()

            # And we set the layerSet again, but this time with the marked combination name as first layer
            visibleLayers.prepend( self._markCombinationKey(name) )
            mapItem.setLayerSet( visibleLayers )

            # It seems the updateCachedImage() function cleans the layerSet by removing inexistant layers, so we have to change the layerset after the update.
            # But I'm not sure of this, maybe it's useless and we could do it at once...

        #mapItem.updateItem()
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
                    if len(item.layerSet()) > 0:
                        if item.layerSet()[0] == self._markCombinationKey(name):
                            self.applyCombinationToMap( name, item )


    
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
    def _saveForMap(self, mapId, name):
        QgsProject.instance().writeEntry('LayerCombinations','Map-'+str(mapId),name)
    def _loadForMap(self, mapId):
        return QgsProject.instance().readEntry('LayerCombinations','Map-'+str(mapId))[0]
    def _saveActive(self, name):
        QgsProject.instance().writeEntry('LayerCombinations','Active',name)
    def _loadActive(self):
        return QgsProject.instance().readEntry('LayerCombinations','Active')[0]
    def _saveCombination(self, name, visibleLayerList, folderLayerList, foldedGroupsList):
        QgsProject.instance().writeEntry('LayerCombinations',self._sanitizeCombinationKey(name),visibleLayerList)
        QgsProject.instance().writeEntry('LayerCombinations',self._sanitizeLayerFoldingKey(name),folderLayerList)
        QgsProject.instance().writeEntry('LayerCombinations',self._sanitizeGroupFoldingKey(name),foldedGroupsList)
    def _deleteCombination(self,name):
        QgsProject.instance().removeEntry('LayerCombinations',self._sanitizeCombinationKey(name))
        QgsProject.instance().removeEntry('LayerCombinations',self._sanitizeLayerFoldingKey(name))
        QgsProject.instance().removeEntry('LayerCombinations',self._sanitizeGroupFoldingKey(name))
    def _loadCombination(self, name):
        return QgsProject.instance().readListEntry('LayerCombinations',self._sanitizeCombinationKey(name))[0]
    def _loadCombinationLayerFolding(self, name):
        return QgsProject.instance().readListEntry('LayerCombinations',self._sanitizeLayerFoldingKey(name))[0]
    def _loadCombinationGroupFolding(self, name):
        return QgsProject.instance().readListEntry('LayerCombinations',self._sanitizeGroupFoldingKey(name))[0]
    def _saveCombinations(self):
        QgsProject.instance().writeEntry('LayerCombinations','List',self.combinationsList)
    def _loadCombinations(self):
        return QgsProject.instance().readListEntry('LayerCombinations','List')[0]
    def _sanitizeCombinationKey(self,key):
        """
        Commodity function.
        The entry key are used as XML tags ! So they should have no space and no special character.
        This can make QGis files unreadable !!
        """
        return 'Combination-'+self._sanitizeKey(key)
    def _sanitizeLayerFoldingKey(self,key):
        """
        Commodity function.
        The entry key are used as XML tags ! So they should have no space and no special character.
        This can make QGis files unreadable !!
        """
        return 'LayerFolding-'+self._sanitizeKey(key)
    def _sanitizeGroupFoldingKey(self,key):
        """
        Commodity function.
        The entry key are used as XML tags ! So they should have no space and no special character.
        This can make QGis files unreadable !!
        """
        return 'GroupFolding-'+self._sanitizeKey(key)
    def _sanitizeKey(self, key):
        # This produces a string that can be used as XML tag name so we can use it as name for the combinations...
        # It's not very readable when there are a lot of special characters but it's only for the project xml file
        sanitizedKey = QString(QUrl.toPercentEncoding(key))
        sanitizedKey.replace(QRegExp("[^a-zA-Z0-9]"),'_')
        return sanitizedKey
    def _markCombinationKey(self,key):
        """
        Commodity function.
        We use a little hack to store the layer combination in the composer's map : actually, the layerCombination is stored as a normal layer. So we have to mark it, so we can recognize it is the layer combination
        """
        marked = QString(key) #key is a QString and is passed by reference ! So we will work on a copy of it...
        marked.prepend('*')
        return marked
    def _markedCombinationKey(self, name):
        """
        Commodity function.
        This returns the combination corresponding to the marked combination, or none if the given element is not a marked combination.
        """
        if len(name)==0 or name[0] != '*':
            return None 
        else:
            return name[1:]


