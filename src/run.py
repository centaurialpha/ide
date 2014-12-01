# -*- coding: utf-8 -*-
# EDIS - Entorno de Desarrollo Integrado Simple para C/C++
#
# This file is part of EDIS
# Copyright 2014 - Gabriel Acosta
# License: GPLv3 (see http://www.gnu.org/licenses/gpl.html)

import sys
from time import time

from PyQt4.QtGui import (
    QIcon,
    QPixmap,
    QSplashScreen
    )

from PyQt4.QtCore import (
    QSettings,
    QCoreApplication,
    Qt,
    QLocale,
    QTranslator,
    QLibraryInfo
    )

from src import recursos
from src.helpers import (
    configuraciones,
    logger
    )
from .ui.ide.Ide import IDE

log = logger.edisLogger('edis.run')
DEBUG = log.debug


def correr_interfaz(app):
    DEBUG('Corriendo interfaz')
    t0 = time()
    config = QSettings(recursos.CONFIGURACION, QSettings.IniFormat)
    QCoreApplication.setOrganizationName('EDIS')
    QCoreApplication.setOrganizationDomain('EDIS')
    QCoreApplication.setApplicationName('EDIS')

    app.setWindowIcon(QIcon(recursos.ICONOS['icono']))
    imagenSplash = QPixmap(recursos.ICONOS['splash'])  # Splash
    splash = QSplashScreen(imagenSplash, Qt.WindowStaysOnTopHint)
    splash.setMask(imagenSplash.mask())
    splash.show()

    app.processEvents()

    # Idioma
    local = unicode(QLocale.system().name())
    qTraductor = QTranslator()
    qTraductor.load("qt_" + local,
        QLibraryInfo.location(QLibraryInfo.TranslationsPath))
    app.installTranslator(qTraductor)

    # Se cargan las configuraciones
    configuraciones.cargar_configuraciones()

    edis = IDE()
    splash.showMessage("Cargando GUI...",
                        Qt.AlignCenter | Qt.AlignTop, Qt.black)
    # Carga de archivos abiertos desde la última sesión
    DEBUG('Cargando archivos...')
    archivos_abiertos = config.value('archivosAbiertos/mainTab', []).toList()
    tmp = []
    for archivo in archivos_abiertos:
        d = archivo.toList()
        if d:
            tmp.append((unicode(d[0].toString()), d[1].toInt()[0]))
    archivos_abiertos = tmp

    # Archivos recientes
    recientes = config.value('archivosAbiertos/archivosRecientes', []).toList()
    tmp = []
    for archivo in recientes:
        d = archivo.toString()
        tmp.append(d)
    recientes = tmp
    if recientes is not None:
        archivos_recientes = list(recientes)
    else:
        archivos_recientes = list()
    archivos_recientes = [archivo for archivo in archivos_recientes]

    archivos_abiertos_hilo = []
    for i in range(len(archivos_abiertos)):
        archivos_abiertos_hilo.append(archivos_abiertos[i][0])

    edis.cargar_sesion(archivos_abiertos, archivos_recientes)

    splash.finish(edis)
    #edis.explorador.navegador.hilo.start()
    DEBUG('Tiempo: {0}'.format(time() - t0))
    sys.exit(app.exec_())