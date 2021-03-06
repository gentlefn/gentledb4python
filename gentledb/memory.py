#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012  Felix Rabe (www.felixrabe.net)
#
# GentleDB is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# GentleDB is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with GentleDB.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, print_function

from hashlib import sha256

from . import interfaces, utilities


class GentleDB(interfaces.GentleDB):

    def __init__(self):
        super(GentleDB, self).__init__()
        self.content_db = {}
        self.pointer_db = {}

    def __add__(self, content):
        content_id = sha256(content).hexdigest()
        self.content_db[content_id] = content
        return content_id

    def __sub__(self, content_id):
        utilities.validate_identifier(content_id)
        return self.content_db[content_id]

    def __invert__(self):
        return utilities.random()

    def __setitem__(self, pointer_id, content_id):
        utilities.validate_identifier(pointer_id)
        if content_id:
            utilities.validate_identifier(content_id)
            self.pointer_db[pointer_id] = content_id
        else:
            del self.pointer_db[pointer_id]

    def __getitem__(self, pointer_id):
        utilities.validate_identifier(pointer_id)
        return self.pointer_db[pointer_id]

    def __call__(self, content_id=None):
        if content_id is not None:  # f=db(content_id) ; content=f.read()
            utilities.validate_identifier(content_id)
            return _InFile(self, content_id)
        else:                       # f=db() ; f.write(content) ; content_id=f()
            return _OutFile(self)


class GentleDBFull(interfaces.GentleDBFull, GentleDB):

    def findc(self, partial_content_id=""):
        utilities.validate_identifier(partial_content_id, partial=True)
        content_ids = [i for i in self.content_db if i.startswith(partial_content_id)]
        return content_ids

    def findp(self, partial_pointer_id=""):
        utilities.validate_identifier(partial_pointer_id, partial=True)
        pointer_ids = [i for i in self.pointer_db if i.startswith(partial_pointer_id)]
        return pointer_ids


class _OutFile(object):

    def __init__(self, db):
        super(_OutFile, self).__init__()
        self.db = db
        self.hash_obj = sha256()
        self.data = []

    def write(self, data):
        self.hash_obj.update(data)
        self.data.append(data)

    def close(self):
        pass

    def __call__(self):
        content_id = self.hash_obj.hexdigest()
        self.db.content_db[content_id] = "".join(self.data)
        return content_id


class _InFile(object):

    def __init__(self, db, content_id):
        super(_InFile, self).__init__()
        self.db = db
        self.content_id = content_id
        self.pos = 0

    def read(self, size=-1):
        content = self.db.content_db[self.content_id]
        length = len(content)
        if size < 0:    newpos = length             # read the rest
        else:           newpos = self.pos + size    # read only a part
        part = content[self.pos:newpos]
        self.pos = min(length, newpos)
        return part
