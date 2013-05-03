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

# Global variable (yuck!) used to record listener process info
listener = None

# Command(s) used to start the listener
listener_script = '''
source %s/.python/bin/activate
/usr/bin/env python listener.py
''' % (os.environ.get('HOME',''),)

# Listener API URL
#url = 'http://localhost:8080'
url = 'http://ibm-x3250m4-04.lab.bos.redhat.com:8080'

def setup_module(module):
    global listener
    sys.stdout.write("Starting listener ... ")
    listener = subprocess.Popen(listener_script,
            stderr=subprocess.PIPE,
            shell=True)
    sys.stdout.write("(%s)\n" % listener.pid)
    # Wait for listener to start ...
    time.sleep(1)

def teardown_module(module):
    global listener
    print "\nKilling listener (%s)..." % (listener.pid)
    listener.kill()
    (stdout, stderr) = listener.communicate()
    print "%s\n%s" % (stdout, stderr)

def is_successful(r):
    # reqeusts built-in exception handler. Is None if okay
    r.raise_for_status()
    # additional response validation:
    try:
        assert r.headers['content-type'] == "application/json", \
            "Reponse is not JSON format (%s)" % r.headers.get('content-type','UNKNOWN')
    except AssertionError as e:
        print e
        return False
    else:
        return True

def json_pprint(j):
    print json.dumps(j , sort_keys=True, indent=4, separators=(',', ': '))

def test_request_list_1():
    r = requests.get(url+'/events')
    assert is_successful(r)
    data = r.json()
    assert len(data) == 0

def test_request_put_1():
    r = requests.put(url+'/events/system-1/msgtype-1?event=etype-1')
    assert is_successful(r)
    data = r.json()
    assert data.get('result') == 'success'

def test_request_put_2():
    r = requests.put(url+'/events/system-1/msgtype-1?event=etype-2')
    assert is_successful(r)
    data = r.json()
    assert data.get('result') == 'success'

def test_request_list_2():
    r = requests.get(url+'/events')
    assert is_successful(r)
    data = r.json()
    assert len(data) == 2

def test_request_get():
    # FIXME - pytest parameterize me
    for etype in ['etype-1', 'etype-2']:
        r = requests.get(url+'/events/system-1/msgtype-1?event=%s' % etype)
        assert is_successful(r)
        data = r.json()
        assert len(data) == 1
        assert data[0].get('event') == etype

def test_request_delete_1():
    r = requests.delete(url+'/events/system-1/msgtype-1?event=etype-1')
    assert is_successful(r)
    data = r.json()
    assert data.get('result') == 'success'

def test_request_list_3():
    r = requests.get(url+'/events')
    data = r.json()
    assert len(data) == 1

def test_request_delete_2():
    r = requests.delete(url+'/events/system-1/msgtype-1?event=etype-2')
    assert is_successful(r)
    data = r.json()
    assert data.get('result') == 'success'

def test_request_list_4():
    r = requests.get(url+'/events')
    data = r.json()
    assert len(data) == 0

@pytest.mark.nondestructive  # IGNORE:E1101
class TestNavigation:
    def test_navigation(self, mozwebqa, home_page_logged_in):
        home_pg = home_page_logged_in
        infra_pg = home_pg.header.site_navigation_menu("Infrastructure").click()
        Assert.true(infra_pg.is_the_current_page)
        pxe_pg = infra_pg.header.site_navigation_menu("Infrastructure").sub_navigation_menu("PXE").click()
        Assert.true(pxe_pg.is_the_current_page)
        ms_pg = pxe_pg.header.site_navigation_menu("Infrastructure").sub_navigation_menu("Management Systems").click()
        Assert.true(ms_pg.is_the_current_page)

