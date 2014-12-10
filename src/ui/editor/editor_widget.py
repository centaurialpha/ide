# -*- coding: utf-8 -*-
# EDIS - Entorno de Desarrollo Integrado Simple para C/C++
#
# This file is part of EDIS
# Copyright 2014 - Gabriel Acosta
# License: GPLv3 (see http://www.gnu.org/licenses/gpl.html)

from PyQt4.QtGui import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QStyle,
    QLabel,
    QComboBox,
    QWidget,
    QStackedWidget,
    QSizePolicy,
    QMessageBox,
    )

from PyQt4.QtCore import (
    SIGNAL,
    pyqtSignal,
    )

from src.ui.edis_main import EDIS
from src.ui.editor import editor


class Frame(QFrame):

    cambio_editor = pyqtSignal(int)

    def __init__(self):
        QFrame.__init__(self)
        box = QHBoxLayout(self)
        box.setContentsMargins(0, 0, 0, 0)
        box.setSpacing(0)

        self.combo = QComboBox()
        #box.addWidget(self.combo)

        self.posicion_cursor = "Lin: %d / Col: %d"
        self.lbl_cursor = QLabel(self.posicion_cursor % (0, 0))
        self.lbl_cursor.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        #box.addWidget(self.lbl_cursor)

        self.btn_cerrar = QPushButton(self.style().standardIcon(
                                        QStyle.SP_DialogCloseButton), '')
        self.btn_cerrar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        #box.addWidget(self.btn_cerrar)

        self.combo.currentIndexChanged[int].connect(self.current_changed)

    #def actualizar_linea_columna(self, linea, columna):
        #self.lbl_cursor.setText(self.posicion_cursor % (linea, columna))

    def agregar_item(self, texto):
        self.combo.addItem(texto)
        self.combo.setCurrentIndex(self.combo.count() - 1)

    def current_changed(self, indice):
        self.cambio_editor.emit(indice)


class EditorWidget(QWidget):

    guardar_editor_actual = pyqtSignal(name="Guardar_Editor_Actual")

    def __init__(self, parent=None):
        super(EditorWidget, self).__init__()
        self.parent = parent
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        self.no_esta_abierto = True

        # Instancias de editores
        self.editores = []

        #self.frame = Frame()
        #self.frame.hide()
        #vbox.addWidget(self.frame)

        self.stack = QStackedWidget()
        vbox.addWidget(self.stack)

        self.principal = EDIS.componente("principal")

        #self.connect(self.frame, SIGNAL("cambio_editor(int)"),
                    #self.cambiar_widget)

    def agregar_editor(self, nombre):
        #self.frame.show()
        editor_ = editor.crear_editor(nombre)
        self.editores.append(editor_)
        #self.frame.agregar_item(nombre)
        #self.connect(editor_, SIGNAL("cursorPositionChanged(int, int)"),
                    #self._actualizar_cursor)
        self.connect(editor_, SIGNAL("modificationChanged(bool)"),
                    self._editor_modificado)
        self.stack.addWidget(editor_)
        self.stack.setCurrentWidget(editor_)
        return editor_

    #def _actualizar_cursor(self, linea, columna):
        #self.frame.actualizar_linea_columna(linea + 1, columna)

    def _editor_modificado(self, valor=True):
        #combo = self.frame.combo
        #wid = self.stack.currentWidget()
        #if isinstance(wid, editor.Editor) and valor and self.no_esta_abierto:
            #combo.setItemText(combo.currentIndex(), '*' + combo.currentText())
            #wid.texto_modificado = True
        #else:
            #texto = combo.currentText().split('*')[-1]
            #combo.setItemText(combo.currentIndex(), texto)
        pass

    def cambiar_widget(self, indice):
        """ Cambia el widget del stack """

        self.stack.setCurrentIndex(indice)

    def resizeEvent(self, e):
        """
        Éste método es llamado automáticamente por Qt cuando se
        redimensiona el widget

        """

        super(EditorWidget, self).resizeEvent(e)
        self.setFixedHeight(self.parent.height())

    def currentWidget(self):
        """ Devuelve el widget actual """

        return self.stack.currentWidget()

    def currentIndex(self):
        """ Devuelve el índice del widget actual """

        return self.stack.currentIndex()

    def archivos_sin_guardar(self):
        """ Retorna una lista con los archivos modificados """

        archivos = list()
        for indice in range(len(self.editores)):
            editor = self.editores[indice]
            if editor.texto_modificado:
                archivos.append(editor.iD)
        return archivos

    def archivos_abiertos(self):
        """ Retorna una lista con los archivos abiertos """

        archivos = list()
        for archivo in self.editores:
            archivos.append(archivo.iD)
        return archivos

    def removeWidget(self, widget):
        """ Eliminar el widget del stack """

        self.stack.removeWidget(widget)

    def cerrar(self):
        """ Elimina el widget actual del contenedor """

        #FIXME: Usar logger
        indice = self.currentIndex()
        if indice != -1:
            SI = QMessageBox.Yes
            NO = QMessageBox.No
            CANCELAR = QMessageBox.Cancel
            self.cambiar_widget(indice)
            editor = self.currentWidget()
            if editor.texto_modificado:
                respuesta = QMessageBox.question(self, self.trUtf8(
                                                "El archivo no está guardado"),
                                                self.trUtf8("¿Guardar?"),
                                                SI | NO | CANCELAR)
                if respuesta == SI:
                    self.guardar_editor_actual.emit()
                    if editor.texto_modificado:
                        return
                elif respuesta == CANCELAR:
                    return
            del self.editores[indice]  # Eliminar de la lista
            self.removeWidget(editor)  # Eliminar del stack
            #FIXME: Hacer métodos para ésto
            #self.frame.combo.removeItem(self.frame.combo.currentIndex())
            # Ocultar frame
            #if self.currentIndex() == -1:
                #self.frame.hide()
        # Foco al widget actual
        if self.currentWidget() is not None:
            self.currentWidget().setFocus()