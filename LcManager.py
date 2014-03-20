# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
import hashlib

class LcManager(QObject):
    """
        This class manages the saving, the loading, the deleting and the applying of the layer combinations.

        It stores the following settings in the project's file :

        <LayerCombinations>
            <Active type="QString">{combination_name}</Active>  :  the name of the last active combination (will be restored on file open)
            <Combinations>
                <Combination-{combination_name_hash}>
                    <VisibleLayers type="QStringList">          :  list of visible layers ids in the combination {combination_name}
                        <value>{layer_name}</value>
                        <value>{layer_name}</value>
                        ...
                    </VisibleLayers>
                    <ExpandedLayers type="QStringList">          :  list of expanded layers ids in the combination {combination_name}
                        <value>{layer_name}</value>
                        <value>{layer_name}</value>
                        ...
                    </ExpandedLayers>
                    <ExpandedGroups type="QStringList">          :  list of expanded groups ids in the combination {combination_name}
                        <value>{group_name}</value>
                        <value>{group_name}</value>
                        ...
                    </ExpandedGroups>
                    <Name type="QString">{combination_name}</Name>
                </Combination-{combination_name_hash}>
                ...
            </Combinations>
            <Assignations>                                      :  the associations between a map composer and a combination
                <Assignation-{composermap_uuid} type="QString">{combination_name}</Assignation-{composermap_uuid}>
                <Assignation-{composermap_uuid} type="QString">{combination_name}</Assignation-{composermap_uuid}>
                ...
            </Assignations>
        </LayerCombinations>

        It emits the combinationsListChanged(Qstring) signal whenever the combination list changed.
        The QString sent is the name of the added layer (if a layer was added) or the NONE_NAME if a layer was removed.
        Widgets that display the list of layer combinations should be connected to that signal.

        When a combination is updated, the plugin iterates through all the ComposerMaps, and if it has an assigned combination, it updates it.
    """

    combinationsListChanged = pyqtSignal('QString')

    NONE_NAME = '[NONE]'
    INVALID_NAMES = ['', NONE_NAME]

    def __init__(self, iface):
        QObject.__init__(self)

        self.iface = iface

        # this will hold the combinations list
        self.combinationsList = []

        # this will hold the visible layers before a combination was applied
        self.previousVisibleLayerList = None


    def loadCombinations(self):
        """
        Loads all the combinations from the file and emits the combinationsListChanged signal.
        """

        #QgsMessageLog.logMessage('Manager : loading combinations','LayerCombinations')

        self.combinationsList = self._loadCombinations()

        self.combinationsList.sort()

        #We could apply the default combination upon project loading...
        #...but this is disabled since it can cause a project to open in a different state than how it was when it was closed.
        #self.applyCombination( self._loadActive() ) 

        self.combinationsListChanged.emit( self._loadActive() )

    def saveCombination(self, name, saveFolding = True, saveSnapping = True, saveExtents = False):
        """
        Saves the all the visible layers in the combination, and if the combination is new, changes the combinations list
        """

        assert(self.nameIsValid(name)) #just to be sure...

        self._saveCombination(  name,
                                self._getVisibleLayersIds(), 
                                self._getExpandedLayersIds() if saveFolding else None, 
                                self._getExpandedGroupsIds() if saveFolding else None, 
                                self._getSnappingLayersIds() if saveSnapping else None, 
                                self._getExtents() if saveExtents else None
                             )

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

