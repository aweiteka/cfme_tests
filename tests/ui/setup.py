# -*- coding: utf-8 -*-

import pytest
import time
from unittestzero import Assert

@pytest.mark.setup
@pytest.mark.destructive
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

    @pytest.mark.skipif(True)
    def test_import_reports(self):
        # see Rod for customer demo reports
        pass

@pytest.mark.setup
@py.mark.destructive
class TestSetupMgmtSystems:
    def test_discover_management_systems_starts(self, mozwebqa, home_page_logged_in, management_system_types, from_address, to_address):
        home_pg = home_page_logged_in
        ms_pg = home_pg.header.site_navigation_menu("Infrastructure").sub_navigation_menu("Management Systems").click()
        Assert.true(ms_pg.is_the_current_page)
        msd_pg = ms_pg.click_on_discover_management_systems()
        Assert.true(msd_pg.is_the_current_page)
        ms_pg = msd_pg.discover_systems(management_system_types, from_address, to_address)
        Assert.true(ms_pg.is_the_current_page)
        Assert.true(ms_pg.flash.message == "Management System: Discovery successfully initiated")

    @pytest.mark.skipif(True)
    def test_that_management_systems_discovered(self, mozwebqa):
        # Loop until the quadicon shows up?
        pass
        
    @pytest.mark.skipif(True)
    def test_add_mamagement_system_credentials(self, mozwebqa):a
        # edit mgmt system, add credentials
        pass

    @pytest.mark.skipif(True)
    def test_add_host_credentials(self, mozwebqa):
        # edit host, add default credentials
        # work-around: set "scan_via_host: false" in vmdb.yml
        pass

    @pytest.mark.skipif(True)
    def test_add_pxe_server(self, mozwebqa):
        # apagac https://github.com/apagac/miq_pages/tree/apagac_infra-PXE/tests
        pass

    @pytest.mark.skipif(True)
    def test_refresh_pxe_server(self, mozwebqa):
        # apagac https://github.com/apagac/miq_pages/tree/apagac_infra-PXE/tests
        pass

    @pytest.mark.skipif(True)
    def test_add_customization_template(self, mozwebqa):
        # apagac https://github.com/apagac/miq_pages/tree/apagac_infra-PXE/tests
        pass

@pytest.mark.setup
@py.mark.destructive
class TestSetupDataCollection:
    @pytest.mark.skipif(True)
    def test_edit_management_engine_relationship(self, mozwebqa):
        # select appliance vm
        # configuration "Edit Management Engine Relationship"
        # select and save
        pass

    @pytest.mark.skipif(True)
    def test_perform_smart_state_analysis(self, mozwebqa):
        # triggered manually for hosts, vms, etc?
        pass

    @pytest.mark.skipif(True)
    def test_enable_cu_collection_region(self, mozwebqa):
        # aweiteka has page modeled. pending jprovazn config-subpage reorg
        pass

@pytest.mark.setup
@py.mark.destructive
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

@pytest.mark.setup
@py.mark.destructive
class TestSetupReporting:
    @pytest.mark.skipif(True)
    def test_schedule_reports(self, mozwebqa):
        # schedule and email csv attachment
        pass

