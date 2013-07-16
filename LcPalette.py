# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LayerCombinationsDialog
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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

# create the dialog for zoom to point

class LcPalette(QDockWidget):
    """
    This palette is the interfae for saving and restoring layers visibilities.

    """


    def __init__(self, manager):
        QDockWidget.__init__(self, "Layer combinations")

        #Keep reference of QGis' instances
        self.manager = manager


        #Setup the DockWidget
        mainWidget = QWidget()
        self.layout = QGridLayout()
        self.layout.setColumnStretch( 0, 1 )
        self.layout.setRowStretch( 3, 1 )
        mainWidget.setLayout(self.layout)
        self.setWidget(mainWidget)

        #Create the main UI elements
        self.combBox = QComboBox()
        self.nameEdt = QLineEdit("New layer combination")
        self.saveBtn = QPushButton("Save")
        self.deleBtn = QPushButton("Delete")
        self.foldChk = QCheckBox("Apply folding")
        self.foldChk.setChecked( True )

        #Layout the main UI elements
        self.layout.addWidget(self.combBox,0,0)
        self.layout.addWidget(self.deleBtn,0,1)
        self.layout.addWidget(self.nameEdt,1,0)
        self.layout.addWidget(self.saveBtn,1,1)
        self.layout.addWidget(self.foldChk,2,0,1,2)

        #Connect the main UI elements
        QObject.connect(self.saveBtn, SIGNAL("pressed()"), self.saveCombination)
        QObject.connect(self.deleBtn, SIGNAL("pressed()"), self.deleteCombination)
        QObject.connect(self.nameEdt, SIGNAL("textChanged(QString)"), self.nameChanged)

        QObject.connect(self.combBox, SIGNAL("currentIndexChanged(QString)"), self.nameEdt.setText)

        QObject.connect(self.combBox, SIGNAL("activated(QString)"), self.manager.applyCombination)
        QObject.connect(self.manager, SIGNAL("combinationsListChanged(QString)"), self.combinationsListChanged )



    def toggle(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def comboBoxActivated(self, name):
        self.manager.applyCombination( name, self.foldChk.isChecked() )


    def combinationsListChanged(self, name):
        """
        When the combinationsList has changed, we have to update the comboBox...
        """
        #Empty the comboBox
        self.combBox.clear()      
        #For each combination name, add it to the comboBox
        self.combBox.addItem( self.manager.NONE_NAME )

        for combination in self.manager.combinationsList:
            self.combBox.addItem( combination )

        search = self.combBox.findText(name)
        if search == -1 :
            self.combBox.setCurrentIndex( self.combBox.count()-1 )
        else:
            self.combBox.setCurrentIndex( search )

    def nameChanged(self, name):
        """
        This is called when the combination's name changes.
        It updates the buttons regarding to the new name.
        If the name is invalid, it disables the save and the delete button.
        If the name is valid but does not already exist, the save button is set to "Save". If it already exists, it is set to "Update"
        """

        if not self.manager.nameIsValid(name):
            self.saveBtn.setText('Invalid')
            self.saveBtn.setEnabled(False)
            self.deleBtn.setEnabled(False)
        else:
            self.saveBtn.setEnabled(True)
            self.deleBtn.setEnabled(True)
            if self.manager.nameIsNew(name):
                self.saveBtn.setText('Save')
            else:
                self.saveBtn.setText('Update')

    def saveCombination(self):
        """
        Saves the current combination.
        If it's new, adds it to the comboBox and saves the combinations list.
        """
        self.manager.saveCombination( self.nameEdt.text(), self.foldChk.isChecked() )

    def deleteCombination(self):
        """
        Removes the current combination list and saves the list
        """
        self.manager.deleteCombination( self.combBox.currentText() )





