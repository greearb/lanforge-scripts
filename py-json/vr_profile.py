import time
from pprint import pprint
from random import randint
from geometry import Rect, Group

from LANforge import LFUtils
from realm import BaseProfile


class VRProfile(BaseProfile):
    Default_Margin = 15 # margin between routers and router connections
    Default_VR_height = 250
    Default_VR_width = 50

    """
    Virtual Router profile
    """
    def __init__(self,
                 local_realm,
                 debug=False):
        super().__init__(local_realm=local_realm,
                         debug=debug)
        self.vr_eid = None
        self.created_rdds = []
        self.created_vrcxs = []

        # self.vrcx_data = {
        #     'shelf': 1,
        #     'resource': 1,
        #     'vr-name': None,
        #     'local_dev': None,  # outer rdd
        #     'remote_dev': None,  # inner rdd
        #     "x": 200+ran,
        #     "y": 0,
        #     "width": 10,
        #     "height": 10,
        #     'flags': 0,
        #     "subnets": None,
        #     "nexthop": None,
        #     "vrrp_ip": "0.0.0.0"
        # }
        #
        # self.set_port_data = {
        #     "shelf": 1,
        #     "resource": 1,
        #     "port": None,
        #     "ip_addr": None,
        #     "netmask": None,
        #     "gateway": None
        # }

    """
        https://unihd-cag.github.io/simple-geometry/reference/rect.html
    """

    def get_netsmith_bounds(self):
        pass

    def get_all_vrcx_bounds(self):
        pass

    def vr_to_rect(self, vr_dict=None):
        return self.to_rect(x=int(vr_dict["x"]),
                            y=int(vr_dict["y"]),
                            width=int(vr_dict["width"]),
                            height=int(vr_dict["height"]))

    def to_rect(self, x=0, y=0, width=10, height=10):
        rect = Rect(x=int(x), y=int(y), width=int(width), height=int(height));
        return rect

    def get_occupied_area(self,
                          resource=1,
                          debug=False):
        debug |= self.debug
        if (resource is None) or (resource == 0) or ("" == resource):
            raise ValueError("resource needs to be a number greater than 1")

        router_map = self.router_list(resource=resource, debug=debug)
        vrcx_map = self.vrcx_list(resource=resource, debug=debug)

        rect_list = []
        for eid,item in router_map.items():
            rect_list.append(self.vr_to_rect(item))
        for eid,item in vrcx_map.items():
            rect_list.append(self.vr_to_rect(item))
        if len(rect_list) < 1:
            return None
        bounding_group = Group()
        for item in rect_list:
            #if debug:
            #    pprint(("item:", item))
            bounding_group.append(item)
        bounding_group.update()
        #if debug:
        #    pprint(("bounding:", bounding_group))
        #    time.sleep(5)

        return Rect(x=bounding_group.x,
                    y=bounding_group.y,
                    width=bounding_group.width,
                    height=bounding_group.height)

    def vrcx_list(self, resource=None, debug=False):
        debug |= self.debug
        list_of_vrcx = self.json_get("/vrcx/1/%s/list?fields=eid,x,y,height,width"%resource,
                                     debug_=debug)
        mapped_vrcx = LFUtils.list_to_alias_map(json_list=list_of_vrcx,
                                                from_element="router-connections",
                                                debug_=debug)
        return mapped_vrcx

    def router_list(self,
                    resource=None,
                    debug=False):
        debug |= self.debug
        list_of_routers = self.json_get("/vr/1/%s/list?fields=eid,x,y,height,width"%resource,
                                        debug_=debug)

        mapped_routers = LFUtils.list_to_alias_map(json_list=list_of_routers,
                                                   from_element="virtual-routers",
                                                   debug_=debug)
        return mapped_routers

    def create_rdd(self,
                   resource=1,
                   ip_addr=None,
                   netmask=None,
                   gateway=None,
                   suppress_related_commands_=True,
                   debug_=False):
        rdd_data = {
            "shelf": 1,
            "resource": resource,
            "port": "rdd0",
            "peer_ifname": "rdd1"
        }
        # print("creating rdd0")
        self.json_post("/cli-json/add_rdd",
                       rdd_data,
                       )

        rdd_data = {
            "shelf": 1,
            "resource": resource,
            "port": "rdd1",
            "peer_ifname": "rdd0"
        }
        # print("creating rdd1")
        # self.json_post("/cli-json/add_rdd",
        #                rdd_data,
        #                suppress_related_commands_=suppress_related_commands_,
        #                debug_=debug_)
        #
        # self.set_port_data["port"] = "rdd0"
        # self.set_port_data["ip_addr"] = gateway
        # self.set_port_data["netmask"] = netmask
        # self.set_port_data["gateway"] = gateway
        # self.json_post("/cli-json/set_port",
        #                self.set_port_data,
        #                suppress_related_commands_=suppress_related_commands_,
        #                debug_=debug_)
        #
        # self.set_port_data["port"] = "rdd1"
        # self.set_port_data["ip_addr"] = ip_addr
        # self.set_port_data["netmask"] = netmask
        # self.set_port_data["gateway"] = gateway
        # self.json_post("/cli-json/set_port",
        #                self.set_port_data,
        #                suppress_related_commands_=suppress_related_commands_,
        #                debug_=debug_)
        #
        # self.created_rdds.append("rdd0")
        # self.created_rdds.append("rdd1")

    def create_vrcx(self,
                    resource=1,
                    local_dev=None,
                    remote_dev=None,
                    subnets=None,
                    nexthop=None,
                    flags=0,
                    suppress_related_commands_=True,
                    debug_=False):
        if self.vr_name is not None:
            self.vrcx_data["resource"] = resource
            self.vrcx_data["vr_name"] = self.vr_name
            self.vrcx_data["local_dev"] = local_dev
            self.vrcx_data["remote_dev"] = remote_dev
            self.vrcx_data["subnets"] = subnets
            self.vrcx_data["nexthop"] = nexthop
            self.vrcx_data["flags"] = flags
            self.json_post("/cli-json/add_vrcx",
                           self.vrcx_data,
                           suppress_related_commands_=suppress_related_commands_,
                           debug_=debug_)
        else:
            raise ValueError("vr_name must be set. Current name: %s" % self.vr_name)

    def find_position(self, eid=None, target_group=None, debug=False):
        debug |= self.debug
        """
        get rectangular coordinates of VR or VRCX
        :param eid:
        :param target_group:
        :return:
        """
        pass

    def next_available_area(self,
                            go_right=True,
                            go_down=False,
                            debug=False,
                            height=Default_VR_height,
                            width=Default_VR_width):
        """
        Returns a coordinate adjacent to the right or bottom of the presently occupied area with a 15px margin.
        :param go_right: look to right
        :param go_down: look to bottom
        :param debug:
        :return: rectangle that that next next VR could occupy
        """
        debug |= self.debug

        # pprint(("used_vrcx_area:", used_vrcx_area))
        # print("used x %s, y %s" % (used_vrcx_area.right+15, used_vrcx_area.top+15 ))

        if not (go_right or go_down):
            raise ValueError("Either go right or go down")

        used_vrcx_area = self.get_occupied_area(resource=self.vr_eid[1], debug=debug)
        next_area = None
        if (go_right):
            next_area = Rect(x=used_vrcx_area.right+15,
                            y=15,
                            width=50,
                            height=250)
        elif (go_down):
            next_area = Rect(x=15,
                            y=used_vrcx_area.bottom+15,
                            width=50,
                            height=250)
        else:
            raise ValueError("Unexpected positioning")

        # pprint(("next_rh_area", next_area))
        # print("next_rh_area: right %s, top %s" % (next_area.right, next_area.top ))
        # print("next_rh_area: x %s, y %s" % (next_area.x, next_area.y ))
        return next_area

    def move_vrcx(self, debug=False):
        debug |= self.debug


    def move_vr(self, eid=None, go_right=True, go_down=False, upper_left_x=None, upper_left_y=None, debug=False):
        """

        :param edit: virtual router EID
        :param go_right: select next area to the right of things
        :param go_down: select next area below all things
        :param upper_left_x: integer value for specific x
        :param upper_left_y: integer value for specific y
        :return:
        """
        debug |= self.debug
        used_vrcx_area = self.get_occupied_area(resource=self.vr_eid[1], debug=debug)

    def create(self,
               vr_name=None,
               # upstream_port=None,
               # upstream_subnets=[],
               # upstream_nexthop=None,
               # local_subnets=[],
               # local_nexthop=None,
               debug=False,
               suppress_related_commands_=True):
        # Create vr
        debug |= self.debug

        if vr_name is None:
            raise ValueError("vr_name must be set. Current name: %s" % vr_name)

        self.vr_eid = self.parent_realm.name_to_eid(vr_name)

        # determine a free area to place a router
        next_area = self.next_available_area(go_right=True)
        self.add_vr_data = {
            "alias": self.vr_eid[2],
            "shelf": 1,
            "resource": self.vr_eid[1],
            "x":  int(next_area.x),
            "y":  15,
            "width": 50,
            "height": 250,
            "flags": 0
        }
        self.json_post("/cli-json/add_vr", self.add_vr_data, debug_=debug)
        self.json_post("/cli-json/apply_vr_cfg", {
            "shelf": 1,
            "resource": self.vr_eid[1]
        }, debug_=debug)
        time.sleep(1)
        self.json_post("/cli-json/nc_show_vr", {
            "shelf": 1,
            "resource": self.vr_eid[1],
            "router": "all"
        }, debug_=debug)
        self.json_post("/cli-json/nc_show_vrcx", {
            "shelf": 1,
            "resource": self.vr_eid[1],
            "cx_name": "all"
        }, debug_=debug)
        self.refresh_gui(self.vr_eid[1], debug)

        # # Create 1 rdd pair
        # self.create_rdd(resource=resource, ip_addr=rdd_ip, gateway=rdd_gateway,
        #                 netmask=rdd_netmask)  # rdd0, rdd1; rdd0 gateway, rdd1 connected to network
        #
        # # connect rdds and upstream
        # self.create_vrcx(resource=resource, local_dev=upstream_port, remote_dev="NA", subnets=upstream_subnets,
        #                  nexthop=upstream_nexthop,
        #                  flags=257, suppress_related_commands_=suppress_related_commands_, debug_=debug)
        # self.create_vrcx(resource=resource, local_dev="rdd0", remote_dev="rdd1", subnets=local_subnets,
        #                  nexthop=local_nexthop,
        #                  flags=1, suppress_related_commands_=suppress_related_commands_, debug_=debug)

        # move a

    def remove_vr(self, eid=None,
                  refresh=True,
                  debug=False,
                  delay=0.05,
                  die_on_error=False):

        if (eid is None) or (eid[1] is None) or (eid[2] is None):
            self.logg("remove_vr: invalid eid: ", audit_list=[eid])
            if (die_on_error):
                raise ValueError("remove_vr: invalid eid: "+eid)
        data = {
            "shelf": 1,
            "resource": eid[1],
            "router_name": eid[2]
        }
        self.json_post("/cli-json/rm_vr", data, debug_=self.debug)
        time.sleep(delay)
        if (refresh):
            self.json_post("/cli-json/nc_show_vr", {
                "shelf": 1,
                "resource": eid[1],
                "router": "all"
            }, debug_=self.debug)
            self.json_post("/cli-json/nc_show_vrcx", {
                "shelf": 1,
                "resource": eid[1],
                "cx_name": "all"
            }, debug_=self.debug)

    def cleanup(self, resource=0, vr_id=0, delay=0.3, debug=False):
        debug |= self.debug
        if self.vr_eid is None:
            return
        if resource == 0:
            resource = self.vr_eid[1]
        if vr_id == 0:
            vr_id = self.vr_eid[2]

        data = {
            "shelf": 1,
            "resource": resource,
            "router_name": vr_id
        }
        self.json_post("/cli-json/rm_vr", data, debug_=debug)
        time.sleep(delay)
        self.refresh_gui(resource, debug)

    def refresh_gui(self, resource=0, delay=0.03, debug=False):
        debug |= self.debug
        self.json_post("/cli-json/nc_show_vr", {
            "shelf": 1,
            "resource": resource,
            "router": "all"
        }, debug_=debug)
        time.sleep(delay)
        self.json_post("/cli-json/nc_show_vrcx", {
            "shelf": 1,
            "resource": resource,
            "cx_name": "all"
        }, debug_=debug)
        time.sleep(delay * 2)
        self.json_post("/vr/1/%s/%s" % (resource, 0), {
            "action":"refresh"
        }, debug_=True)
#