# -*- coding: utf-8 -*-

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


from subprocess import Popen, PIPE

"""
COMANDO = ctags -n --fields=fiKmnsSzt -f  - filename

"""


def get_ctags():
    """ Return True if ctags is installed or False is not installed. """

    command = ["ctags", "--version"]
    try:
        process = Popen(command, 0, stdout=PIPE, stderr=PIPE, shell=False)
        if process.communicate()[0]:
            return True
    except:
        return False


class CTags:

    def __init__(self):
        self.tags = None

    def start_ctags(self, filename):
        """ Run the command ctags """

        cmd = ["ctags", "-n", "--fields=fimKnsSzt", "-f", "-", filename]
        process = Popen(cmd, 0, stdout=PIPE, stderr=PIPE, shell=False)
        tag = process.communicate()[0]

        return tag


class Parser(object):

    def __init__(self):
        self._tags = []

    def parser_tag(self, tag):
        """
        Parse the tag for obtain the symbols of source code.

        functions = {name: [line, definition]}
        variables = {name: line}
        structs = {name: {line: [members]}}
"
        """
        tagc = None

        for line in tag.splitlines():
            name = None
            type_ = None
            nline = None
            definition = None
            for e, v in enumerate(line.split('\t')):
                if e == 0:
                    name = v.split(':')[-1]
                if e == 3:
                    type_ = v.split(':')[-1]
                if e == 4:
                    nline = v.split(':')[-1]
                if e == 5:
                    definition = (v.split(':')[-1], v.split(':')[0])

            tagc = Tag(name, type_, nline)
            if type_ == 'class':
                tagc.isClass = True
                self._tags.append(tagc)
            if type_ == 'function':
                if definition[1] == 'class':
                    tagc.isMethod = True
                    tagc.memberOf = definition[0]
                else:
                    tagc.memberOf = definition[0]
                    tagc.isFunction = True
                self._tags.append(tagc)
            if type_ == 'struct':
                tagc.isStruct = True
                self._tags.append(tagc)
            if type_ == 'variable':
                tagc.isGlobal = True
                self._tags.append(tagc)
            if type_ == 'member':
                if definition[1] == 'class':
                    tagc.isAttribute = True
                else:
                    tagc.isMember = True
                tagc.memberOf = definition[0]
                self._tags.append(tagc)
            if type_ == 'enum':
                tagc.isEnum = True
                self._tags.append(tagc)
            if type_ == 'enumerator':
                tagc.memberOf = definition[0]
                tagc.isEnumerator = True
                self._tags.append(tagc)

    def get_symbols(self):
        symbols = {}

        classes = dict()
        structs = dict()
        globalss = dict()
        functions = dict()
        enums = dict()
        atr = []
        met = []
        stc = []
        enu = []

        for i in self._tags:
            if i.isClass:
                classes[i.name] = (i.line, {'attributes': {}}, {'methods': {}})
            if i.isStruct:
                structs[i.name] = (i.line, {'members': {}})
            if i.isFunction:
                functions[i.name] = i.line
            if i.isGlobal:
                globalss[i.name] = i.line
            if i.isAttribute:
                atr.append(i)
            if i.isMethod:
                met.append(i)
            if i.isMember:
                stc.append(i)
            if i.isEnum:
                enums[i.name] = (i.line, {'enumerators': {}})
            if i.isEnumerator:
                enu.append(i)

        for i in atr:
            if i.memberOf in classes:
                classes[i.memberOf][1]['attributes'].update({i.name: i.line})
        for i in met:
            if i.memberOf in classes:
                classes[i.memberOf][2]['methods'].update({i.name: i.line})
        for i in stc:
            if i.memberOf in structs:
                structs[i.memberOf][1]['members'].update({i.name: i.line})
        for i in enu:
            if i.memberOf in enums:
                enums[i.memberOf][1]['enumerators'].update({i.name: i.line})

        if functions:
            symbols['functions'] = functions
        if globalss:
            symbols['globals'] = globalss
        if classes:
            symbols['classes'] = classes
        if structs:
            symbols['structs'] = structs
        if enums:
            symbols['enums'] = enums

        self._tags = []

        return symbols


class Tag(object):

    def __init__(self, name, type_='', line=None):
        self.name = name
        self.line = line
        self.type = type_
        self.isClass = False
        self.isFunction = False
        self.isMethod = False
        self.isAttribute = False
        self.isGlobal = False
        self.isMember = False
        self.isStruct = False
        self.isEnum = False
        self.isEnumerator = False
        self.memberOf = ''