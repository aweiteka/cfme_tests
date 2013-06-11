#!/usr/bin/env python

# -*- coding: utf-8 -*-

import pytest
import time
from datetime import datetime
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
    "EvmGroup-vm_user" 
    ])
#@pytest.mark.usefixtures("maximized", "setup_mgmt_systems")
@pytest.mark.usefixtures("maximized")
class TestLdap:
    _node_depth=3

    def test_default_ldap_group_roles(self, mozwebqa, home_page_logged_in, ldap_group, cfme_data):
        """Basic default LDAP group role RBAC test
        
        Validates enabled main menu and submenus are present for default 
        LDAP group roles. Cycles through RBAC UI for assigned group as admin
        then logs in as user and tests items are presented correctly, 
        positive (menu exists) and negative (menu does not exist).
        
        Tests top nav, submenus and accordion items
        """
        start = datetime.now()

        home_pg = home_page_logged_in
        config_pg = home_pg.header.site_navigation_menu("Configuration").sub_navigation_menu("Configuration").click()
        Assert.true(config_pg.is_the_current_page)
        grp_pg = config_pg.click_on_access_control().click_on_groups().click_on_group(ldap_group)
        role_pg = grp_pg.click_on_role()
        rbac_tree = role_pg.traverse_rbac_tree(depth=self._node_depth)
        
        # have root RBAC object tree so now login as user and check items
        new_pg = LoginPage(mozwebqa)
        new_pg.go_to_login_page()
        if ldap_group.lower() not in new_pg.testsetup.credentials:
            pytest.xfail("No match in credentials file for group '%s'" % ldap_group)
        home = new_pg.login(user=ldap_group.lower())
        Assert.true(home.is_logged_in, "Could not determine if logged in")
        self.check_tree(home, rbac_tree, self._node_depth)

        print(datetime.now()-start)

    ###
    # helper functions
    ###
    def check_tree(self, page, tree, depth, parent=None):
        '''Traverse RBAC tree and validate items
        '''
        if depth > 0:
            for node in tree.children:
                if self.is_menu(node.name):
                    node.name = self.translate_menu(node.name)
                    if self.enabled(node):
                        page = self.ensure_present(page, node, parent, depth)
                    else:
                        if parent:
                            if self.enabled(parent):
                                self.ensure_absent(page, node, parent, depth)
                else:
                    # item isn't a menu so there can't be any children
                    continue
                self.check_tree(page, node, depth-1, parent=node)

    def ensure_present(self, page, node, parent, depth):
        '''Ensure item is visible
        '''
        # Top nav
        if depth == self._node_depth:
            Assert.true(page.header.site_navigation_menu(node.name).name == node.name)
            print "Present: %s" % node.name
            return page
        # submenu
        elif depth == self._node_depth - 1:
            subpage =  page.header.site_navigation_menu(parent.name).sub_navigation_menu(node.name).click()
            Assert.true(subpage.is_the_current_page)
            print "\tPresent: %s" % (node.name)
            return subpage
        # accordion (other items?)
        elif depth == self._node_depth - 2:
            if self.is_accordion(node):
                displayed_accordion = [item.name for item in page.accordion.accordion_items]
                Assert.true(node.name in displayed_accordion)
                print "\t\tAccordion: %s" % node.name
            return page

    def ensure_absent(self, page, node, parent, depth):
        '''Ensure item is not visible
        '''
        # top nav
        if depth == self._node_depth:
            displayed_menus = [item.name for item in page.header.site_navigation_menus]
            Assert.true(node.name not in displayed_menus)
            print "Absent: %s (not in %s)" % (node.name, displayed_menus)
        # submenu
        elif depth == self._node_depth - 1:
            displayed_menus = [item.name for item in page.header.site_navigation_menu(parent.name).items]
            Assert.true(node.name not in displayed_menus)
            print "\tAbsent: %s (not in %s)" % (node.name, displayed_menus)
        # TODO: ensure accordion absent

    def is_accordion(self, node):
        '''Test if node is accordion based on icon image and list of exclusions
        '''
        not_accordion_items = ["All Services",
                               "Accordions",
                               "Template Access Rules",
                               "VM Access Rules"
                               ]
        if "feature_node" in node.icon:
            if node.name not in not_accordion_items:
                return True

    def is_menu(self, menu):
        '''Filter out RBAC items that aren't represented as menus
        '''
        if menu not in ["Storage", "Buttons"]:
            return True

    def translate_menu(self, menu):
        '''translate RBAC tree string into menu string
        '''
        menu_map = {"Settings & Operations": "Configuration", 
                    "Catalogs Explorer": "Catalogs",
                    # for submenus
                    "Import/Export": "Import / Export",
                    # for accordion
                    "Import / Export": "Import/Export"}
        return menu_map.get(menu, menu)

    def enabled(self, menu):
        '''check if menu is checked or checked_dim
        '''
        if menu.is_checked or menu.is_checked_dim:
            return True

