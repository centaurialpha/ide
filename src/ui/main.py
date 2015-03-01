# -*- coding: utf-8 -*-
# EDIS - a simple cross-platform IDE for C
#
# This file is part of Edis
# Copyright 2014-2015 - Edis Team
# License: GPLv3 (see http://www.gnu.org/licenses/gpl.html)

# Módulos Python
import os
import webbrowser

# Módulos QtGui
from PyQt4.QtGui import (
    QMainWindow,
    QIcon,
    QToolBar,
    QMessageBox
    )

# Módulos QtCore
from PyQt4.QtCore import (
    SIGNAL,
    Qt,
    QSize,
    )

# Módulos EDIS
from src import ui
from src.ui import system_tray
from src.helpers import (
    configuracion,
    #dependencias
    )
#from src.ui.widgets import tool_button
from src.helpers.configuracion import ESettings
from src.ui.dialogos import (
    dialogo_guardar_archivos,
    #dialogo_dependencias,
    acerca_de
    )


class EDIS(QMainWindow):
    """
    Esta clase es conocedora de todas las demás.

    """

    # Cada instancia de una clase  se guarda en éste diccionario
    __COMPONENTES = {}
    __LATERAL = {}  # Widgets laterales

    def __init__(self):
        QMainWindow.__init__(self)
        # Esto para tener widgets laterales en full height,
        window = QMainWindow(self)
        self.setWindowTitle('{' + ui.__nombre__ + '}')
        self.setMinimumSize(750, 500)
        # Se cargan las dimensiones de la ventana
        if ESettings.get('ventana/show-maximized'):
            self.setWindowState(Qt.WindowMaximized)
        else:
            size = ESettings.get('ventana/size')
            position = ESettings.get('ventana/position')
            self.resize(size)
            self.move(position)
        # Toolbar
        self.toolbar = QToolBar(self)
        toggle_action = self.toolbar.toggleViewAction()
        toggle_action.setText(self.tr("Toolbar"))
        self.toolbar.setMovable(False)
        self.toolbar.setObjectName("toolbar")
        self.toolbar.setIconSize(QSize(22, 22))
        self.addToolBar(Qt.RightToolBarArea, self.toolbar)
        self.dock_toolbar = QToolBar(self)
        toggle_action = self.dock_toolbar.toggleViewAction()
        toggle_action.setText(self.tr("Dock toolbar"))
        self.dock_toolbar.setObjectName("dock_toolbar")
        self.dock_toolbar.setMovable(False)
        self.addToolBar(Qt.LeftToolBarArea, self.dock_toolbar)
        toolbars = [self.toolbar, self.dock_toolbar]
        EDIS.cargar_componente("toolbars", toolbars)
        # Animated property
        self.setDockOptions(QMainWindow.AnimatedDocks)
        # Menú
        menu_bar = self.menuBar()
        self.setup_menu(menu_bar)
        # Barra de estado
        self.barra_de_estado = EDIS.componente("barra_de_estado")
        self.setStatusBar(self.barra_de_estado)
        # Widget central
        central = self._load_ui(window)
        window.setCentralWidget(central)
        window.setWindowFlags(Qt.Widget)
        self.setCentralWidget(window)

        EDIS.cargar_componente("edis", self)

        # Comprobar nueva versión
        if ESettings.get('general/check-updates'):
            self.noti = system_tray.NotificacionActualizacion()
            self.noti.show()

    @classmethod
    def cargar_componente(cls, nombre, instancia):
        """ Se guarda el nombre y la instancia de una clase """

        cls.__COMPONENTES[nombre] = instancia

    @classmethod
    def componente(cls, nombre):
        """ Devuelve la instancia de un componente """

        return cls.__COMPONENTES.get(nombre, None)

    @classmethod
    def cargar_lateral(cls, nombre, instancia):
        cls.__LATERAL[nombre] = instancia

    @classmethod
    def lateral(cls, nombre):
        return cls.__LATERAL.get(nombre, None)

    def setup_menu(self, menu_bar):
        from src.ui import actions
        from src import recursos

        menubar_items = [
            self.tr("&Archivo"),
            self.tr("&Editar"),
            self.tr("&Ver"),
            self.tr("&Buscar"),
            self.tr("E&jecución"),
            self.tr("A&cerca de")
            ]
        menu_items = {}
        toolbar_actions = {}
        editor_container = EDIS.componente("principal")
        shortcuts = recursos.SHORTCUTS
        toolbar_items = configuracion.TOOLBAR_ITEMS
        for i, m in enumerate(menubar_items):
            menu = menu_bar.addMenu(m)
            menu_items[i] = menu
        for i, _actions in enumerate(actions.ACTIONS):
            for action in _actions:
                obj = editor_container
                menu_name = menu_items[i]
                name = action.get('name', None)
                connection = action.get('connection', None)
                shortcut = action.get('shortcut', None)
                icon_action = action.get('icon', None)
                if icon_action is not None:
                    icon = QIcon(":image/%s" % icon_action)
                else:
                    icon = QIcon(":image/%s" % shortcut)
                separator = action.get('separator', False)
                subm = action.get('menu', False)
                if subm:
                    # Archivos recientes
                    submenu = menu_name.addMenu(name)
                    EDIS.cargar_componente("menu_recent_file", submenu)
                    continue
                qaction = menu_name.addAction(name)
                #FIXME: No depender de shortcut
                qaction.setIcon(icon)
                if shortcut is not None:
                    qaction.setShortcut(shortcuts[shortcut])
                if connection.startswith('edis'):
                    obj = self
                    connection = connection.split('.')[-1]
                slot = getattr(obj, connection, None)
                if hasattr(slot, "__call__"):
                    self.connect(qaction, SIGNAL("triggered()"), slot)
                if separator:
                    menu_name.addSeparator()
                if shortcut in toolbar_items:
                    toolbar_actions[shortcut] = qaction
        # Load toolbar
        for item in toolbar_items:
            action = toolbar_actions.get(item, None)
            if action is None:
                self.toolbar.addSeparator()
            else:
                self.toolbar.addAction(action)

    def _load_ui(self, window):
        """ Carga los componentes laterales y la salida del compilador """

        principal = EDIS.componente("principal")
        dock = EDIS.componente("dock")
        dock.load_dock_toolbar(self.dock_toolbar)
        names_instances = ["symbols", "navigator", "explorer"]
        for name in names_instances:
            method = getattr(dock, "load_%s_widget" % name, None)
            widget = EDIS.lateral(name)
            method(widget)
            self.addDockWidget(Qt.LeftDockWidgetArea, widget)
        output_widget = EDIS.componente("output")
        dock.load_output_widget(output_widget)
        window.addDockWidget(Qt.BottomDockWidgetArea, output_widget)
        if ESettings.get('general/show-start-page'):
            principal.add_start_page()

        # Conexiones
        self.connect(principal, SIGNAL("fileChanged(QString)"),
                     self._update_status)
        self.connect(principal, SIGNAL("cursorPosition(int, int, int)"),
                     self._update_cursor)
        self.connect(principal, SIGNAL("fileChanged(QString)"),
                     self._change_title)
        self.connect(principal.editor_widget, SIGNAL("allFilesClosed()"),
                     self._all_closed)

        return principal

    def _update_cursor(self, line, row, lines):
        self.barra_de_estado.cursor_widget.show()
        self.barra_de_estado.cursor_widget.actualizar_cursor(line, row, lines)

    def _update_status(self, archivo):
        self.barra_de_estado.update_status(archivo)

    def _all_closed(self):
        self.setWindowTitle('{' + ui.__nombre__ + '}')
        self.barra_de_estado.cursor_widget.hide()
        self._update_status("")

    def _change_title(self, title):
        """ Cambia el título de la ventana (filename - {EDIS}) """

        title = os.path.basename(title)
        self.setWindowTitle(title + ' - ' + '{' + ui.__nombre__ + '}')

    def report_bug(self):
        webbrowser.open_new(ui.__reportar_bug__)

    def show_hide_toolbars(self):
        for toolbar in [self.toolbar, self.dock_toolbar]:
            if toolbar.isVisible():
                toolbar.hide()
            else:
                toolbar.show()

    def show_hide_all(self):
        dock = EDIS.componente("dock")
        dock.show_hide_all()

    def show_full_screen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def show_hide_output(self):
        dock = EDIS.componente("dock")
        dock.output_visibility()

    def cargar_archivos(self, files, recents_files):
        """ Carga archivos al editor desde la última sesión y actualiza el menú
        de archivos recientes.
        """

        principal = EDIS.componente("principal")
        for _file in files:
            filename, cursor_position = _file
            principal.open_file(filename, cursor_position)
        principal.update_recents_files(recents_files)

    def about_qt(self):
        QMessageBox.aboutQt(self)

    def about_edis(self):
        dialogo = acerca_de.AcercaDe(self)
        dialogo.exec_()

    def closeEvent(self, event):
        """
        Éste médoto es llamado automáticamente por Qt cuando se
        cierra la aplicación

        """

        editor_container = EDIS.componente("principal")
        if editor_container.check_files_not_saved() and \
                ESettings.get('general/confirm-exit'):

            files_not_saved = editor_container.files_not_saved()
            dialog = dialogo_guardar_archivos.DialogSaveFiles(
                files_not_saved, editor_container)
            dialog.exec_()
            if dialog.ignorado():
                event.ignore()
        if ESettings.get('ventana/store-size'):
            if self.isMaximized():
                ESettings.set('ventana/show-maximized', True)
            else:
                ESettings.set('ventana/show-maximized', False)
                ESettings.set('ventana/size', self.size())
                ESettings.set('ventana/position', self.pos())
        opened_files = editor_container.opened_files()
        ESettings.set('general/files', opened_files)
        ESettings.set('general/recents-files',
            editor_container.get_recents_files())

    def show_settings(self):
        from src.ui.dialogos.preferencias import preferencias
        dialogo = preferencias.Preferencias(self)
        dialogo.show()
