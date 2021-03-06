# -*- coding: utf-8 -*-
# EDIS - a simple cross-platform IDE for C
#
# This file is part of Edis
# Copyright 2014-2015 - Gabriel Acosta <acostadariogabriel at gmail>
# License: GPLv3 (see http://www.gnu.org/licenses/gpl.html)

import sys
import os

from PyQt4.QtGui import (
    QIcon,
    QSplashScreen,
    QPixmap,
    QToolTip,
    QFont
    )

from PyQt4.QtCore import (
    QLocale,
    QTranslator,
    QLibraryInfo,
    QSettings,
    Qt
    )
from src.core import (
    paths,
    settings,
    cmd_parser,
    logger
    )
# Logger
log = logger.get_logger(__name__)
DEBUG = log.debug

# Se cargan las configuraciones
DEBUG("Loading settings...")
settings.load_settings()
# Se crean los objetos
#lint:disable
from src.ui.containers.lateral import (
    tab_container,
    explorer,
    tree_symbols,
    tree_projects
    )
from src.ui.containers.output import output_container
from src.ui.containers import editor_container
from src.ui.widgets import status_bar
from src.ui.dialogs.preferences import preferences
#lint:enable
from src.ui.main import Edis


def run_edis(app):
    """ Se carga la interfáz """

    DEBUG("Running Edis...")
    qsettings = QSettings(paths.CONFIGURACION, QSettings.IniFormat)
    # Ícono
    app.setWindowIcon(QIcon(":image/edis"))
    # Lenguaje
    local = QLocale.system().name()
    DEBUG("Loading language...")
    language = settings.get_setting('general/language')
    if language:
        edis_translator = QTranslator()
        edis_translator.load(os.path.join(paths.PATH,
                             "extras", "i18n", language))
        app.installTranslator(edis_translator)
        # Qt translator
        qtranslator = QTranslator()
        qtranslator.load("qt_" + local, QLibraryInfo.location(
                         QLibraryInfo.TranslationsPath))
        app.installTranslator(qtranslator)
    pixmap = QPixmap(":image/splash")
    # Splash screen
    show_splash = False
    if settings.get_setting('general/show-splash'):
        DEBUG("Showing splash...")
        splash = QSplashScreen(pixmap, Qt.WindowStaysOnTopHint)
        splash.setMask(pixmap.mask())
        splash.show()
        app.processEvents()
        show_splash = True

    # Style Sheet
    style = settings.get_setting('window/style-sheet')
    path_style = None
    style_sheet = None
    if style == 'Edark':
        path_style = os.path.join(paths.PATH, 'extras', 'theme', 'edark.qss')
    elif style != 'Default':
        path_style = os.path.join(paths.EDIS, style + '.qss')
    if path_style is not None:
        with open(path_style, mode='r') as f:
            style_sheet = f.read()
    app.setStyleSheet(style_sheet)

    # Fuente en Tooltips
    QToolTip.setFont(QFont(settings.DEFAULT_FONT, 9))

    # GUI
    if show_splash:
        alignment = Qt.AlignBottom | Qt.AlignLeft
        splash.showMessage("Loading UI...", alignment, Qt.white)
    DEBUG("Loading GUI...")
    edis = Edis()
    edis.show()
    # Archivos de última sesión
    files, recents_files, projects = [], [], []
    projects = qsettings.value('general/projects')
    #FIXME:
    if projects is None:
        projects = []
    if settings.get_setting('general/load-files'):
        DEBUG("Loading files and projects...")
        if show_splash:
            splash.showMessage("Loading files...", alignment, Qt.white)
        files = qsettings.value('general/files')
        if files is None:
            files = []
        # Archivos recientes
        recents_files = qsettings.value('general/recents-files')
        if recents_files is None:
            recents_files = []
    # Archivos desde línea de comandos
    files += cmd_parser.parse()
    edis.load_files_and_projects(files, recents_files, projects)
    if show_splash:
        splash.finish(edis)
    DEBUG("Edis is Ready!")
    sys.exit(app.exec_())