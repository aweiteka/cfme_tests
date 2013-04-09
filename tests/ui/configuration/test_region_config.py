# -*- coding: utf-8 -*-

import pytest
import time
from unittestzero import Assert


@pytest.fixture(scope="module",
                params=["Region: Region 0 [0]"])
def region(request):
    return request.param

@pytest.fixture(scope="module",
                params=["Zone: Active (current)"])
def zone(request):
    return request.param

@pytest.fixture(scope="module",
                params=[True])
def enable_cu_collect_clusters(request):
    return request.param

@pytest.fixture(scope="module",
                params=[True])
def enable_cu_collect_datastores(request):
    return request.param

@pytest.fixture(scope="module",
                params=["Server: EVM [2] (current)"])
def cfme_name(request):
    return request.param

@pytest.fixture(scope="module",
                params=["FIXME_IP_ADDR"])
def external_cfme_vmdb(request):
    return request.param

@pytest.fixture(scope="module",
                params=["my zone"])
def new_zone_name(request):
    return request.param

@pytest.fixture(scope="module",
                params=["zone description"])
def new_zone_description(request):
    return request.param

@pytest.fixture(scope="module",
                params=["my zone"])
def join_zone_name(request):
    return request.param

@pytest.mark.destructive
@pytest.mark.usefixtures("maximized")
class TestConfig:
    def test_enable_cu_at_region(self, mozwebqa, home_page_logged_in,
                                 region, zone, enable_cu_collect_clusters,
                                 enable_cu_collect_datastores):
        home_pg = home_page_logged_in
        c_pg = home_pg.header.site_navigation_menu("Configuration").sub_navigation_menu("Configuration").click()
        Assert.true(c_pg.is_the_current_page)
        Assert.true(len(c_pg.accordion.accordion_items) == 4, "Should be 4 accordion items")
        c_pg.accordion.accordion_items[0].click()
        name = c_pg.accordion.accordion_items[0].name
        Assert.true(name == "Settings", "Name should be 'Settings'")
        tree = c_pg.accordion.current_content
        Assert.true(tree.name == region)
        tree.root.click()
        if c_pg.toggle_region_cu_collection(enable_cu_collect_clusters, enable_cu_collect_datastores):
            c_pg = c_pg.save_changes()
            Assert.true(c_pg.flash.message == "Capacity and Utilization Collection settings saved")
        else:
            Assert.false(c_pg.save.is_displayed(), "No changes made")

    def test_set_external_cfme_vmdb(self, mozwebqa, home_page_logged_in,
                                    cfme_name, external_cfme_vmdb):
        home_pg = home_page_logged_in
        c_pg = home_pg.header.site_navigation_menu("Configuration").sub_navigation_menu("Configuration").click()
        Assert.true(c_pg.is_the_current_page)
        Assert.true(len(c_pg.accordion.accordion_items) == 4, "Should be 4 accordion items")
        c_pg.accordion.accordion_items[0].click()
        accord_name = c_pg.accordion.accordion_items[0].name
        Assert.true(accord_name == "Settings", "Name should be 'Settings'")
        tree = c_pg.accordion.current_content
        tree.children[1].twisty.expand()
        tree.children[1].children[0].twisty.expand()
        # FIXME: name and order can change; access another way
        appliance = tree.children[1].children[0].children[0]
        Assert.true(appliance.name == cfme_name)
        c_pg.validate_external_cfme_vmdb(appliance, cfme_name, external_cfme_vmdb)
        Assert.true(c_pg.flash.message == "EVM Database settings validation was successful")
        if c_pg.save_database.is_displayed():
            c_pg.save_database_and_restart()
            # FIXME: validate 2-line flash message. '\n'?
            Assert.true(c_pg.flash.message == "Database settings successfully saved, they will take effect upon EVM restart\nEvm Server: Restart successfully initiated")
            time.sleep(10)

    def test_create_zone(self, mozwebqa, home_page_logged_in, region,
                         new_zone_name, new_zone_description):
        home_pg = home_page_logged_in
        c_pg = home_pg.header.site_navigation_menu("Configuration").sub_navigation_menu("Configuration").click()
        Assert.true(c_pg.is_the_current_page)
        c_pg.accordion.accordion_items[0].click()
        accord_name = c_pg.accordion.accordion_items[0].name
        Assert.true(accord_name == "Settings", "Name should be 'Settings'")
        tree = c_pg.accordion.current_content
        Assert.true(tree.name == region)
        tree.root.click()
        c_pg.create_zone(new_zone_name, new_zone_description)
        Assert.true(c_pg.flash.message == 'Zone "%s" was added' % new_zone_name)

    def test_join_zone(self, mozwebqa, home_page_logged_in, join_zone_name):
        home_pg = home_page_logged_in
        c_pg = home_pg.header.site_navigation_menu("Configuration").sub_navigation_menu("Configuration").click()
        Assert.true(c_pg.is_the_current_page)
        c_pg.accordion.accordion_items[0].click()
        tree = c_pg.accordion.current_content
        tree.children[1].twisty.expand()
        tree.children[1].children[0].twisty.expand()
        # FIXME: name and order can change; access another way
        appliance = tree.children[1].children[0].children[1]
        c_pg = c_pg.select_zone(join_zone_name)
        if c_pg.save.is_displayed():
            c_pg.save_changes()
            # FIXME: flash message doesn't have "Server: " or "(current)" str
            app_name = appliance.name
            app_name = app_name.split()
            app_name = "%s %s" % (name[1], name[2])
            Assert.true(c_pg.flash.message == 'Configuration settings saved for EVM Server "%s" in Zone "%s"' % (app_name, join_zone_name))
