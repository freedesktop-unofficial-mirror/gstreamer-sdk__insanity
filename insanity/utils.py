# GStreamer QA system
#
#       utils.py
#
# Copyright (c) 2007, Edward Hervey <bilboed@bilboed.com>
# Copyright (C) 2004 Johan Dahlin <johan at gnome dot org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

"""
Miscellaneous utility functions and classes
"""

from random import randint
import bz2

__uuids = []

def randuuid():
    """
    Generates a random uuid, not guaranteed to be unique.
    """
    return "%032x" % randint(0, 2**128)

def acquire_uuid():
    """
    Returns a guaranted unique identifier.
    When the user of that UUID is done with it, it should call
    release_uuid(uuid) with that identifier.
    """
    global __uuids
    uuid = randuuid()
    while uuid in __uuids:
        uuid = randuuid()
    __uuids.append(uuid)
    return uuid

def release_uuid(uuid):
    """
    Releases the use of a unique identifier.
    """
    global __uuids
    if not uuid in __uuids:
        return
    __uuids.remove(uuid)

def list_available_tests():
    """
    Returns the list of available tests containing for each:
    * the test name
    * the test description
    * the test class
    """
    from insanity.test import Test,DBusTest,PythonDBusTest,GStreamerTest,CmdLineTest
    from insanity.scenario import Scenario

    def get_valid_subclasses(cls):
        res = []
        if cls == Scenario:
            return res
        if not cls in [Test,DBusTest,PythonDBusTest,GStreamerTest,CmdLineTest]:
            res.append((cls.__test_name__.strip(), cls.__test_description__.strip(), cls))
        for i in cls.__subclasses__():
            res.extend(get_valid_subclasses(i))
        return res
    return get_valid_subclasses(Test)

def list_available_scenarios():
    """
    Returns the list of available scenarios containing for each:
    * the scenario name
    * the scenario description
    * the scenario class
    """
    from insanity.test import Test,DBusTest,PythonDBusTest,GStreamerTest,CmdLineTest
    from insanity.scenario import Scenario

    def get_valid_subclasses(cls):
        res = []
        if not cls == Scenario:
            res.append((cls.__test_name__.strip(), cls.__test_description__.strip(), cls))
        for i in cls.__subclasses__():
            res.extend(get_valid_subclasses(i))
        return res
    return get_valid_subclasses(Scenario)

def scan_for_tests():
    from tests import *
    from tests.scenarios import *

def get_test_class(testname):
    """
    Returns the Test class corresponding to the given testname
    """
    tests = list_available_tests()
    tests.extend(list_available_scenarios())
    testname = testname.strip()
    for name, desc, cls in tests:
        if testname == name:
            return cls
    raise ValueError("No Test class available for %s" % testname)

def reverse_dict(adict):
    """
    Returns a dictionnary where keys and values are inverted.

    Uniqueness of keys/values isn't checked !
    """
    d = {}
    if not adict:
        return d
    for k,v in adict.iteritems():
        d[v] = k
    return d

def map_dict(adict, mapdict):
    """
    Returns a dictionnary where the keys from adict are replaced
    by the value mapped in mapdict.

    If a key isn't present in mapdict, the (key,value) is copied
    in the resulting dictionnary
    """
    d = {}
    if not mapdict:
        return d
    for k,v in adict.iteritems():
        if k in mapdict:
            d[mapdict[k]] = v
    return d

def map_list(alist, mapdict):
    """
    Same as map_dict, except the first argument and return value are
    the flattened out tuple-list version : [(key1,val1), (key2, val2)..]
    """
    r = []
    if not mapdict:
        return r
    for k,v in alist:
        if k in mapdict:
            r.append((mapdict[k], v))
    return r

def compress_file(original, compfile):
    """
    Takes the contents of 'original' and compresses it into the new file
    'compfile' using BZ2.
    """
    f = open(original, "r")
    out = bz2.BZ2File(compfile, "w")
    # reading 8kbytes at a time, might want to increase it later
    buf = f.read(8192)
    while buf:
        out.write(buf)
        buf = f.read(8192)

    f.close()
    out.close()
