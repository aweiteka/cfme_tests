#!/usr/bin/env python

# -*- coding: utf-8 -*-

import pytest
import time
from datetime import datetime
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
    "EvmGroup-vm_user" 
    ])
#@pytest.mark.usefixtures("maximized", "setup_mgmt_systems")
@pytest.mark.usefixtures("maximized")
class TestLdap:
    # max supported depth: 4
    _node_depth=4

    def test_default_ldap_group_roles(self, mozwebqa, home_page_logged_in, ldap_group, cfme_data):
        """Tests default LDAP group RBAC roles
        
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
                if node.is_menu:
                    if node.is_enabled:
                        page = self.ensure_present(page, node, parent, depth)
                    else:
                        if parent:
                            if parent.is_enabled:
                                self.ensure_absent(page, node, parent, depth)
                else:
                    # item isn't a menu so there can't be any children
                    continue
                self.check_tree(page, node, depth-1, parent=node)

    def ensure_present(self, page, node, parent, depth):
        '''Ensure element is visible and navigate to page
        '''
        # Top nav
        if depth == self._node_depth:
            Assert.true(node.name in self.menu_items(page))
            print "+ %s" % node.name
            return page
        # submenu
        elif depth == self._node_depth - 1:
            page = self.nav_to_page(node.name, page, parent=parent.name)
            Assert.true(page.is_the_current_page)
            print "\t+ %s" % (node.name)
            return page
        # accordion
        elif depth <= self._node_depth - 2:
            if node.is_accordion:
                Assert.true(node.name in self.menu_items(page=page, accordion=True))
                print "\t\t+ %s (accordion)" % node.name
            else:
                print "\t\t%s: %s (%s)" % (node.name, node.node_type, depth)
            return page

    def ensure_absent(self, page, node, parent, depth):
        '''Ensure item is not visible
        '''
        # top nav
        if depth == self._node_depth:
            Assert.true(node.name not in self.menu_items(page))
            print "- %s" % node.name
        # submenu
        elif depth == self._node_depth - 1:
            Assert.true(node.name not in self.menu_items(page=page, parent=parent))
            print "\t- %s" % node.name
        # accordion
        elif depth <= self._node_depth - 2:
            if node.is_accordion:
                Assert.true(node.name not in self.menu_items(page=page, accordion=True))
                print "\t\t- %s (accordion)" % node.name
            else:
                print "\t\t%s: %s (%s)" % (node.name, node.node_type, depth)

    def menu_items(self, page, parent=None, accordion=None):
        if parent:
            return [item.name for item in page.header.site_navigation_menu(parent.name).items]
        elif accordion:
            return [item.name for item in page.accordion.accordion_items]
        else:
            return [item.name for item in page.header.site_navigation_menus]
            
    def nav_to_page(self, node, page, parent=None, item_type=None):
        if parent:
            return page.header.site_navigation_menu(parent).sub_navigation_menu(node).click()
        else:
            # placeholder for deep div into built-out pages
            # Infrastructure is a candidate for this
            return page

