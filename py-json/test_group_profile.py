#!/usr/bin/env python3
import sys
import os
import importlib


sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

lfcli_base = importlib.import_module("py-json.LANforge.lfcli_base")
LFCliBase = lfcli_base.LFCliBase


class TestGroupProfile(LFCliBase):
    def __init__(self, lfclient_host, lfclient_port, local_realm, test_group_name=None, debug_=False):
        super().__init__(lfclient_host, lfclient_port, debug_)
        self.local_realm = local_realm
        self.group_name = test_group_name
        self.cx_list = []

    def start_group(self):
        if self.group_name is not None:
            self.local_realm.json_post("/cli-json/start_group", {"name": self.group_name})
            self.local_realm.json_post("/cli-json/start_group", {"name": self.group_name})
        else:
            raise ValueError("test_group name must be set.")

    def quiesce_group(self):
        if self.group_name is not None:
            self.local_realm.json_post("/cli-json/quiesce_group", {"name": self.group_name})
        else:
            raise ValueError("test_group name must be set.")

    def stop_group(self):
        if self.group_name is not None:
            self.local_realm.json_post("/cli-json/stop_group", {"name": self.group_name})
        else:
            raise ValueError("test_group name must be set.")

    def create_group(self):
        if self.group_name is not None:
            self.local_realm.json_post("/cli-json/add_group", {"name": self.group_name})
        else:
            raise ValueError("test_group name must be set.")

    def rm_group(self):
        if self.group_name is not None:
            self.local_realm.json_post("/cli-json/rm_group", {"name": self.group_name})
        else:
            raise ValueError("test_group name must be set.")

    def add_cx(self, cx_name):
        self.local_realm.json_post("/cli-json/add_tgcx", {"tgname": self.group_name, "cxname": cx_name})

    def rm_cx(self, cx_name):
        self.local_realm.json_post("/cli-json/rm_tgcx", {"tgname": self.group_name, "cxname": cx_name})

    def check_group_exists(self):
        test_groups = self.local_realm.json_get("/testgroups/all")
        # This breaks on only one existing group, this expects an array not a single object
        if test_groups is not None and "groups" in test_groups:
            test_groups = test_groups["groups"]
            if isinstance(test_groups, dict):
                if test_groups['name'] == self.group_name:
                    return True
                else:
                    return False
            for group in test_groups:
                for _, v in group.items():
                    if v['name'] == self.group_name:
                        return True
        else:
            return False

    def list_groups(self):
        test_groups = self.local_realm.json_get("/testgroups/all")
        tg_list = []
        if test_groups and "groups" in test_groups:
            # if single test_group type == dict
            if not isinstance(test_groups, list):
                # be sure the list is not empty
                if test_groups['groups']:
                    if test_groups['groups']['name'] != '':
                        tg_list.append(test_groups['groups']['name'])
            # if multiple test_group type ==list
            else:
                for group in test_groups["groups"]:
                    for k, v in group.items():
                        tg_list.append(v['name'])
        return tg_list

    def list_cxs(self):
        test_groups = self.local_realm.json_get("/testgroups/all")
        if test_groups is not None:
            test_groups = test_groups["groups"]
            # if single test_group is not empty
            if not isinstance(test_groups, list):
                if test_groups['name'] == self.group_name:
                    return test_groups['cross connects']
            for group in test_groups:
                for k, v in group.items():
                    if v['name'] == self.group_name:
                        return v['cross connects']

        else:
            return []
