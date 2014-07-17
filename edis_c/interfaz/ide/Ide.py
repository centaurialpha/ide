#-*- coding: utf-8 -*-

# <Encargado de correr la Interfáz.>
# Copyright (C) <2014>  <Gabriel Acosta>
# This file is part of EDIS-C.

# EDIS-C is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# EDIS-C is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with EDIS-C.  If not, see <http://www.gnu.org/licenses/>.

import os

from PyQt4.QtGui import QMainWindow
from PyQt4.QtGui import QDesktopWidget
from PyQt4.QtGui import QToolBar
from PyQt4.QtGui import QApplication
from PyQt4.QtGui import QMessageBox

from PyQt4.QtCore import Qt
from PyQt4.QtCore import QSize
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QSettings

from edis_c.interfaz.menu import menu_archivo
from edis_c.interfaz.menu import menu_editar
from edis_c.interfaz.menu import menu_ver
from edis_c.interfaz.menu import menu_buscar
from edis_c.interfaz.menu import menu_herramientas
from edis_c.interfaz.menu import menu_ejecucion
from edis_c.interfaz.menu import menu_acerca_de

from edis_c.interfaz import widget_central
#from side_c.interfaz.contenedor_secundario import simbolos_widget
from edis_c.interfaz.contenedor_principal import contenedor_principal
from edis_c.interfaz.contenedor_secundario import contenedor_secundario
from edis_c.interfaz import barra_de_estado

import edis_c
from edis_c import recursos
from edis_c.nucleo import configuraciones


ITEMS_TOOLBAR1 = [
    "nuevo-archivo",
    "abrir-archivo",
    "guardar-archivo",
    "separador",
    "deshacer",
    "rehacer",
    "separador",
    "cortar",
    "copiar",
    "pegar",
    "separador",
    "indentar",
    "desindentar",
    "include",
    "titulo",
    "linea",
    "separador"
    ]

ITEMS_TOOLBAR2 = [
    "compilar-archivo",
    "ejecutar-archivo",
    "compilar_ejecutar-archivo",
    "frenar"
    ]

__instanciaIde = None


# Singleton
def IDE(*args, **kw):
    global __instanciaIde
    if __instanciaIde is None:
        __instanciaIde = __IDE(*args, **kw)
    return __instanciaIde


