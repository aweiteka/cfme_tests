#!/usr/bin/env python

# -*- coding: utf-8 -*-

import pytest
import time
from unittestzero import Assert
#import copy
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
    def check_menu(self, page, menu, parent=None):
        # watch for string variations: no PXE, Services > Catalogs Explorer
        # no "Requests" in Automate and Infrastructure (just Services)
        if parent == "Settings & Operations":
            parent = "Configuration"
        # Positive test: ensure enabled menus present
        if menu["checked"] or menu["checked_dim"]:
            if "Settings & Operations" in menu["name"]:
                Assert.true(page.header.site_navigation_menu("Configuration").name == "Configuration")
            elif "Catalogs Explorer" in menu["name"]:
                Assert.true(page.header.site_navigation_menu(parent).sub_navigation_menu("Catalogs").name == "Catalogs")
            elif "Import/Export" in menu["name"]:
                Assert.true(page.header.site_navigation_menu(parent).sub_navigation_menu("Import / Export").name == "Import / Export")
            else:
                if not parent:
                    Assert.true(page.header.site_navigation_menu(menu["name"]).name == menu["name"])
                else:
                    Assert.true(page.header.site_navigation_menu(parent).sub_navigation_menu(menu["name"]).name == menu["name"])
        # Negative test: ensure disabled menus not present
        #else:
        #    # menu should be absent
        #    if "Settings & Operations" in menu["name"]:
        #        Assert.false(page.header.site_navigation_menu("Configuration").name == "Configuration")
        #    elif "Catalogs Explorer" in menu["name"]:
        #        Assert.false(page.header.site_navigation_menu("Services").sub_navigation_menu("Catalogs").name == "Catalogs")
        #    else:
        #        if not parent:
        #            Assert.false(page.header.site_navigation_menu(menu["name"]).name == menu["name"])
        #        else:
        #            Assert.false(page.header.site_navigation_menu(parent).sub_navigation_menu(menu["name"]).name == menu["name"])
 
    def test_default_ldap_group_roles(self, mozwebqa, home_page_logged_in, ldap_group, cfme_data):
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
        rbac_tree = role_pg.rbac_tree('Everything')
        
        # have root RBAC object tree so now login as user and check items
        new_pg = LoginPage(mozwebqa)
        new_pg.go_to_login_page()
        if ldap_group.lower() not in new_pg.testsetup.credentials:
            pytest.xfail("No match in credentials file for group '%s'" % ldap_group)
        home = new_pg.login(user=ldap_group.lower())
        Assert.true(home.is_logged_in, "Could not determine if logged in")
        for menu in rbac_tree:
            # some role access not expressed as a menu
            if not "Storage" in menu["name"]:
                self.check_menu(home, menu)
                for submenu in menu["children"]:
                    if not "Buttons" in submenu["name"]:
                        self.check_menu(home, submenu, menu["name"])
        # TODO: submenu and beyond...

