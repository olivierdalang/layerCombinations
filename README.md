# LayerCombinations #

**Disclaimer** : use at your own risk, the plugin is in developpement. In case of problem, open your QGis file in a plain text editor, and remove everything between &lt;LayerCombinations&gt; and &lt;/LayerCombinations&gt;.

## Description ##

QGis plugin to store/restore layer visbilities.
These visibilities combinations can then be applied dynamically to maps items.


## Usage ##

To save a layer combination, enter a name and press "save".
To restore a layer combination, choose it from the drop down list.
To delete a layer combination, choose it from the drop down list and press "delete".
To update a layer combination, choose it from the drop down list, make your changes, and press "update"

Once there are at least one combination, you can select a map in the composer and assign a combination to it. When the combination is updated, the map is also dynamically updated.
Note that the layer order in the map corresponds to the layer order when the combination is saved. One has to update a combination to take into account a modified layer order.


## Feedback / bugs ##

Please send bugs and ideas on the issue tracker : https://github.com/redlegoreng/layerCombinations/issues

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


## Contribute ##

Help is welcome ! There's a serie of issues and ideas on the github repository : https://github.com/redlegoreng/layerCombinations.git