class __IDE(QMainWindow):
    """ Aplicación principal """

    def __init__(self):
        QMainWindow.__init__(self)
        self.setMinimumSize(850, 700)
        self.setWindowTitle(edis_c.__nombre__)
        self._cargar_tema()
        get_pantalla = QDesktopWidget().screenGeometry()
        self.posicionar_ventana(get_pantalla)
        self.showMaximized()

        # Widget Central
        self.widget_Central = widget_central.WidgetCentral(self)
        self.cargar_ui(self.widget_Central)
        self.setCentralWidget(self.widget_Central)

        # ToolBar
        self.toolbar = QToolBar(self)
        self.toolbar_ = QToolBar(self)
        self.toolbar.setToolTip(self.trUtf8("Mantén presionado y mueve"))
        if not configuraciones.LINUX:
            self.toolbar_.setIconSize(QSize(25, 25))
            self.toolbar.setIconSize(QSize(25, 25))
        else:
            self.toolbar_.setIconSize(QSize(22, 22))
            self.toolbar.setIconSize(QSize(22, 22))
        self.toolbar.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.addToolBar(Qt.RightToolBarArea, self.toolbar)
        self.addToolBar(Qt.RightToolBarArea, self.toolbar_)

        # Barra de estado
        self.barra_de_estado = barra_de_estado.BarraDeEstado(self)
        #self.barra_de_estado.hide()
        self.setStatusBar(self.barra_de_estado)

        # Menu
        menu = self.menuBar()
        archivo = menu.addMenu(self.tr("&Archivo"))
        editar = menu.addMenu(self.tr("&Editar"))
        ver = menu.addMenu(self.trUtf8("&Ver"))
        buscar = menu.addMenu(self.trUtf8("&Buscar"))
        herramientas = menu.addMenu(self.trUtf8("&Herramientas"))
        ejecucion = menu.addMenu(self.trUtf8("E&jecucion"))
        acerca = menu.addMenu(self.tr("Ace&rca de"))

        self._menu_archivo = menu_archivo.MenuArchivo(
            archivo, self.toolbar, self)
        self._menu_editar = menu_editar.MenuEditar(
            editar, self.toolbar_, self)
        self._menu_ver = menu_ver.MenuVer(ver, self)
        self._menu_herramientas = menu_herramientas.MenuHerramientas(
            herramientas, self.toolbar_, self)
        self._menu_buscar = menu_buscar.MenuBuscar(buscar, self)
        self._menu_ejecucion = menu_ejecucion.MenuEjecucion(
            ejecucion, self.toolbar, self)
        self._menu_acerca_de = menu_acerca_de.MenuAcercade(acerca, self)

        self.connect(self.contenedor_principal, SIGNAL("fileSaved(QString)"),
            self.mostrar_barra_de_estado)

        # Métodos para cargar items en las toolbar
        self.cargar_toolbar([self._menu_archivo, self._menu_editar,
            self._menu_herramientas], self.toolbar, ITEMS_TOOLBAR1)

        self.cargar_toolbar([self._menu_ejecucion], self.toolbar_, ITEMS_TOOLBAR2)

        if configuraciones.MOSTRAR_PAGINA_INICIO:
            self.contenedor_principal.mostrar_pagina_de_inicio()

    def posicionar_ventana(self, pantalla):
        """ Posiciona la ventana en el centro de la pantalla. """

        tam_ventana = self.geometry()

        self.move((pantalla.width() - tam_ventana.width()) / 2,
                  (pantalla.height() - tam_ventana.height()) / 2)

    def cargar_ui(self, widget_central):
        self.contenedor_principal = contenedor_principal.ContenedorMain(self)
        self.contenedor_secundario = \
            contenedor_secundario.ContenedorBottom(self)

        self.connect(self.contenedor_principal,
            SIGNAL("desactivarPagInicio()"), self.desactivar_pagina_de_inicio)
        self.connect(self.contenedor_principal, SIGNAL(
            "currentTabChanged(QString)"), self.cambiar_titulo_de_ventana)
        self.connect(self.contenedor_principal, SIGNAL("nuevoArchivo()"),
            self.contenedor_principal.agregar_editor)
        self.connect(self.contenedor_principal, SIGNAL("abrirArchivo()"),
            self.contenedor_principal.abrir_archivo)
        #self.widget_simbolos = simbolos_widget.SimbolosWidget()
        widget_central.agregar_contenedor_central(self.contenedor_principal)
        #widget_central.agregar_contenedor_lateral(self.widget_simbolos)
        widget_central.agregar_contenedor_bottom(self.contenedor_secundario)

        self.connect(self.contenedor_principal, SIGNAL(
            "cursorPositionChange(int, int)"), self._linea_columna)

    def desactivar_pagina_de_inicio(self):
        configuraciones.MOSTRAR_PAGINA_INICIO = False
        qsettings = QSettings()
        qsettings.beginGroup('configuraciones')
        qsettings.beginGroup('general')
        qsettings.setValue('paginaInicio',
            configuraciones.MOSTRAR_PAGINA_INICIO)
        qsettings.endGroup()
        qsettings.endGroup()
        self.contenedor_principal.tab_actual.cerrar_tab()

    def cargar_toolbar(self, menus, toolbar, items):
        """ Carga los items en el toolbar
            menus: lista de menus o menu.
            toolbar: QToolBar
            items: lista de items
        """
        toolbar.clear()
        items_toolbar = {}

        if isinstance(menus, list):
            for menu in menus:
                items_toolbar.update(menu.items_toolbar)
        else:
            items_toolbar.update(menus.items_toolbar)

        for item in items:
            if item == 'separador':
                toolbar.addSeparator()
            else:
                item_tool = items_toolbar.get(item, None)

                if item_tool is not None:
                    toolbar.addAction(item_tool)

    def cargar_status_tips(self, accion, texto):
        accion.setStatusTip(texto)

    def cambiar_titulo_de_ventana(self, titulo):
        """ Cambia el título de la ventana cuando la pestaña cambia de nombre,
        esta emite la señal de cambio. """

        if titulo == edis_c.__nombre__:
            titulo = ""
            return

        nombre_con_extension = os.path.basename(str(titulo)).split('/')[0]
        self.setWindowTitle(
            #nombre_con_extension + ' (' + titulo + ')' + ' - EDIS-C')
            nombre_con_extension + ' (' + titulo + ') - ' + edis_c.__nombre__)

    def _linea_columna(self):
        editor = self.contenedor_principal.devolver_editor_actual()
        if editor is not None:
            i = editor.textCursor().blockNumber() + 1
            j = editor.textCursor().columnNumber()
            self.barra_de_estado.linea_columna.actualizar_linea_columna(i, j)

    def closeEvent(self, evento):
        SI = QMessageBox.Yes
        CANCELAR = QMessageBox.Cancel

        if self.contenedor_principal.check_tabs_sin_guardar():
            v = QMessageBox.question(self,
                self.trUtf8("Algunos cambios no se han guardado"),
                (self.trUtf8("\n\n¿ Guardar los archivos ?")),
                SI, QMessageBox.No, CANCELAR)

            if v == SI:
                self.contenedor_principal.guardar_todo()

            if v == CANCELAR:
                evento.ignore()

    def mostrar_barra_de_estado(self, mensaje):
        self.barra_de_estado.show()
        self.barra_de_estado.showMessage(mensaje, 3000)

    def _cargar_tema(self):
        """ Carga el tema por defecto """

        qss = recursos.TEMA_POR_DEFECTO
        #qss = recursos.TEMA_BLACK_SIDE
        with open(qss) as q:
            tema = q.read()
        QApplication.instance().setStyleSheet(tema)