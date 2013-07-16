# LayerCombinations #

**Disclaimer** : use at your own risk, the plugin is in developpement. In case of problem, open your QGis file in a plain text editor, and remove everything between &lt;LayerCombinations&gt; and &lt;/LayerCombinations&gt;.

## Description ##

LayerCombinations is a QGis plugin to store/restore layer visbilities and folding.
These visibilities combinations can then be applied dynamically to maps items.


## Usage ##

To save a layer combination, enter a name and press "save".
To restore a layer combination, choose it from the drop down list.
To delete a layer combination, choose it from the drop down list and press "delete".
To update a layer combination, choose it from the drop down list, make your changes, and press "update".
To restore the previous (aka current) layer combination, select the "- NONE -" item.

Once there is at least one combination, you can select a map in the composer and assign a combination to it using the new docking pane at the bottom-right. When the combination is updated, the map is also dynamically updated.
Note that the layer order in the map corresponds to the layer order when the combination is saved. One has to update a combination to take into account a modified layer order.

When you add new groups/layers, they are considered to be hidden and folded by existing combinations.

If you want to avoid folding to be saved and applied, uncheck the "apply folding" checkbox.


## Feedback / bugs ##

Please report bugs and ideas on the issue tracker : https://github.com/olivierdalang/layerCombinations/issues

Or send me some feedback at : olivier.dalang@gmail.com


## Version history ##

- 2012-12-26 - version 0.1 : intial release
- 2012-12-28 - Version 0.2 : Fixed critical bug where special characters in the combination's name could make the QGis project to become unreadable... (as I said, it is experimental... :) )
- 2012-12-30 - Version 0.3 :
    - Rewriting of internal code
    - Saves the active combination to the file
    - Sorts the lists
- 2012-12-31 - Version 0.4 :
    - Layer Combinations can be assigned to Maps in the composer (!!)
    - Special characters are taken into account
- 2013-01-16 - Version 0.5 :
    - added help (via the plugin menu)
    - the layer order is now properly taken into account
- 2013-01-20 - Version 0.6 :
    - group folding is stored also (does not work for subgroups in 1.8)
    - layer folding is stored also (does not work at all in 1.8)
    - "current" layer combination is stored
- 2013-04-18 - Version 0.7 :
    - storage format improved (using the new composer's UUID), applying compositions to maps should be more robust
    - /!\ compatibility is broken with 0.6. A python script is provided to partialy translate old files (almost untested)
    - added "use folding" checkbox to temporarily disable the folding feature
    - several bug fixes
- 2013-06-08 - Version 0.8 :
    - adapted to Python API V2
    - corrected a bug where combination's application where lost upon reloading the project
    - "- NONE -" combination now also stores folding
    - /!\ compatibility is broken with 0.7.
    - /!\ now only works with QGIS 2.0 and higher



## Contribute ##

Help is welcome ! There's a serie of issues and ideas on the github repository : https://github.com/olivierdalang/layerCombinations.git
