#-*- coding: utf-8 -*-

# Copyright (C) <2014>  <Gabriel Acosta>
# This file is part of EDIS.

# EDIS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# EDIS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with EDIS.  If not, see <http://www.gnu.org/licenses/>.

"""
Basado en Python Syntax highlighting de:
https://wiki.python.org/moin/PyQt/Python%20syntax%20highlighting
"""

# Módulos QtGui
from PyQt4.QtGui import QColor
from PyQt4.QtGui import QTextCharFormat
from PyQt4.QtGui import QFont
from PyQt4.QtGui import QSyntaxHighlighter
from PyQt4.QtGui import QBrush
from PyQt4.QtGui import QTextBlockUserData

# Módulos QtCore
from PyQt4.QtCore import QRegExp
from PyQt4.QtCore import Qt

# Módulos EDIS
from src import recursos
from src.ui.editor import sintaxis


def formato(color, estilo=''):
    """ Retorna un QTextCharformat con atributos dados. """

    color_ = QColor()
    color_.setNamedColor(color)

    formato_ = QTextCharFormat()
    formato_.setForeground(color_)

    if 'bold' in estilo:
        formato_.setFontWeight(QFont.Bold)
    if 'italic' in estilo:
        formato_.setFontItalic(True)

    return formato_

ESTILOS = {}


def re_estilo(tema):
    ESTILOS['palabra'] = formato(tema.get('palabra',
        recursos.TEMA_EDITOR['palabra']), 'bold')
    ESTILOS['types'] = formato(tema.get('types',
        recursos.TEMA_EDITOR['types']))
    ESTILOS['operador'] = formato(tema.get('operador',
        recursos.TEMA_EDITOR['operador']))
    ESTILOS['brace'] = formato(tema.get('brace',
        recursos.TEMA_EDITOR['brace']), 'bold')
    ESTILOS['struct'] = formato(tema.get('struct',
        recursos.TEMA_EDITOR['struct']), 'bold')
    ESTILOS['cadena'] = formato(tema.get('cadena',
        recursos.TEMA_EDITOR['cadena']))
    ESTILOS['caracter'] = formato(tema.get('caracter',
        recursos.TEMA_EDITOR['caracter']))
    ESTILOS['include'] = formato(tema.get('include',
        recursos.TEMA_EDITOR['include']))
    ESTILOS['comentario'] = formato(tema.get('comentario',
        recursos.TEMA_EDITOR['comentario']), 'italic')
    ESTILOS['numero'] = formato(tema.get('numero',
        recursos.TEMA_EDITOR['numero']))
    ESTILOS['pcoma'] = formato(tema.get('pcoma',
        recursos.TEMA_EDITOR['pcoma']), 'bold')


class Highlighter(QSyntaxHighlighter):
    """ Highlighter EDIS-C. """

    def __init__(self, documento, tema):
        QSyntaxHighlighter.__init__(self, documento)
        re_estilo(tema)
        self.braces = QRegExp('(\{|\}|\(|\)|\[|\])')
        # Reglas
        reglas = []
        # Palabras reservadas
        reglas += [(r'\b%s\b' % w, 0, ESTILOS['palabra'])
            for w in sintaxis.sintax['keywords']]
        # Types
        reglas += [(r'\b%s\b' % t, 0, ESTILOS['types'])
            for t in sintaxis.sintax['types']]
        # Operadores
        reglas += [(r'%s' % o, 0, ESTILOS['operador'])
            for o in sintaxis.sintax['operators']]
        reglas += [(r';', 0, ESTILOS['pcoma'])]
        # Braces
        reglas += [(r'%s' % b, 0, ESTILOS['brace'])
            for b in sintaxis.sintax['braces']]
        # Struct
        reglas += [(r'\bstruct\b\s*(\w+)', 1, ESTILOS['struct'])]
        # Caracter
        reglas += [(r"'[^'\\]*(\\.[^'\\]*)*'", 0, ESTILOS['caracter'])]
        # Numeros
        reglas += [(r'\b[+-]?[0-9]+[lL]?\b', 0, ESTILOS['numero']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, ESTILOS['numero']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b',
                0, ESTILOS['numero'])]
        # Cadena
        reglas += [(r'"[^"\\]*(\\.[^"\\]*)*"', 0, ESTILOS['cadena'])]
        # Include
        reglas += [(r'#[^\n]*', 0, ESTILOS['include'])]
        # Comentario simple
        reglas += [(r'//[^\n]*', 0, ESTILOS['comentario'])]
        # Comentario múltiple
        self.comentario_multiple_lineas = QTextCharFormat()
        color = QColor('gray')
        brush = QBrush(color, Qt.SolidPattern)
        self.comentario_multiple_lineas.setForeground(brush)
        self.comentario_inicio = QRegExp("/\\*")
        self.comentario_final = QRegExp("\\*/")

        self.reglas = [(QRegExp(pat), indice, fmt)
            for (pat, indice, fmt) in reglas]
        self.rehighlight()

    def highlightBlock(self, texto):

        block_data = TextBlockData()
        braces = self.braces
        ind = braces.indexIn(texto, 0)
        while ind >= 0:
            match_brace = str(braces.capturedTexts()[0])
            info = BracketsInfo(match_brace, ind)
            block_data.insert_brackets_info(info)
            ind = braces.indexIn(texto, ind + 1)
        self.setCurrentBlockUserData(block_data)

        for expresion, nth, formato in self.reglas:
            indice = expresion.indexIn(texto, 0)

            while indice >= 0:
                indice = expresion.pos(nth)
                length = expresion.cap(nth).length()
                self.setFormat(indice, length, formato)
                indice = expresion.indexIn(texto, indice + length)

        self.setCurrentBlockState(0)
        inicio_indice = 0
        if self.previousBlockState() != 1:
            inicio_indice = self.comentario_inicio.indexIn(texto)
        while inicio_indice >= 0:
            final_indice = self.comentario_final.indexIn(texto, inicio_indice)
            if final_indice == -1:
                self.setCurrentBlockState(1)
                commentLength = texto.length() - inicio_indice
            else:
                commentLength = final_indice - inicio_indice + \
                self.comentario_final.matchedLength()
            self.setFormat(inicio_indice, commentLength,
                self.comentario_multiple_lineas)
            inicio_indice = self.comentario_final.indexIn(texto,
                inicio_indice + commentLength)


class BracketsInfo:

    def __init__(self, character, position):
        self.character = character
        self.position = position


class TextBlockData(QTextBlockUserData):

    def __init__(self, parent=None):
        super(TextBlockData, self).__init__()
        self.braces = []
        self.valid = False

    def insert_brackets_info(self, info):
        self.valid = True
        self.braces.append(info)

    def isValid(self):
        return self.valid