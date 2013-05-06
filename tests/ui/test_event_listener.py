#!/usr/bin/env python

# -*- coding: utf-8 -*-

import pytest
import time
from unittestzero import Assert
import os
import sys
import json
import subprocess
import shlex
import requests
import logging

# TODO:
# * move rhevm_api_tool credentials to file 
# * move api listener url:port to file 
#   ^^ how to do outside of test methods? cfme_data.yaml? no __init__ method


# Global variable (yuck!) used to record listener process info
listener = None

# Command(s) used to start the listener
#listener_script = '''
#source %s/.python/bin/activate
#/usr/bin/env python listener.py
#''' % (os.environ.get('HOME',''),)

logging.basicConfig(filename='test_events.log',level=logging.INFO)

def setup_module(module):
    global listener
    listener_script = "/usr/bin/env python tests/common/listener.py"
    logging.info("Starting listener ... ")
    listener = subprocess.Popen(listener_script,
            stderr=subprocess.PIPE,
            shell=True)
    logging.info("(%s)\n" % listener.pid)
    # Wait for listener to start ...
    time.sleep(1)

def teardown_module(module):
    global listener
    logging.info("\nKilling listener (%s)..." % (listener.pid))
    listener.kill()
    (stdout, stderr) = listener.communicate()
    logging.info("%s\n%s" % (stdout, stderr))

@pytest.fixture(scope="module", # IGNORE:E1101
                params=["start", "stop"])
def events(request, cfme_data):
    param = request.param
    return cfme_data.data['events']['vm_events'][param]


@pytest.mark.destructive  # IGNORE:E1101
class TestEventListener():

    # FIXME: __init__ method prevents test discovery
    #def __init__(self, cfme_data):
    #    self.listener_url = "%s:%s" % (cfme_data.data['listener']['url'], 
    #        cfme_data.data['listener']['port'])
    #    self.rhevm_script = "tests/common/rhev_api_control.py"
    #    self.rhevm_host = cfme_data.data['rhevm_api_tool']['host']
    #    self.rhevm_user = cfme_data.data['rhevm_api_tool']['user']
    #    self.rhevm_passwd = cfme_data.data['rhevm_api_tool']['passwd']

    def api_request(self, route):
        # FIXME: hard-coded URL
        listener_url = "http://localhost:8080"
        logging.debug("api request to %s%s" % (listener_url, route))
        r = requests.get(listener_url + route)
        r.raise_for_status()
        return r.json

    def json_pprint(self, j):
        print json.dumps(j, sort_keys=True, indent=4, separators=(',', ': '))

    def call_rhevm(self, vm, action):
        rhevm_script = "tests/common/rhev_api_control.py"
        # FIXME: hard-coded credentials
        rhevm_host = "https://localhost"
        rhevm_user = "administrator"
        rhevm_passwd = "password"

        call = rhevm_script + \
        " -o " + rhevm_host + \
        " -u " + rhevm_user + \
        " -p " + rhevm_passwd + \
        " -v %s -a %s" % (vm, action)
        logging.info("RHEVM call: %s" % call)
        return subprocess.check_call(call, shell=True)

    def check_db(self, req):
        max_attempts = 24
        sleep_interval = 10
        for attempt in range(1, max_attempts+1):
            try:
                assert len(self.api_request(req)) == 1
            except AssertionError as e:
                if attempt < max_attempts:
                    logging.debug("Waiting for DB (%s/%s): %s" % (attempt, max_attempts, e))
                    time.sleep(sleep_interval)
                    pass
                # Enough sleeping, something went wrong
                else:
                    logging.exception("Check DB failed. Max attempts: '%s'." % (max_attempts))
                    raise e
            else:
                # No exceptions raised
                logging.info("DB row found for '%s'" % req)
                break

        return True

    def test_check_events_list_zero(self):
        assert len(self.api_request('/events')) == 0

    def test_vm_events(self, cfme_data, events):
        vm = cfme_data.data['vm']['name']
        for k, v in cfme_data.data['events']['vm_events'].iteritems():
            if events in v:
                self.call_rhevm(vm, k)
        assert self.check_db("/events/VmRedhat/%s?event=%s" % (vm, events))

    @pytest.mark.nondestructive  # IGNORE:E1101
    @pytest.mark.usefixtures("maximized") # IGNORE:E1101
    def test_navigation(self, mozwebqa, home_page_logged_in):
        home_pg = home_page_logged_in
        ms_pg = home_pg.header.site_navigation_menu("Infrastructure").sub_navigation_menu("Management Systems").click()
        Assert.true(ms_pg.is_the_current_page)
