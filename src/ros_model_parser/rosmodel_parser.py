#!/usr/bin/env python
#
# Copyright 2020 Fraunhofer Institute for Manufacturing Engineering and Automation (IPA)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pprint
from pyparsing import *
import ros_metamodels.ros_metamodel_core as rosmodel

# TODO: extract nodes, topics, services, etc from 'result'
# Compute Connections


# stateless functions
def parseActionStr(string, location, tokens):
    if((len(tokens[0]) == 1) and (type(tokens[0][0]) == str)):
        return tokens[0][0]


def parseActionDict(string, location, tokens):
    dict_list = list()
    for toks in tokens:
        param_dict = dict()
        for tok in toks:
            param_dict[tok[0]] = tok[1]
        dict_list.append(param_dict)
    return dict_list


class RosModelParser(object):
    def __init__(self, model, isFile=True):
        # OCB = Open Curly Bracket {}
        # CCB = Close Curly Bracket }
        # ORB = Open Round Bracket (
        # CRB = Close Round Bracket )
        # SQ = Single Quotes '
        # OSB = Open Square Bracket [
        # CSB = Close Square Bracket ]

        OCB, CCB, ORB, CRB, SQ, OSB, CSB = map(Suppress, "{}()'[]")
        name = Optional(SQ) + Word(printables,
                                   excludeChars="{},'") + Optional(SQ)

        real = Combine(Word(nums) + '.' + Word(nums))

        listStr = Forward()
        mapStr = Forward()
        param_value = Forward()

        sglQStr = QuotedString("'", multiline=True)
        string_value = Dict(
            Group(sglQStr + ZeroOrMore(OCB + param_value + CCB)))

        string_value.setParseAction(parseActionStr)
        values = (Combine(Optional("-") + real) | Combine(Optional("-") + Word(nums))).setParseAction(
            lambda tokens: float(tokens[0])) | string_value | Keyword("false") | Keyword("true") | listStr | mapStr

        _packageSet = Keyword("PackageSet").suppress()
        #_package = Keyword("package").suppress()
        _catkin_pkg = Keyword("CatkinPackage").suppress()
        #_artifact = Keyword("artifact").suppress()
        _artifacts = Keyword("Artifact").suppress()
        #_node = Keyword("node").suppress()
        _nodes = Keyword("Node").suppress()
        _name = CaselessKeyword("name").suppress()

        # Types
        _srv_type= Keyword("service").suppress()
        _topic_type= Keyword("message").suppress()
        _act_type = Keyword("action").suppress()

        # Service Server
        _service_svrs= Keyword("ServiceServers").suppress()
        _service_svr= Keyword("ServiceServer").suppress()
        service_svr = Group( _service_svr + OCB + _name + name("name") + _srv_type + name("service") + CCB)
        service_svrs = (_service_svrs + OCB + OneOrMore(service_svr + Optional(",").suppress()) + CCB)

        # Service Client
        _service_clis= Keyword("ServiceClients").suppress()
        _service_cli= Keyword("ServiceClient").suppress()
        service_cli = Group( _service_cli + OCB + _name + name("name") + _srv_type + name("service") + CCB)
        service_clis = (_service_clis + OCB + OneOrMore(service_cli + Optional(",").suppress()) + CCB)

        # Action Server
        _action_svrs= Keyword("ActionServers").suppress()
        _action_svr= Keyword("ActionServer").suppress()
        action_svr = Group( _action_svr + OCB + _name + name("name") + _act_type + name("action") + CCB)
        action_svrs = (_action_svrs + OCB + OneOrMore(action_svr + Optional(",").suppress()) + CCB)

        # Action Client
        _action_clis= Keyword("ActionClients").suppress()
        _action_cli= Keyword("ActionClient").suppress()
        action_cli = Group( _action_cli + OCB + _name + name("name") + _act_type + name("action") + CCB)
        action_clis = (_action_clis + OCB + OneOrMore(action_cli + Optional(",").suppress()) + CCB)

        # Publisher
        _pubs= Keyword("Publishers").suppress()
        _pub= Keyword("Publisher").suppress()
        pub = Group( _pub + OCB + _name + name("name") + _topic_type + name("message") + CCB)
        pubs = (_pubs + OCB + OneOrMore(pub + Optional(",").suppress()) + CCB)

        # Subscriber
        _subs= Keyword("Subscribers").suppress()
        _sub= Keyword("Subscriber").suppress()
        sub = Group( _sub + OCB + _name + name("name") + _topic_type + name("message") + CCB)
        subs = (_subs + OCB + OneOrMore(sub + Optional(",").suppress()) + CCB)

        # Parameter
        _params= Keyword("Parameters").suppress()
        _param= Keyword("Parameter").suppress()
        _type= Keyword("type").suppress()
        param = Group( _sub + OCB + _name + name("name") + _type + name("type") + CCB)
        params = (_params + OCB + OneOrMore(param + Optional(",").suppress()) + CCB)

        self.rospkg_grammar = _packageSet + \
            OCB + \
            _catkin_pkg + name("pkg_name") + OCB + \
            _artifacts + name("artifact_name") + OCB + \
            _nodes + OCB + _name + name("node_name") + \
            Optional(service_svrs)("svr_servers") + \
            Optional(service_clis)("svr_clients") + \
            Optional(action_svrs)("act_servers") + \
            Optional(action_clis)("act_clients") + \
            Optional(pubs)("publishers") + \
            Optional(subs)("subscribers") + \
            Optional(params)("parameters")

        self._isFile = isFile
        self._model = model


    def _parse_from_string(self):
        self._result = self.rospkg_grammar.parseString(self._model)

    def _parse_from_file(self):
        self._result = self.rospkg_grammar.parseFile(self._model)

    def parse(self):
        self._result = ParseResults()
        try:
            if self._isFile:
                self._parse_from_file()
            else:
                self._parse_from_string()
        except Exception as e:
            print(e.args)   # Should set a default 'result'?
        ros_model = rosmodel.RosModel()
        ros_node = rosmodel.Node(self._result.get("node_name"))

        try:
          [ros_node.add_service_server(srv_ser.get("name"), srv_ser.get("service")) for srv_ser in self._result.get("svr_servers") if self._result.get("svr_servers") is not None]
          [ros_node.add_service_client(srv_cli.get("name"), srv_cli.get("service")) for srv_cli in self._result.get("svr_clients") if self._result.get("svr_clients") is not None]
          [ros_node.add_action_server(act_ser.get("name"), act_ser.get("action")) for act_cli in self._result.get("act_servers") if self._result.get("act_servers") is not None]
          [ros_node.add_action_client(act_cli.get("name"), act_cli.get("action")) for act_cli in self._result.get("act_clients") if self._result.get("act_clients") is not None]
          [ros_node.add_publisher(pub.get("name"), pub.get("message")) for pub in self._result.get("publishers") if self._result.get("publishers") is not None]
          [ros_node.add_subscriber(sub.get("name"), sub.get("message")) for sub in self._result.get("subscribers") if self._result.get("subscribers") is not None]
          [ros_node.add_parameter(param.get("name"), param.get("type")) for param in self._result.get("parameters") if self._result.get("parameters") is not None]
        except Exception as e:
          pass
        ros_artifact = rosmodel.Artifact(self._result.get("artifact_name"),ros_node)
        ros_package = rosmodel.Package(self._result.get("pkg_name"))
        ros_package.add_artifact(ros_artifact)
        ros_model.add_package(ros_package)

        return ros_model


if __name__ == "__main__":
    import os
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(
        my_path, "../../resources/cob_light.ros")
    print(path)

    parser = RosModelParser(path)
    try:
        print(parser.parse().dump())
    except Exception as e:
        print(e.args)

