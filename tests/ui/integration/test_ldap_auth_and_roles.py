#!/usr/bin/env python

# -*- coding: utf-8 -*-

import pytest
import time
from unittestzero import Assert
from pages.login import LoginPage

@pytest.mark.nondestructive  # IGNORE:E1101
@pytest.mark.parametrize("ldap_group", [
    "EvmGroup-administrator",
    "EvmGroup-approver",
    "EvmGroup-auditor",
    "EvmGroup-desktop",
    "EvmGroup-operator",
    "EvmGroup-security",
    "EvmGroup-super_administrator",
    "EvmGroup-support",
    "EvmGroup-user",
    "EvmGroup-user_limited_self_service",
    "EvmGroup-user_self_service",
    "EvmGroup-vm_user" ])
#@pytest.mark.usefixtures("maximized", "setup_mgmt_systems")
@pytest.mark.usefixtures("maximized")
class TestLdap:
    def test_default_ldap_group_roles(self, mozwebqa,  home_page_logged_in, ldap_group, cfme_data):
        """Basic default LDAP group role RBAC test
        
        Validates enabled main menu and submenus are present for default 
        LDAP group roles. Cycles through RBAC UI for assigned group as admin
        then logs in as user and tests menus are presented correctly, 
        positive (menu exists) and negative (menu does not exist) tests
        """
        home_pg = home_page_logged_in
        config_pg = home_pg.header.site_navigation_menu("Configuration").sub_navigation_menu("Configuration").click()
        Assert.true(config_pg.is_the_current_page)
        grp_pg = config_pg.click_on_access_control().click_on_groups().click_on_group(ldap_group)
        role_pg = grp_pg.click_on_role()
        role_tree = role_pg.product_features.find_node_by_name('Everything')
        print "as admin: %s" % len(role_tree.children)
        login_pg = home_page_logged_in.header.logout()
        Assert.true(login_pg.is_the_current_page, "Not on login page")
        # have root RBAC object tree so now login as user
        login_pg = LoginPage(mozwebqa)
        login_pg.go_to_login_page()
        if ldap_group.lower() not in login_pg.testsetup.credentials:
            pytest.xfail("No match in credentials file for group '%s'" % ldap_group)
        home_pg = login_pg.login(user=ldap_group.lower())
        print "as user: %s" % len(role_tree.children)
        Assert.true(home_pg.is_logged_in, "Could not determine if logged in")
        for menu in role_tree.children:
            if menu.is_checked or menu.is_checked.dim:
                Assert.true(home_pg.header.site_navigation_menu(menu.name).name == menu.name)
            #for submenu in menu.children:
            #    Assert.true(submenu.name in home_pg.header.site_navigation_menu(menu).items)

@pytest.mark.usefixtures("maximized")
class TestRole:
    def test_checkboxtree(self, mozwebqa, home_page_logged_in):
        home_pg = home_page_logged_in
        config_pg = home_pg.header.site_navigation_menu("Configuration").sub_navigation_menu("Configuration").click()
        Assert.true(config_pg.is_the_current_page)
        grp_pg = config_pg.click_on_access_control().click_on_groups().click_on_group("EvmGroup-administrator")
        role_pg = grp_pg.click_on_role()
        root = role_pg.product_features.find_node_by_name('Everything')
        #assert 1 == 0
        root.twisty.expand()
        for child in root.children:
            child.twisty.expand()
            print "%s: check? %s dim? %s" % (child.name, child.is_checked, child.is_checked_dim)
            for grandchild in child.children:
                print "   - %s: check? %s dim? %s" % (grandchild.name, grandchild.is_checked, grandchild.is_checked_dim)

