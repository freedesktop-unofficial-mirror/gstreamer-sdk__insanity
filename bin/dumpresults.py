#!/usr/bin/env python

# GStreamer QA system
#
#       dumpresults.py
#
# Copyright (c) 2008, Edward Hervey <bilboed@bilboed.com>
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
Dumps the results of a test results DB
"""

import sys
import time
from optparse import OptionParser
from gstqa.storage.sqlite import SQLiteStorage

def printTestRunInfo(db, testrunid, verbose=False):
    # id , date, nbtests, client
    cid, starttime, stoptime = db.getTestRun(testrunid)
    softname, clientname, clientuser = db.getClientInfoForTestRun(testrunid)
    tests = db.getTestsForTestRun(testrunid)
    failed = db.getFailedTestsForTestRun(testrunid)
    print "[% 3d]\tDate:%s\tnbtests:% 5dFailed:% 5d\tClient : %s/%s/%s" % (testrunid,
                                                                           time.ctime(starttime),
                                                                           len(tests),
                                                                           len(failed),
                                                                           softname,
                                                                           clientname,
                                                                           clientuser)

def printTestInfo(db, testid, failedonly=False):
    trid, ttype, args, checks, resperc, extras, outputfiles = db.getFullTestInfo(testid)
    if failedonly and resperc == 100.0:
        return
    # test number + name
    print "Test #% 3d (%s) Success : %0.1f%%" % (testid, ttype, resperc)
    # arguments
    print "Arguments :"
    for key,val in args.iteritems():
        print "\t% -30s:\t%s" % (key, val)
    # results
    print "Results :"
    for key,val in checks:
        print "\t% -30s:\t%d" % (key, val)
    if extras:
        print "Extra Information:"
        for key,val in extras.iteritems():
            print "\t% -30s:\t%s" % (key, val)
    if outputfiles:
        print "Output files:"
        for key,val in outputfiles.iteritems():
            print "\t% -30s:\t%s" % (key,val)
    # monitors
    monitors = db.getMonitorsIDForTest(testid)
    if monitors:
        print "Applied Monitors:"
        for mid in monitors:
            tid,mtyp,args,results,resperc,extras,outputfiles = db.getFullMonitorInfo(mid)
            print "\tMonitor #% 3d (%s) Success : %0.1f%%" % (mid, mtyp, resperc)
            if args:
                print "\t\tArguments :"
                for k,v in args.iteritems():
                    print "\t\t\t% -30s:\t%s" % (k,v)
            if results:
                print "\t\tResults :"
                for k,v in results.iteritems():
                    print "\t\t\t% -30s:\t%s" % (k,v)
            if extras:
                print "\t\tExtra Information :"
                for k,v in extras.iteritems():
                    print "\t\t\t% -30s:\t%s" % (k,v)
            if outputfiles:
                print "\t\tOutput Files :"
                for k,v in outputfiles.iteritems():
                    print "\t\t\t% -30s:\t%s" % (k,v)
    print ""

def printEnvironment(d):
    print "Environment"
    for key,val in d.iteritems():
        if isinstance(val, dict):
            print "\t% -30s:" % (key)
            for dk,dv in val.iteritems():
                print "\t\t% -30s:\t%s" % (dk,dv)
        else:
            print "\t% -30s:\t%s" % (key,val)
    print ""

def printTestRun(db, testrunid, failedonly=False, hidescenarios=False):
    # let's output everything !
    cid, starttime, stoptime = db.getTestRun(testrunid)
    softname, clientname, clientuser = db.getClientInfoForTestRun(testrunid)
    environ = db.getEnvironmentForTestRun(testrunid)
    tests = db.getTestsForTestRun(testrunid, not hidescenarios)
    print "TestRun #% 3d:" % testrunid
    print "Started:%s\nStopped:%s" % (time.ctime(starttime), time.ctime(stoptime))
    if environ:
        printEnvironment(environ)
    print "Number of tests:", len(tests)
    for testid in tests:
        printTestInfo(db, testid, failedonly)

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-l", "--list", dest="list",
                      help="List the available test runs",
                      action="store_true",
                      default=False)
    parser.add_option("-t", "--testrun", dest="testrun",
                      help="Specify a testrun id",
                      type=int,
                      default=-1)
    parser.add_option("-f", "--failed", dest="failed",
                      help="Only show failed tests",
                      action="store_true", default=False)
    parser.add_option("-x", "--hidescenarios", dest="hidescenarios",
                      help="Do not show scenarios",
                      action="store_true", default=False)
    (options, args) = parser.parse_args(sys.argv[1:])
    if len(args) != 1:
        print "You need to specify a database file !"
        parser.print_help()
        sys.exit()
    db = SQLiteStorage(path=args[0])
    if options.list:
        # list all available test rus
        testruns = db.listTestRuns()
        for runid in testruns:
            printTestRunInfo(db, runid)
    else:
        testruns = db.listTestRuns()
        if options.testrun:
            if not options.testrun in testruns:
                print "Specified testrunid not available !"
                parser.print_help()
                sys.exit()
            printTestRun(db, options.testrun, options.failed, options.hidescenarios)
        else:
            for runid in testruns:
                printTestRun(db,runid,options.failed, options.hidescenarios)

