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

class LcCanvasBase():
    """
    This palette is the interface for saving and restoring layers visibilities.

    """


    def __init__(self, manager):

        #Keep reference of QGis' instances
        self.manager = manager

        #Create the main UI elements
        self.combBox = QComboBox()
        self.nameEdt = QLineEdit("New combination")
        self.saveBtn = QToolButton()
        self.saveBtn.setText("Save")
        self.deleBtn = QToolButton()
        self.deleBtn.setText("Delete")
        self.foldChk = QCheckBox()
        #self.foldChk = QToolButton() # we can also display is as a button
        #self.foldChk.setCheckable( True )
        self.foldChk.setText("Fold")
        self.foldChk.setChecked( True )

        #Connect the main UI elements
        self.saveBtn.pressed.connect(self.saveCombination)
        self.deleBtn.pressed.connect(self.deleteCombination)
        self.nameEdt.textChanged[str].connect(self.nameChanged)

        self.combBox.currentIndexChanged[str].connect(self.nameEdt.setText)

        self.combBox.activated[str].connect(self.comboBoxActivated)
        self.manager.combinationsListChanged[str].connect(self.combinationsListChanged)


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
            if self.manager.nameIsNew(name):
                self.saveBtn.setText('Save')
                self.deleBtn.setEnabled(False)
            else:
                self.saveBtn.setText('Update')
                self.deleBtn.setEnabled(True)

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
        confirmBox = QMessageBox()
        confirmBox.setIcon(QMessageBox.Warning)
        confirmBox.setText("Are you sure you want to delete the combination '%s' ?" % self.combBox.currentText())
        confirmBox.setInformativeText("There is no way to restore this change. Maps that use this combination will keep that layer set as locked.")
        confirmBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        confirmBox.setDefaultButton(QMessageBox.Cancel)

        if confirmBox.exec_() == QMessageBox.Ok:
            self.manager.deleteCombination( self.combBox.currentText() )





