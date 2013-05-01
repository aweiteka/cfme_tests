# -*- coding: utf-8 -*-

import pytest
import time
from unittestzero import Assert

@pytest.mark.setup # IGNORE:E1101
@pytest.mark.destructive # IGNORE:E1101
@pytest.mark.usefixtures("maximized") # IGNORE:E1101
class TestImportData:
    def test_import_automate(self, mozwebqa, home_page_logged_in, import_automate_file):
        # base to enable provisioning: https://raw.github.com/aweiteka/cfme_test_config/master/exports/automate_model/base.xml
        home_pg = home_page_logged_in
        ms_pg = home_pg.header.site_navigation_menu("Automate").sub_navigation_menu("Import / Export").click()
        Assert.true(ms_pg.is_the_current_page)
        ms_pg = ms_pg.import_automate(import_automate_file)
        Assert.true(ms_pg.flash.message == "Import file was uploaded successfully")

    def test_import_policies(self, mozwebqa, home_page_logged_in, import_policy_file):
        # customer demo: https://raw.github.com/aweiteka/cfme_test_config/master/exports/policies/customer_demo_policies.yaml
        home_pg = home_page_logged_in
        ms_pg = home_pg.header.site_navigation_menu("Control").sub_navigation_menu("Import / Export").click()
        Assert.true(ms_pg.is_the_current_page)
        ms_pg = ms_pg.import_policies(import_policy_file)
        Assert.true(ms_pg.flash.message == "Press commit to Import")
        ms_pg = ms_pg.click_on_commit()
        Assert.true(ms_pg.flash.message == "Import file was uploaded successfully")

    def test_import_reports(self):
        report_file = "sample_reports.yaml"
        reports = "%s/tests/%s" % (os.getcwd(), report_file)

        home_pg = home_page_logged_in
        report_pg = home_pg.header.site_navigation_menu("Virtual Intelligence").sub_navigation_menu("Reports").click()
        Assert.true(report_pg.is_the_current_page)
        import_pg = report_pg.click_on_import_export()
        import_pg = import_pg.import_reports(reports)
        Assert.true(any(import_pg.flash.message.startswith(m) for m in ["Imported Report", "Replaced Report"]))

