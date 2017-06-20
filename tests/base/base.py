##############################################################################
#
# Copyright 2016 KPMG Advisory N.V. (unless otherwise stated)
#
# Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
##############################################################################
"""
Common code for multiple tests and simplified wrappers for running tests

run(mods) and parallel(mods,modargs) are wrappers for running existing test modules as a suite
^ in sequence   ^in multiple subprocesses

findServices is a helper function to return a list of services present in a given stack of this checkout

LDTest is a derived test case class from unittest.TestCase, adding common methods for running tests on newly-created
aws machines
"""
import unittest
import sys
import os
import glob
import threading
import queue
import subprocess as sub
import __future__

def run(mods):
    """
    Wrapper for unittest running of test suite in sequence, collecting results and exiting on failure
    mods is either a single unittest.TestSuite object, or a list of python modules that each declared a suite() method

    for a wrapper which runs test in parallel instead, see the parallel method of this module
    """
    suite = None
    if type(mods) is unittest.TestSuite:
        suite = mods
    else:
        suite = unittest.TestSuite([mod.suite() for mod in mods])

    res = unittest.TextTestRunner(verbosity=2).run(suite)
    # print dir(res)
    # print res.errors, res.failures
    if len(res.errors) == 0 and len(res.failures) == 0:
        sys.exit(0)
    sys.exit(1)


#
# unittest does not come with a way to run test in parallel, so I must design that here, the parallel method is the
# equivalent of the run() method
#

class LockOnPrintThread(threading.Thread):
    """
    A threading class which locks before printing a result,
    method should be replaced with your own method returning a
    string for printing
    """

    def __init__(self, pool, lock):
        """
        pool should be a queue.Queue object
        lock, a thread.lock object
        """
        threading.Thread.__init__(self)
        self.lock = lock
        self.pool = pool
        self.done = False

    def run(self):
        """
        The main sequence, method, lock, print, unlock
        """
        while not self.done:
            try:
                item = self.pool.get_nowait()
                if item is not None:
                    result = self.method(self, item)
                    self.lock.acquire()
                    print(result.strip())
                    self.lock.release()
            except queue.Empty:
                self.done = True

    def method(self, item):
        """
        A const method on any class variables, must return a string
        or an exception
        """
        raise ImportError("do not call the baseclass method!")


class RedirectStdOut(object):

    def __init__(self, stdout=None):
        self._stdout = stdout or sys.stdout

    def __enter__(self):
        self.old_stdout = sys.stdout
        self.old_stdout.flush()
        sys.stdout = self._stdout

    def __exit__(self, exc_type, exc_value, traceback):
        self._stdout.flush()
        sys.stdout = self.old_stdout


class RunFileInSubProcess(LockOnPrintThread):
    """
    Class derived from lockOnPrintThread to re-implement run method. In this case the item list sent, the queue must
    be a series of commands to be run in subprocesses
    These commands are checked for status, and then locking is done before printing their stdout/err in case of failure.
    """

    def __init__(self, pool, lock, result):
        """
        pool should be a queue.Queue object
        lock, a thread.lock object
        """
        threading.Thread.__init__(self)
        self.lock = lock
        self.islockedbyme = False
        self.pool = pool
        self.done = False
        self.result = result
        self.errors = []
        self.margs = []

    def run(self, limit=100):
        """
        The main sequence, method, lock, adjust, unlock
        """
        looping = 0
        while not self.done and looping < limit:
            looping = looping + 1
            try:
                item = self.pool.get_nowait()
                if item is not None:
                    self.lock.acquire()
                    self.islockedbyme = True
                    myname = item.replace(os.path.realpath(os.path.dirname(__file__) + "/../") + "/", "")
                    myname = myname.replace("python ", "").replace(".py", "")
                    print("started:", myname)
                    sys.__stdout__.flush()
                    self.lock.release()
                    self.islockedbyme = False
                    proc = sub.Popen(item, shell=True, stdout=sub.PIPE, stderr=sub.PIPE)
                    stdout, stderr = proc.communicate()
                    status = proc.returncode
                    self.lock.acquire()
                    self.islockedbyme = True
                    self.result[item]["stdout"] = stdout
                    self.result[item]["stderr"] = stderr
                    self.result[item]["status"] = status
                    import datetime

                    if not status:
                        print(myname, "... OK")
                    else:
                        print(myname, "... ERROR")
                        print(myname, datetime.datetime.utcnow().strftime('%a %b %d %H:%M:%S UTC %Y'))
                        print(myname, " details: exited with ", status)
                        print(stdout)
                        print(stderr)
                    sys.__stdout__.flush()
                    self.lock.release()
                    self.islockedbyme = False
            except queue.Empty:
                self.done = True
                if self.islockedbyme:
                    try:
                        self.lock.release()
                        self.islockedbyme = False
                    except:
                        self.islockedbyme = False
            except Exception as e:
                print("Exiting a thread due to Error: " + str(e))
                err1, err2, err3 = sys.exc_info()
                self.errors.append(str(e) + " " + str(err1) + " " + str(err2) + "\n" + str(err3))
                if self.islockedbyme:
                    try:
                        self.lock.release()
                        self.islockedbyme = False
                    except:
                        self.islockedbyme = False


