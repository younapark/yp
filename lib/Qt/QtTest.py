import sys
from PyQt4 import QtCore, QtGui

from Close_ui import Ui_Dialog


class MyForm(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MyForm()
    myapp.show()
    sys.exit(app.exec_())
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'QtTest.ui'
#
# Created: Wed May 18 09:49:39 2016
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

