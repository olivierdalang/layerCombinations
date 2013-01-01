# LayerCombinations #


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

### Example ###

An example file is provided : [layerCombinationsSample.zip](https://github.com/redlegoreng/layerCombinations/blob/master/layerCombinationsSample.zip?raw=true) 


## Todo ##

### Short term ###
- Test, test, test...
- The application of layer combinations is very slow in large files, see if it's possible to make it more fluid...
- Study if there's a cleaner way to store the layer combinations than having the combinationName as the xml tag name
- Visual return to know if the layer combination is up to date or if it has been updated (disable the update button if up to date)
- The way Map items' layer combinations are stored is a kind of hack... Is there a cleaner way to do this ?


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
- 2013-01-01 - Version 0.5 : the layer order is now properly taken into account

## Contribute ##
Github repository : https://github.com/redlegoreng/layerCombinations.git