@pytest.mark.setup # IGNORE:E1101
@py.mark.destructive # IGNORE:E1101
@pytest.mark.usefixtures("maximized") # IGNORE:E1101
class TestSetupMgmtSystems:
    def test_discover_management_systems_starts(self, mozwebqa, mgmtsys_page, management_system):
        ms_pg = mgmtsys_page
        Assert.true(ms_pg.is_the_current_page)
        msd_pg = ms_pg.click_on_discover_management_systems()
        Assert.true(msd_pg.is_the_current_page)
        ms_pg = msd_pg.discover_systems(management_system["type"], management_system["discovery_range"]["start"], management_system["discovery_range"]["end"])
        Assert.true(ms_pg.is_the_current_page)
        Assert.true(ms_pg.flash.message == "Management System: Discovery successfully initiated")

    def test_management_systems_discovered(home_page_logged_in):a
        # TODO: assert specific mgmt system exists
        ms_pg = home_page_logged_in.header.site_navigation_menu("Infrastructure").sub_navigation_menu("Management Systems").click()
        sleep_time = 1
        while not len(ms_pg.quadicon_region.quadicons) > 0:
            ms_pg.selenium.refresh()
            time.sleep(sleep_time)
            sleep_time *= 2

    # TODO: Change to use a fixture that uses Add Management System, instead of Discover.
    # This will allow to more easily specify the start and end states
    @pytest.mark.usefixtures("test_management_systems_discovered") #IGNORE:E1101
    def test_edit_management_system(self, mozwebqa, mgmtsys_page, management_system):
        ms_pg = mgmtsys_page
        ms_pg.select_management_system(management_system["default_name"])
        Assert.true(len(ms_pg.quadicon_region.selected) == 1, "More than one quadicon was selected")
        mse_pg = ms_pg.click_on_edit_management_systems()
        msdetail_pg = mse_pg.edit_management_system(management_system)
        Assert.true(msdetail_pg.flash.message == "Management System \"%s\" was saved" % management_system["name"])
        Assert.true(msdetail_pg.name == management_system["name"])
        Assert.true(msdetail_pg.hostname == management_system["hostname"])
        Assert.true(msdetail_pg.zone == management_system["server_zone"])
        Assert.true(msdetail_pg.vnc_port_range == management_system["host_vnc_port"])
        # if msdetail_pg.credentials_validity == "None":
            # Try reloading the page once. If we get valid then, ok. Otherwise, failure
        # msdetail_pg.selenium.refresh()
        # Assert.true(msdetail_pg.credentials_validity == "Valid")
 
    @pytest.mark.skipif(True)
    def test_add_host_credentials(self, mozwebqa):
        # see "test_edit_management_system"
        # edit host, add default credentials
        # work-around: set "scan_via_host: false" in vmdb.yml
        pass

    def test_add_pxe_server(self, mozwebqa):
        NAME = "rhel_pxe_server"
        home_pg = home_page_logged_in
        pxe_pg = home_pg.header.site_navigation_menu("Infrastructure").sub_navigation_menu("PXE").click()
        Assert.true(pxe_pg.is_the_current_page)

        pxe_pg.accordion_region.accordion_by_name("PXE Servers").click()
        pxe_pg.accordion_region.current_content.click()

        pxe_pg.center_buttons.configuration_button.click()
        add_pg = pxe_pg.click_on_add_pxe_server()
        refreshed_pg = add_pg.select_depot_type("Network File System")

        #use default values
        refreshed_pg.new_pxe_server_fill_data(name=NAME)
        refreshed_pg.click_on_add()

        flash_message = 'PXE Server "%s" was added' % NAME

        Assert.true(refreshed_pg.flash.message == flash_message, "Flash message: %s" % refreshed_pg.flash.message)

    def test_refresh_pxe_server(self, mozwebqa):
        EXPECTED_NAMES = ["rhel63server", "winpex64"]
        PXE_SERVER_NAME = "rhel_pxe_server"
        home_pg = home_page_logged_in
        pxe_pg = home_pg.header.site_navigation_menu("Infrastructure").sub_navigation_menu("PXE").click()
        Assert.true(pxe_pg.is_the_current_page)

        pxe_pg.accordion_region.accordion_by_name("PXE Servers").click()

        children_count = len(pxe_pg.accordion_region.current_content.children)

        Assert.true(children_count > 0, "There is no PXE server")

        #TODO for now, I'm refreshing only the first PXE server in line
        pxe_pg.accordion_region.current_content.children[0].click()

        #This needs to be here. We must wait for page to refresh
        time.sleep(2)

        pxe_pg.center_buttons.configuration_button.click()

        pxe_pg.click_on_refresh()
        pxe_pg.handle_popup()

        flash_message = 'PXE Server "%s": synchronize_advertised_images_queue successfully initiated' % PXE_SERVER_NAME

        Assert.true(pxe_pg.flash.message == flash_message, "Flash message: %s" % pxe_pg.flash.message)

        for i in range(1, 8):
            try:
                #To refresh the page
                #TODO for now, I'm refreshing only the first PXE server in line
                pxe_pg.accordion_region.current_content.children[0].click()
                #This needs to be here
                time.sleep(2)
                pxe_image_names = pxe_pg.pxe_image_names()
            except NoSuchElementException:
                print("Waiting....")
                pass
            else:
                break

        for name in EXPECTED_NAMES:
            Assert.true(name in pxe_image_names, "This image has not been found: '%s'" % name)

    def test_add_customization_template(self, mozwebqa):
        home_pg = home_page_logged_in
        pxe_pg = home_pg.header.site_navigation_menu("Infrastructure").sub_navigation_menu("PXE").click()
        Assert.true(pxe_pg.is_the_current_page)

        error_text = "There should be 4 accordion items instead of %s" % len(pxe_pg.accordion_region.accordion_items)
        Assert.true(len(pxe_pg.accordion_region.accordion_items) == 4, error_text)

        pxe_pg.accordion_region.accordion_by_name("Customization Templates").click()
        pxe_pg.accordion_region.current_content.children[0].twisty.expand()
        pxe_pg.accordion_region.current_content.children[0].children[2].click()

        #This needs to be here. Configuration button is not clickable immediately.
        time.sleep(1)
        pxe_pg.center_buttons.configuration_button.click()

        copy_pg = pxe_pg.click_on_copy_template()
        copy_pg.rename_template("This is a test")
        copy_pg.select_image_type("RHEL-6")

        #This needs to be here. Add button is displayed only after a short time after selecting the image type.
        #And: 'Element must be displayed to click'
        time.sleep(1)
        added_pg = copy_pg.click_on_add()
        Assert.true(added_pg.flash.message == 'Customization Template "This is a test" was added', "Flash message: %s" % added_pg.flash.message)

@pytest.mark.setup # IGNORE:E1101
@py.mark.destructive # IGNORE:E1101
@pytest.mark.usefixtures("maximized") # IGNORE:E1101
class TestSetupDataCollection:
    @pytest.mark.skipif(True)
    def test_edit_management_engine_relationship(self, mozwebqa):
        # REQUIRED?
        # select appliance vm
        # configuration "Edit Management Engine Relationship"
        # select and save
        pass

    @pytest.mark.skipif(True)
    def test_perform_smart_state_analysis(self, mozwebqa):
        # REQUIRED?
        # triggered manually for hosts, vms, etc?
        pass

    @pytest.mark.skipif(True)
    def test_enable_cu_collection_region(self, mozwebqa):
        # REQUIRED?
        # aweiteka has page modeled.
        pass

@pytest.mark.setup # IGNORE:E1101
@py.mark.destructive # IGNORE:E1101
@pytest.mark.usefixtures("maximized") # IGNORE:E1101
class TestSetupProvisioning:
    @pytest.mark.skipif(True)
    def test_tag_infrastructure(self, mozwebqa):
        # tag templates, hosts, datastores (also clusters for rhevm)
        # "Provisioning Scope: All"
        # Taggable mixin available
        # example: https://github.com/RedHatQE/cfme_pages/blob/master/tests/test_configuration_access_control.py#L73
        pass

    @pytest.mark.skipif(True)
    def test_assign_policies_to_managment_systems(self, mozwebqa):
        # 
        pass

