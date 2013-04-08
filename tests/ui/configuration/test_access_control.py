# -*- coding: utf-8 -*-

import pytest
import time
from unittestzero import Assert

@pytest.fixture(scope="module",
                params=["myLocalGroup"])
def local_group(request):
    return request.param

@pytest.fixture(scope="module",
                params=["EvmRole-user"])
def evm_role(request):
    return request.param

@pytest.fixture(scope="module",
                params=["user-group-ad"])
def ldap_group(request):
    return request.param

@pytest.fixture(scope="module",
                params=["EvmRole-operator"])
def ldap_role(request):
    return request.param

@pytest.fixture(scope="module",
                params=["admin-user1"])
def ldap_user(request):
    return request.param

@pytest.fixture(scope="module",
                params=["Administrator"])
def ldap_admin(request):
    return request.param

@pytest.fixture(scope="module",
                params=["FIXME"])
def ldap_pass(request):
    return request.param

@pytest.fixture(scope="module",
                params=["Provisioning Scope:All"])
def group_tag(request):
    return request.param

@pytest.mark.destructive
@pytest.mark.usefixtures("maximized")
class TestConfig:
    def test_create_local_group(self, mozwebqa, home_page_logged_in, local_group, evm_role):
        home_pg = home_page_logged_in
        c_pg = home_pg.header.site_navigation_menu("Configuration").sub_navigation_menu("Configuration").click()
        Assert.true(c_pg.is_the_current_page)
        Assert.true(len(c_pg.accordion.accordion_items) == 4, "Should be 4 accordion items")
        c_pg.accordion.accordion_items[1].click()
        name = c_pg.accordion.accordion_items[1].name
        Assert.true(name == "Access Control", "Name should be 'Access Control'")
        tree = c_pg.accordion.current_content
        Assert.true(tree.children[1].name == "Groups")
        did_expand = tree.children[1].twisty.expand()
        Assert.true(did_expand)
        c_pg = c_pg.create_local_group(local_group, evm_role)
        Assert.true(c_pg.flash.message == 'Group "%s" was saved' % local_group)

    def test_create_ldap_group(self, mozwebqa, home_page_logged_in, \
            ldap_group, ldap_role, ldap_user, ldap_admin, ldap_pass):
        home_pg = home_page_logged_in
        c_pg = home_pg.header.site_navigation_menu("Configuration").sub_navigation_menu("Configuration").click()
        Assert.true(c_pg.is_the_current_page)
        Assert.true(len(c_pg.accordion.accordion_items) == 4, "Should be 4 accordion items")
        c_pg.accordion.accordion_items[1].click()
        name = c_pg.accordion.accordion_items[1].name
        Assert.true(name == "Access Control", "Name should be 'Access Control'")
        tree = c_pg.accordion.current_content
        Assert.true(tree.children[1].name == "Groups")
        did_expand = tree.children[1].twisty.expand()
        Assert.true(did_expand)
        c_pg = c_pg.create_ldap_group(ldap_group, ldap_role, ldap_user, \
                                      ldap_admin, ldap_pass)
        Assert.true(c_pg.flash.message == 'Group "%s" was saved' % ldap_group)

    def test_assign_group_tags(self, mozwebqa, home_page_logged_in, local_group, group_tag):
        home_pg = home_page_logged_in
        c_pg = home_pg.header.site_navigation_menu("Configuration").sub_navigation_menu("Configuration").click()
        Assert.true(c_pg.is_the_current_page)
        Assert.true(len(c_pg.accordion.accordion_items) == 4, "Should be 4 accordion items")
        c_pg.accordion.accordion_items[1].click()
        name = c_pg.accordion.accordion_items[1].name
        Assert.true(name == "Access Control", "Name should be 'Access Control'")
        tree = c_pg.accordion.current_content
        Assert.true(tree.children[1].name == "Groups")
        did_expand = tree.children[1].twisty.expand()
        Assert.true(did_expand)
        # TODO: improve dealing with list of fixture params
        c_pg = c_pg.assign_group_tags(local_group, group_tag.split(":"))
        Assert.true(c_pg.flash.message == "Tag edits were successfully saved")

