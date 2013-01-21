#!/usr/bin/python
# -*- coding: utf-8 -*-
"""`This`_ is a daemon that will start a tracker and seeder for a set of
repositories

.. _This:   https://github.com/wikimedia/Sartoris/blob/master/seeder.py

"""
__license__ = """\
Copyright (c) 2013 Ryan Lane <rlane@wikimedia.org>

Permission to use, copy, modify, and distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.\
"""

import yaml
import os
import pyinotify
import signal
import socket
import sys
import threading
import time
from optparse import OptionParser
from subprocess import Popen


class SeedNotifier(threading.Thread):


    def __init__(self, notifier):
        threading.Thread.__init__(self)
        self.notifier = notifier


    def run(self):
        self.notifier.loop()


class SeedWatcher(threading.Thread):


    def __init__(self, config):
        threading.Thread.__init__(self)
        self.config = config


    def run(self):
        self.notifiers = []
        for repo, config in self.config.items():
            wm = pyinotify.WatchManager()
            mask = pyinotify.IN_MODIFY | pyinotify.IN_CREATE
            wm.watch_transient_file(config["torrent"], mask, SeedHandler)
            notifier = SeedNotifier(pyinotify.Notifier(wm))
            self.notifiers.append(notifier)
        for notifier in self.notifiers:
            notifier.start()


class SeedHandler(pyinotify.ProcessEvent):


    def _kill_process_file(self, pidfile):
        try:
            f = open(pidfile)
            pid = f.read()
            self._kill_process(pid)
            f.close()
            os.unlink(pidfile)
        except IOError:
            pass
        except OSError:
            pass


    def _kill_process(self, pid):
        pid = int(pid)
        try:
            # See if the process is running
            os.kill(pid, 0)
            # Kill the process nicely
            os.kill(pid, signal.SIGTERM)
            # Give it a short amount of time to die
            grace_time = time.time() + 2
            while time.time() < grace_time:
                done, status = os.waitpid(pid, os.WNOHANG)
                if done:
                    break
                time.sleep(0.1)
            else:
                # Timeout reached, kill it with fire
                os.kill(pid, signal.SIGKILL)
        except OSError:
            # Process isn't running
            pass


    def _update_repo(self, run_location, tracker_port, torrent, seed_location):
        try:
            ip = socket.gethostbyname(socket.gethostname())
        except socket.error:
            print "Error getting the IP address of this system"
            sys.exit(1)
        tracker_file_loc = "%s/tracker_%s" % (run_location,
                                              tracker_port)
        # Kill the old tracker
        self._kill_process_file("%s.pid" % tracker_file_loc)
        try:
            # Remove the tracker's state file, to ensure peers reconnect fresh
            os.unlink("%s.dstate" % tracker_file_loc)
        except OSError:
            pass
        # Launch a new tracker
        tpid = Popen(["/usr/bin/bttrack", "--port", "%s" % tracker_port,
                      "--dfile", "%s.dstate" % tracker_file_loc]).pid
        try:
            f = open("%s.pid" % tracker_file_loc, 'w')
            f.write("%s" % tpid)
            f.close()
        except IOError:
            print "Error writing to pidfile for tracking" \
                  "%s" % tracker_port
            self._kill_process(tpid)
        seeder_file_loc = "%s/seeder_%s" % (run_location,
                                            tracker_port)
        # Kill the old seeder
        self._kill_process_file("%s.pid" % seeder_file_loc)
        # Launch a new seeder
        spid = Popen(["/usr/local/bin/murder_client", "seed", torrent,
                      seed_location, ip]).pid
        try:
            f = open("%s.pid" % seeder_file_loc, 'w')
            f.write("%s" % spid)
            f.close()
        except IOError:
            print "Error writing to pidfile for seeding %s" % self.torrent
            self._kill_process(spid)


    def _handle_file_action(self, event):
        for repo, config in seeder.config.items():
            if event.pathname == config["torrent"]:
                self._update_repo(config["run_location"],
                                  config["tracker_port"],
                                  config["torrent"], config["seed_location"])


    def process_IN_MODIFY(self, event):
        self._handle_file_action(event)


    def process_IN_CREATE(self, event):
        self._handle_file_action(event)


def main():
    parser = OptionParser(conflict_handler="resolve")
    parser.set_usage("seeder --config=<filename>")
    parser.add_option("--config", dest="config_file",
                      help="Use the specified configuration file")
    (options, args) = parser.parse_args()
    if not options.config_file:
        parser.error("A configuration file must be specified.")
        sys.exit(1)
    try:
        f = open(options.config_file)
        config = yaml.load(f)
    except IOError:
        print "Couldn't open config file"
        sys.exit(1)
    global seeder
    seeder = SeedWatcher(config)
    seeder.start()


if __name__ == "__main__":
    main()
