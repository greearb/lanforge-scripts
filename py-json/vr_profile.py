import realm
from realm import BaseProfile

class VRProfile(BaseProfile):
    """
    Virtual Router profile
    """
    def __init__(self,
                 local_realm,
                 vr_id=0,
                 debug=False):
        super().__init__(local_realm=local_realm,
                         debug=debug)
        self.vr_name = vr_id
        self.created_rdds = []
        self.created_vrcxs = []

        self.add_vr_data = {
            "alias": None,
            "shelf": 1,
            "resource": 1,
            "x": 100,
            "y": 100,
            "width": 250,
            "height": 250,
            "flags": 0
        }

        self.vrcx_data = {
            'shelf': 1,
            'resource': 1,
            'vr-name': None,
            'local_dev': None,  # outer rdd
            'remote_dev': None,  # inner rdd
            "x": 0,
            "y": 0,
            "width": 10,
            "height": 10,
            'flags': 0,
            "subnets": None,
            "nexthop": None,
            "vrrp_ip": "0.0.0.0"
        }

        self.set_port_data = {
            "shelf": 1,
            "resource": 1,
            "port": None,
            "ip_addr": None,
            "netmask": None,
            "gateway": None
        }

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
                       suppress_related_commands_=suppress_related_commands_,
                       debug_=debug_)

        rdd_data = {
            "shelf": 1,
            "resource": resource,
            "port": "rdd1",
            "peer_ifname": "rdd0"
        }
        # print("creating rdd1")
        self.json_post("/cli-json/add_rdd",
                       rdd_data,
                       suppress_related_commands_=suppress_related_commands_,
                       debug_=debug_)

        self.set_port_data["port"] = "rdd0"
        self.set_port_data["ip_addr"] = gateway
        self.set_port_data["netmask"] = netmask
        self.set_port_data["gateway"] = gateway
        self.json_post("/cli-json/set_port",
                       self.set_port_data,
                       suppress_related_commands_=suppress_related_commands_,
                       debug_=debug_)

        self.set_port_data["port"] = "rdd1"
        self.set_port_data["ip_addr"] = ip_addr
        self.set_port_data["netmask"] = netmask
        self.set_port_data["gateway"] = gateway
        self.json_post("/cli-json/set_port",
                       self.set_port_data,
                       suppress_related_commands_=suppress_related_commands_,
                       debug_=debug_)

        self.created_rdds.append("rdd0")
        self.created_rdds.append("rdd1")

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


    def create(self,
               resource=1,
               vr_name=None,
               upstream_port="eth1",
               upstream_subnets="20.20.20.0/24",
               upstream_nexthop="20.20.20.1",
               local_subnets="10.40.0.0/24",
               local_nexthop="10.40.3.198",
               rdd_ip="20.20.20.20",
               rdd_gateway="20.20.20.1",
               rdd_netmask="255.255.255.0",
               debug=False,
               suppress_related_commands_=True):
        # Create vr
        if self.debug:
            debug = True
        if self.vr_name is None:
            raise ValueError("vr_name must be set. Current name: %s" % self.vr_name)

        self.add_vr_data["alias"] = self.vr_name
        self.json_post("/cli-json/add_vr", self.add_vr_data, debug_=debug)


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

    def cleanup(self, resource, delay=0.03):
        # TODO: Cleanup for VRProfile
        pass