def parallel(mods, modargs=[]):
    """
    Run a set of tests in parallel, rather than in sequence, then collect and print their results.
    Mods is a set of python modules, and then each of their corresponding files is run with arguments from modargs,
    assuming the files are executable with python

    mods: python modules containing tests. Each module must be runnable with python mod.__file__, which usually means
    each file
         needs a runnable __main__ which runs some tests
    modargs: set of args which can be passed to each mod
        if it is a list, each entry of the list will be iterated over with the mod (sub-lists will be hjoined with "
        ".join() )
        if it is a dictionary of mod : [list] each entry in the list will be iterated over for the corresponding mod
        (sub-lists will be joined with " ".join() )
    e.g. mods=[foo,bar,fish], modargs={'foo':["spam","eggs"], 'bar':[["spam","and","eggs"]]} will run four tests in
    parallel:
        python foo.__file__ spam
        python foo.__file__ eggs
        python bar.__file__ spam and eggs
        python fish.__file__
    """
    # loop over threads, see the class for more details
    # create list of packages as a queue
    item_pool = queue.Queue()
    result = {}
    items = []
    if not len(modargs):
        items = ["python " + mod.__file__.replace('.pyc', ".py") for mod in mods]
    elif type(modargs) is list:
        for mod in mods:
            for arg in modargs:
                if type(arg) is list:
                    arg = " ".join(arg)
                items.append("python " + mod.__file__.replace('.pyc', ".py") + " " + arg)
    elif type(modargs) is dict:
        for mod in mods:
            if mod not in modargs:
                items.append("python " + mod.__file__.replace('.pyc', ".py"))
                continue
            args = modargs[mod]
            # just a single arguement
            if type(args) is not list:
                items.append("python " + mod.__file__.replace('.pyc', ".py") + " " + args)
                continue
            # empty list
            if not len(args):
                items.append("python " + mod.__file__.replace('.pyc', ".py"))
                continue
            for arg in args:
                if type(arg) is list:
                    arg = " ".join(arg)
                items.append("python " + mod.__file__.replace('.pyc', ".py") + " " + arg)
    else:
        raise ValueError("failed to interpret mod and modargs")
    # print items
    for item in items:
        result[item] = {}
        item_pool.put(item)
    lock = threading._allocate_lock()
    thethreads = []
    for _i in range(20):
        t = RunFileInSubProcess(item_pool, lock, result)
        thethreads.append(t)
        t.start()
    # setup a timeout to prevent really infinite loops!
    import datetime
    import time

    begin = datetime.datetime.utcnow()
    timeout = 60 * 60 * 3
    for t in thethreads:
        while not t.done:
            if (datetime.datetime.utcnow() - begin).seconds > timeout:
                break
            time.sleep(0.1)
    nd = [t for t in thethreads if not t.done]
    errs = []
    for t in thethreads:
        errs = errs + t.errors
    if len(errs):
        raise RuntimeError("Exceptions encountered while running tests as threads, as: \n" + '\n'.join(errs))
    # print result
    FAILED = len([f for f in result if result[f]["status"] != 0])
    TIMES = []
    TESTS = []
    for key, val in result.items():
        timing = [l for l in val["stderr"].split(b"\n") if l.startswith(b"Ran") and b" in " in l][0].strip()
        if len(timing):
            TIMES.append(float(timing.split(b" ")[-1].replace(b"s", b"")))
            TESTS.append(int(timing.split(b" ")[1]))
    print("======================================================================")
    print("Ran", sum(TESTS), "tests in", sum(TIMES).__str__() + "s", "from", len(result), "module/args")
    print('')
    if FAILED == 0 and len(nd) == 0:
        print("OK")
        sys.exit(0)
    if FAILED:
        print("FAILED (modules=" + str(FAILED) + ")")
    if len(nd):
        print("TIMEOUT (modules=" + str(len(nd)) + ")")
    sys.exit(1)


######################
# Any other helper functions?
######################


def d2j(adict):
    """Replacements to take a literal string and return a dictionary, using ajson intermediate
    """
    replaced = adict.strip().replace('{u\'', "{'").replace(' [u\'', "['").replace(
        ' (u\'', "('").replace(' u\'', " '").replace("'", '"').replace('(', "[").replace(")", "]")
    import json
    return json.loads(replaced)
