# -*- coding: utf-8 -*-
# EDIS - Entorno de Desarrollo Integrado Simple para C/C++
#
# This file is part of EDIS
# Copyright 2014-2015 - Gabriel Acosta
# License: GPLv3 (see http://www.gnu.org/licenses/gpl.html)

# Éste contenedor conoce los tres widgets laterales
# (Símbolos, Navegador y Explorador)

from PyQt4.QtGui import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QStackedWidget,
    QToolButton,
    QToolBar,
    QIcon
    )

from PyQt4.QtCore import SIGNAL, QSize

from src import recursos
from src.helpers.configuracion import ESettings
from src.ui.contenedores.lateral import (
    navegador,
    arbol_simbolos,
    explorador
    )
from src.ectags import ectags

instancia = None


# Singleton
def ContenedorLateral(*args, **kw):
    global instancia
    if instancia is None:
        instancia = _ContenedorLateral(*args, **kw)
    return instancia


class _ContenedorLateral(QWidget):

    def __init__(self, parent=None):
        super(_ContenedorLateral, self).__init__()
        self.ctags = ectags.Ctags()
        self._edis = parent
        box = QVBoxLayout(self)
        box.setContentsMargins(0, 0, 0, 0)
        box.setSpacing(0)

        hbox = QHBoxLayout()
        # Combo selector
        self.combo_selector = QComboBox()
        self.combo_selector.setObjectName("combo_selector")
        self.combo_selector.setStyleSheet(
            "QComboBox::drop-down{image: url(%s); top: 5px;}"
            % recursos.ICONOS['down'])
        hbox.addWidget(self.combo_selector, stretch=1)
        # Toolbar
        toolbar = QToolBar()
        toolbar.setObjectName("selector")
        toolbar.setIconSize(QSize(20, 20))
        tool_undock = QToolButton()
        tool_undock.setToolTip(self.tr("Undock widget"))
        tool_undock.setIcon(QIcon(recursos.ICONOS['undock']))
        toolbar.addWidget(tool_undock)
        hbox.addWidget(toolbar)

        box.addLayout(hbox)

        # Stacked
        self.stack = QStackedWidget()
        box.addWidget(self.stack)

        # Widgets
        self._arbol_simbolos = None
        if ESettings.get('gui/simbolos'):
            self.agregar_arbol_de_simbolos()
        self._navegador = None
        if ESettings.get('gui/navegador'):
            self.agregar_navegador()
        self._explorador = None
        if ESettings.get('gui/explorador'):
            self.agregar_explorador()

        self.actualizar()

        # Conexiónes
        self.combo_selector.currentIndexChanged[int].connect(
            lambda: self._cambiar_widget(self.combo_selector.currentIndex()))
        tool_undock.clicked.connect(self._undock)

    def actualizar(self):
        central = self._edis.central
        if self.stack.count() == 0:
            central.splitter_secundario.hide()
        else:
            central.splitter_secundario.show()

    def agregar_arbol_de_simbolos(self):
        if self._arbol_simbolos is None:
            self._arbol_simbolos = arbol_simbolos.ArbolDeSimbolos()
            self.combo_selector.addItem(self.tr("Símbolos"))
            self.stack.addWidget(self._arbol_simbolos)

    def agregar_navegador(self):
        if self._navegador is None:
            self._navegador = navegador.Navegador()
            self.combo_selector.addItem(self.tr("Navegador"))
            self.stack.addWidget(self._navegador)

            self.connect(self._edis.contenedor_editor,
                         SIGNAL("archivo_abierto(QString)"),
                         self._navegador.agregar)
            self.connect(self._edis.contenedor_editor,
                         SIGNAL("archivo_cerrado(int)"),
                         self._navegador.eliminar)
            self.connect(self._edis.contenedor_editor,
                         SIGNAL("cambiar_item(int)"),
                        self._navegador.cambiar_foco)
            self.connect(self._navegador,
                         SIGNAL("cambiar_editor(int)"),
                         self._edis.contenedor_editor.cambiar_widget)

    def agregar_explorador(self):
        if self._explorador is None:
            self._explorador = explorador.Explorador()
            self.combo_selector.addItem(self.tr("Explorador"))
            self.stack.addWidget(self._explorador)

            self.connect(self._explorador, SIGNAL("abriendoArchivo(QString)"),
                         self._edis.contenedor_editor.abrir_archivo)

    def eliminar_arbol_de_simbolos(self):
        if self._arbol_simbolos is not None:
            indice = self.stack.indexOf(self._arbol_simbolos)
            self.stack.removeWidget(self._arbol_simbolos)
            self.combo_selector.removeItem(indice)
            self._arbol_simbolos = None

    def eliminar_navegador(self):
        if self._navegador is not None:
            indice = self.stack.indexOf(self._navegador)
            self.stack.removeWidget(self._navegador)
            self.combo_selector.removeItem(indice)
            self._navegador = None

    def eliminar_explorador(self):
        if self._explorador is not None:
            indice = self.stack.indexOf(self._explorador)
            self.stack.removeWidget(self._explorador)
            self.combo_selector.removeItem(indice)
            self._explorador = None

    def _cambiar_widget(self, indice):
        self.stack.setCurrentIndex(indice)

    def _undock(self):
        indice = self.stack.currentIndex()
        widget = self.stack.widget(indice)
        titulo_widget = self.combo_selector.itemText(indice)
        self.combo_selector.removeItem(indice)
        widget.setParent(None)
        widget.setWindowTitle(titulo_widget)
        widget.resize(400, 400)
        widget.show()

    def _dock(self):
        pass

    def actualizar_simbolos(self, archivo):
        if archivo == 'Nuevo_archivo':
            return
        tag = self.ctags.run_ctags(archivo)
        simbolos = self.ctags.parser(tag)
        self._arbol_simbolos.actualizar_simbolos(simbolos)