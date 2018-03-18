#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) 2018 Florian Lagg <github@florian.lagg.at>
# Under Terms of GPL v3

from threading import Lock, Thread, currentThread, Event
from datetime import datetime, timedelta
from time import sleep
import sys
import traceback
#from console.keystroke import getChar
import os
from InputHandler import InputHandler

class DoEvery(object):
    def __init__(self, profilerPath = None):
        super(DoEvery, self).__init__()
        self._lock = Lock()
        self._timeDict = {}
        self._keepRunning = True
        self._threadLst = []
        self._stopEvent = Event()
        self._profilerPath = profilerPath
        if profilerPath is not None:
            try:
                os.makedirs(profilerPath)
            except:
                pass

    @property
    def StopEvent(self):
        return self._stopEvent

    def _dt2sec(self, dt):
        return int((dt - datetime(1970, 1, 1)).total_seconds())

    def _enqueue(self, next, func, every, *args, **kwargs):
        if self._keepRunning:
            lateInfo = "for next run at"
            now = self._dt2sec(datetime.utcnow())
            if next < now:
                print '*** Enqueue  ***', currentThread().getName(), "was late", now - next, "Seconds. Starting in 1s."
                next = self._dt2sec(datetime.utcnow() + timedelta(seconds=1))
            else:
                print '*** Enqueue  ***', currentThread().getName(), "scheduling for", datetime.utcfromtimestamp(next)
            with self._lock:
                if next not in self._timeDict:
                    self._timeDict[next] = []
                self._timeDict[next] += [
                    {'func': func, 'every': every, 'args': args, 'kwargs': kwargs}
                ]

    def _profilerWrapper(self, func, *args, **kwargs):
        try:
            import cProfile
            pr = cProfile.Profile()
            pr.enable()
            func(*args, **kwargs)
        finally:
            pr.disable()
            pr.dump_stats("%s/%s_%s.cProfile" % (
                self._profilerPath, func.func_code.co_name, datetime.utcnow().strftime("%Y%m%d-%H%M%S")))

    def _runAndRequeue(self, func, every, *args, **kwargs):
        if self._keepRunning:
            next = self._dt2sec(datetime.utcnow() + timedelta(seconds=every))
            print '*** Starting ***', currentThread().getName(), "with next runtime target", datetime.utcfromtimestamp(next)
            try:
                if self._profilerPath is None:
                    func(*args, **kwargs)
                else:
                    self._profilerWrapper(func, *args, **kwargs)
                #print '*** Finished ***', currentThread().getName()
            except Exception as ex:
                print("%s" % (repr(ex)))
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_tb(exc_traceback, file=sys.stdout)
                print '*** Errored  ***', currentThread().getName()
            finally:
                self._enqueue(next, func, every, *args, **kwargs)
        else:
            print '*** Last Run ***', currentThread().getName(), "NO FURTHER RUN!"

    def RunAndRequeue(self, func, every, *args, **kwargs):
        p = Thread(name="%s started %s (args=%s, kwargs=%s)" % (func.func_code.co_name.ljust(30,' '), datetime.utcnow(), repr(args), repr(kwargs)),
                   target=self._runAndRequeue, args=(func, every) + args, kwargs=kwargs)
        p.daemon = True
        p.start()
        self._threadLst.append(p)



    def Loop(self, threadInfoInterval):
        inputHandler = InputHandler()

        doRun = True
        sleepSec = 0.5
        nextThreadInfo = datetime.utcnow() + timedelta(seconds=threadInfoInterval)
        while doRun:
            try:
                # save some cpu
                sleep(sleepSec)

                # input
                ch = inputHandler.ConsumeChar()
                if ch is not None:
                    if ch == u'\x03':  # CTRL+C
                        raise KeyboardInterrupt()
                    elif ch == u't':  # t = threads
                        # print threadinfo now
                        nextThreadInfo = datetime.utcnow()
                    else:
                        print "UNKNOWN KEY PRESSED:", repr(ch), "\n"

                # start threads
                now = self._dt2sec(datetime.utcnow())
                toStart = []
                with self._lock:
                    for key in [k for k in self._timeDict if k <= now]:
                        toStart += self._timeDict.pop(key)
                for start in toStart:
                    self.RunAndRequeue(start['func'], start['every'], *start['args'], **start['kwargs'])
                toStart = []

                # exit if all managed threads are done
                if not self._keepRunning:
                    running = self._threadInfo()
                    if not len(running):
                        doRun = False

                #thread info every seconds
                if nextThreadInfo < datetime.utcnow():
                    running = self._threadInfo()
                    if (not self._keepRunning) and not len(running):
                        doRun = False
                    else:
                        if not  self._keepRunning:
                            print "Received CTRL+C, exiting gracefully."
                        self._printThreadInfo(running)
                    nextThreadInfo = datetime.utcnow() + timedelta(seconds=threadInfoInterval)
            except KeyboardInterrupt:
                if not self._keepRunning:
                    print "Received CTRL+C again, exiting now."
                    sys.exit(1)
                self._keepRunning = False
                self._stopEvent.set()
                print "Received CTRL+C, exiting gracefully."
            except Exception as ex:
                print("%s" % (repr(ex)))
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_tb(exc_traceback, file=sys.stdout)
        print "::: THREADS Done  :::"

    def _threadInfo(self):
        running = []
        # get threads
        while self._threadLst:
            p = self._threadLst.pop()
            if p.isAlive():
                running.append(p) #TODO: do not append p itself, it may be unavailable later.
        # add the running threads back to the list
        for p in running:
            self._threadLst.append(p)
        # return a copy of running threads
        return running
    def _printThreadInfo(self, threads):
        if len(threads):
            pTextLst = []
            for p in threads:
                pTextLst.append("%s : %s" % (str(p.ident).rjust(20,' '), p.name))
            print ":::::::::::::::::::::::::::::::::::: THREADS Running ::::::::::::::::::::::::::::::::::::\n       ", "\n        ".join(sorted(pTextLst)), "\n"
        else:
            print "::::::::::::::::::::::::::::::::: No THREADS Running ::::::::::::::::::::::::::::::::::::\n"

# demo usage
# we want to run this task every 15s, sometimes it takes longer, where it will be restarted immediatly after ending.
def exampleTask(stopEvent):
    from random import Random
    sleepSec = Random().randint(0, 30)
    print "I will run ", sleepSec, "Seconds now."
    end = datetime.utcnow() + timedelta(seconds=sleepSec)
    while not stopEvent.is_set() and end > datetime.utcnow():
        sleep(1)
    if stopEvent.is_set():
        print "StopEvent asked me to stop."
    else:
        print "Done after", sleepSec, "."

if __name__ == "__main__":
    profilerPath = "./log"
    loop = DoEvery(profilerPath)

    # every task will run every 10 seconds, but no task will be started twice.
    # Tasks running longer than that will be restarted after finished.
    # Parameters: runnable, seconds, parameters. Pass the StopEvent to exit when the application asks to:
    loop.RunAndRequeue(exampleTask, 15, loop.StopEvent)

    loop.Loop(threadInfoInterval=10)
    print "Program ended. Wait for Threads to finish."