#    def userChangedVisibility(self):
#        """
#        TODO : 
#        -When the users changes visibility and/or folding manually, we keep that in the "- NONE -" combination.
#        -We also enable/disable the "update" button depending if the current visibilties/folding matches or not the selected combination.
#        See Workaround below
#        """
#        # We store the current combination as being the previous combination
#        self.previousVisibleLayerList = self._getVisibleLayersIds()
#        self.previousExpandedLayersList = self._getExpandedLayersIds()
#        self.previousExpandedGroupsList = self._getExpandedGroupsIds()
#        
#        #TODO  : We also enable/disable the "update" button depending if the current visibilties/folding matches or not the selected combination.

    def applyCombination(self, name, withFolding=True, withSnapping=True, withExtents=False):
        """
        Applies a combination by setting the layers to visible if they are in the selected layer combination and hiding it if absent from the layer combination
        """

        #QgsMessageLog.logMessage('Manager : applying combination '+name,'LayerCombinations')

        self._saveActive( name )

        if not self.nameIsValid(name):
            #We apply the NONE combination if the name is not valid...
            if self.previousVisibleLayerList is not None:
                self._applyVisibleLayersIds(self.previousVisibleLayerList)
                if withFolding:
                    self._applyExpandedLayersIds(self.previousExpandedLayersList)
                    self._applyExpandedGroupsIds(self.previousExpandedGroupsList)
                if withSnapping:
                    self._applySnappingLayersIds(self.previousSnappingOptionsList)
                if withExtents:
                    self._applyExtents(self.previousExtents)

                #Workaround : we don't have a signal for userChangedVisibility/Folding
                self.previousVisibleLayerList = None 
                #/Workaround
            #And that's it
            return

        if self.nameIsNew(name):
            #We don't do anything if it's a new combination
            return

        #Workaround : we don't have a signal for userChangedVisibility/Folding
        #So we store the NONE combination whenever a valid combination is choosen.
        #This does not work perfectly, since it won't take into accounts modificaiton to the visibility when a combination is selected.
        if self.previousVisibleLayerList is None:
            self.previousVisibleLayerList = self._getVisibleLayersIds()
            self.previousExpandedLayersList = self._getExpandedLayersIds()
            self.previousExpandedGroupsList = self._getExpandedGroupsIds()
            self.previousSnappingOptionsList = self._getSnappingLayersIds()
            self.previousExtents = self._getExtents()
        #/Workaround


        #Don't repaint the map canvas at each layer visibility change
        self.iface.mapCanvas().freeze()        

        # We loop through all the layers in the project
        self._applyVisibleLayersIds(self._loadCombination(name))
        if withFolding:
            self._applyExpandedLayersIds(self._loadCombinationLayerFolding(name))
            self._applyExpandedGroupsIds(self._loadCombinationGroupFolding(name))
        if withSnapping:
            self._applySnappingLayersIds(self._loadCombinationSnappingOptions(name))
        if withExtents:
            self._applyExtents(self._loadCombinationExtents(name))

        #But repaint the canvas once at the end.
        self.iface.mapCanvas().freeze( False )
        self.iface.mapCanvas().setDirty( True )
        self.iface.mapCanvas().refresh()

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

                    assignedComposition = self._assignedCombForMap( item )
                    if assignedComposition == name:
                        #If the composition assigned to that map is the same we are loading...                    
                        self.applyCombinationToMap( assignedComposition, item )     
    
    def nameIsNew(self, name):
        return name not in self.combinationsList
    def nameIsValid(self, name):
        return name not in self.INVALID_NAMES

    #Helper
    def _getVisibleLayersIds(self):
        visibleLayerIds = []
        layers = self.iface.legendInterface().layers()
        for layer in layers:
            if self.iface.legendInterface().isLayerVisible( layer ):
                visibleLayerIds.append( layer.id() )  #id() is a QSTRING
            else:
                pass
        return visibleLayerIds
    def _getExpandedLayersIds(self):
        expandedLayerIds = []
        if QGis.QGIS_VERSION_INT<10900:
            #we skip, because legendInterface().isLayerExpanded() does not exist in 1.8
            return expandedLayerIds
        layers = self.iface.legendInterface().layers()
        for layer in layers:
            if self.iface.legendInterface().isLayerExpanded( layer ):
                expandedLayerIds.append( layer.id() )  #id() is a QSTRING
        return expandedLayerIds
    def _getExpandedGroupsIds(self):
        expandedGroupsIds = []
        groups = self.iface.legendInterface().groups()
        i=0
        for group in groups:
            if self.iface.legendInterface().isGroupExpanded( i ): # /!\ THIS SEEMS TO BE BUGGY IN 1.8 !!! Does not work with subgroups !
                #expandedGroupsIds.append( QString(str(i)) )  #id() is a QSTRING
                expandedGroupsIds.append( group )  #id() is a QSTRING
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
            try:
                expandedGroupsIds.index(group)
                self.iface.legendInterface().setGroupExpanded( i, True ) # /!\ THIS SEEMS TO BE BUGGY IN 1.8 !!! Does not work with subgroups !
            except ValueError:
                self.iface.legendInterface().setGroupExpanded( i, False ) # /!\ THIS SEEMS TO BE BUGGY IN 1.8 !!! Does not work with subgroups !
            i+=1
    def _applyExtents(self, extents):
        try:
            rect = QgsRectangle(float(extents[0]),float(extents[1]),float(extents[2]),float(extents[3]))
            self.iface.mapCanvas().setExtent(rect)
        except IndexError, e:
            #in case no extent was existing, we don't do anything
            pass
        
    def _getSnappingLayersIds(self):
        snappingLayersIds = []
        layers = self.iface.legendInterface().layers()
        for layer in layers:
            if QgsProject.instance().snapSettingsForLayer(layer.id())[1]:
                snappingLayersIds.append(layer.id())
        return snappingLayersIds
    def _getExtents(self):
        rect = self.iface.mapCanvas().extent()
        return [str(rect.xMinimum()),str(rect.yMinimum()),str(rect.xMaximum()),str(rect.yMaximum())]
    def _applySnappingLayersIds(self, snappingLayersIds):

        # We loop through all the layers in the project
        layers = QgsMapLayerRegistry.instance().mapLayers()
        for key in layers:
            # And for each layer, we set it's visibility, depending if it was in the combination
            options = QgsProject.instance().snapSettingsForLayer( layers[key].id() )
            if key in snappingLayersIds:
                QgsProject.instance().setSnapSettingsForLayer( layers[key].id(),True,options[2],options[3],options[4],options[5])
                self.iface.legendInterface().setLayerExpanded( layers[key], True )
            else:
                QgsProject.instance().setSnapSettingsForLayer( layers[key].id(),False,options[2],options[3],options[4],options[5])


            

    #These funtions actually do the saving and loading in the project's files
    def _deleteForMap(self, mapId):
        QgsProject.instance().removeEntry('LayerCombinations','Assignations/'+self._uuidToken(mapId.uuid()))
    def _saveForMap(self, mapId, name):
        QgsProject.instance().writeEntry('LayerCombinations','Assignations/'+self._uuidToken(mapId.uuid()),name)
    def _assignedCombForMap(self, mapId):
        return QgsProject.instance().readEntry('LayerCombinations','Assignations/'+self._uuidToken(mapId.uuid()))[0]
    def _saveActive(self, name):
        QgsProject.instance().writeEntry('LayerCombinations','Active',name)
    def _loadActive(self):
        return QgsProject.instance().readEntry('LayerCombinations','Active')[0]
    def _saveCombination(self, name, visibleLayerList, foldedLayerList=None, foldedGroupsList=None, snappingOptionsList=None, extents=None):
        QgsProject.instance().writeEntry('LayerCombinations','Combinations/'+self._nameToken(name)+'/Name',name)
        QgsProject.instance().writeEntry('LayerCombinations','Combinations/'+self._nameToken(name)+'/VisibleLayers',visibleLayerList)
        if foldedLayerList is not None:
            QgsProject.instance().writeEntry('LayerCombinations','Combinations/'+self._nameToken(name)+'/ExpandedLayers',foldedLayerList)
        if foldedGroupsList is not None:
            QgsProject.instance().writeEntry('LayerCombinations','Combinations/'+self._nameToken(name)+'/ExpandedGroups',foldedGroupsList)
        if snappingOptionsList is not None:
            QgsProject.instance().writeEntry('LayerCombinations','Combinations/'+self._nameToken(name)+'/SnappingOptions',snappingOptionsList)
        if extents is not None:
            QgsProject.instance().writeEntry('LayerCombinations','Combinations/'+self._nameToken(name)+'/Extents',extents)
    def _deleteCombination(self,name):
        QgsProject.instance().removeEntry('LayerCombinations','Combinations/'+self._nameToken(name))
    def _loadCombination(self, name):
        return QgsProject.instance().readListEntry('LayerCombinations','Combinations/'+self._nameToken(name)+'/VisibleLayers')[0]
    def _loadCombinationLayerFolding(self, name):
        return QgsProject.instance().readListEntry('LayerCombinations','Combinations/'+self._nameToken(name)+'/ExpandedLayers')[0]
    def _loadCombinationGroupFolding(self, name):
        return QgsProject.instance().readListEntry('LayerCombinations','Combinations/'+self._nameToken(name)+'/ExpandedGroups')[0]
    def _loadCombinationSnappingOptions(self, name):
        return QgsProject.instance().readListEntry('LayerCombinations','Combinations/'+self._nameToken(name)+'/SnappingOptions')[0]
    def _loadCombinationExtents(self, name):
        return QgsProject.instance().readListEntry('LayerCombinations','Combinations/'+self._nameToken(name)+'/Extents')[0]
    def _loadCombinations(self):
        combinationsNames = []
        if QgsProject is not None:
            combEntries = QgsProject.instance().subkeyList('LayerCombinations','Combinations')
            for combEntry in combEntries:
                combName = QgsProject.instance().readEntry('LayerCombinations','Combinations/'+combEntry+'/Name')[0]
                combinationsNames.append( combName )
        return combinationsNames

    def _nameToken(self, inputName):
        #We make tokens because those strings are used as XML tags. Using a hash, we have no risk of invalid XML nor duplicate tokens.
        return 'Combination-'+hashlib.md5(inputName.encode('UTF-8')).hexdigest()
    def _uuidToken(self, inputAssignation):
        #We have to remove the {} from the uuid so it can be stored as XML tag.
        return 'Assignation-'+inputAssignation[1:-1]


