# -*- coding: utf-8 -*-
# EDIS - a simple cross-platform IDE for C
#
# This file is part of EDIS
# Copyright 2014-2015 - Gabriel Acosta
# License: GPLv3 (see http://www.gnu.org/licenses/gpl.html)

from PyQt4.QtGui import (
    QDialog,
    QHBoxLayout,
    QToolButton,
    QLineEdit,
    QIcon
    )

from PyQt4.QtCore import (
    Qt,
    QPoint,
    SIGNAL
    )

from src import recursos


class PopupBusqueda(QDialog):

    def __init__(self, editor):
        QDialog.__init__(self, editor)
        self._editor = editor
        self.total = 0
        # Popup!
        self.setWindowFlags(Qt.Popup)
        box = QHBoxLayout(self)
        box.setContentsMargins(5, 5, 5, 5)
        self.line = CustomLineEdit(self)
        self.line.setMinimumWidth(200)
        box.addWidget(self.line)
        # Botones
        btn_previous = QToolButton()
        btn_previous.setIcon(QIcon(":image/up"))
        btn_next = QToolButton()
        btn_next.setIcon(QIcon(":image/down"))
        box.addWidget(btn_previous)
        box.addWidget(btn_next)

        # Posición
        qpoint = self._editor.rect().topRight()
        global_point = self._editor.mapToGlobal(qpoint)
        self.move(global_point - QPoint(self.width() + 180, 0))

        # Conexiones
        self.connect(self.line, SIGNAL("textEdited(QString)"), self._find)
        self.connect(self.line, SIGNAL("returnPressed()"), self._find_next)
        self.connect(btn_previous, SIGNAL("clicked()"), self._find_previous)
        self.connect(btn_next, SIGNAL("clicked()"), self._find_next)

    def _find(self):
        weditor = self._editor
        found = weditor.findFirst(self.word, False, False, False, False,
                                  True, 0, 0, True)
        if self.word:
            self.line.update(found)
        weditor.hilo_ocurrencias.buscar(self.word, weditor.text())

    def _find_next(self):
        weditor = self._editor
        weditor.findFirst(self.word, False, False, False, True,
                                  True, -1, -1, True)

    def _find_previous(self):
        weditor = self._editor
        weditor.findFirst(self.word, False, False, False, True,
                          False, -1, -1, True)
        weditor.findNext()

    @property
    def word(self):
        """ Devuelve el texto ingresado en el CustomLineEdit """

        return self.line.text()


class CustomLineEdit(QLineEdit):

    """ QLineEdit personalizado """

    def __init__(self, parent):
        super(CustomLineEdit, self).__init__()
        self._parent = parent

    def update(self, found):
        if not found:
            self.setStyleSheet('background: %s; border-radius: 3px' %
                               recursos.TEMA['error'])
        else:
            self.setStyleSheet('color: #dedede')

    def showEvent(self, event):
        super(CustomLineEdit, self).showEvent(event)
        self.setFocus()