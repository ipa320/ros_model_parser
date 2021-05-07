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


class RosSystemModelParser(object):
    def __init__(self, model, isFile=True):
        # OCB = Open Curly Bracket {
        # CCB = Close Curly Bracket }
        # ORB = Open Round Bracket (
        # CRB = Close Round Bracket )
        # SQ = Single Quotes '
        # DQ = Double Quotes "
        # OSB = Open Square Bracket [
        # CSB = Close Square Bracket ]


        OCB, CCB, ORB, CRB, SQ, DQ, OSB, CSB = map(Suppress, "{}()'\"[]")
        
        name = Optional(SQ) + Optional(DQ) + Word(printables,
                                   excludeChars="{},'") + Optional(SQ) + Optional(DQ)

        real = pyparsing_common.number.copy()

        listStr = Forward()
        mapStr = Forward()
        structStr = Forward()
        param_value = Forward()
        param_type = Forward()
        structType = Forward()

        sglQStr = QuotedString("'", multiline=True)
        string_value = Dict(
            Group(sglQStr + ZeroOrMore(OCB + param_value + CCB)))

        string_value.setParseAction(parseActionStr)
        values = (Combine(Optional("-") + real) | Combine(Optional("-") + Word(nums))).setParseAction(
            lambda tokens: float(tokens[0])) | string_value | CaselessKeyword("false")  | CaselessKeyword("true") | listStr | mapStr | structStr

        _system = Keyword("RosSystem").suppress()
        _name = CaselessKeyword("name").suppress()
        _component = Keyword("RosComponents").suppress()
        _interface = Keyword("ComponentInterface").suppress()

        # Parameter Def
        _parameters = Keyword("RosParameters").suppress()
        _parameter = Keyword("RosParameter").suppress()
        _ref_parameter = Keyword("RefParameter").suppress()
        _value = Keyword("value").suppress()

        # Subscriber Def
        _subscribers = Keyword("RosSubscribers").suppress()
        _subscriber = Keyword("RosSubscriber").suppress()
        _ref_subscriber = Keyword("RefSubscriber").suppress()

        # Subscriber Def
        _publishers = Keyword("RosPublishers").suppress()
        _publisher = Keyword("RosPublisher").suppress()
        _ref_publisher = Keyword("RefPublisher").suppress()

        # ServiceServers Def
        _services = Keyword("RosSrvServers").suppress()
        _service = Keyword("RosServiceServer").suppress()
        _ref_service = Keyword("RefServer").suppress()

        # ServiceClients Def
        _srv_clients = Keyword("RosSrvClients").suppress()
        _srv_client = Keyword("RosServiceClient").suppress()
        _ref_srv_client = Keyword("RefClient").suppress()

        # ActionServers Def
        _action_servers = Keyword("RosActionServers").suppress()
        _action_server = Keyword("RosActionServer").suppress(
        ) | Keyword("RosServer").suppress()
        _ref_server = Keyword("RefServer").suppress()

        # Actio Clients Def
        _action_clients = Keyword("RosActionClients").suppress()
        _action_client = Keyword("RosActionClient").suppress(
        ) | Keyword("RosClient").suppress()
        _ref_action_client = Keyword("RefClient").suppress()

        # Topic Connections Def
        _topic_connections = Keyword("TopicConnections").suppress()
        _topic_connection = Keyword("TopicConnection").suppress()
        _from = Keyword("From").suppress()
        _to = Keyword("To").suppress()

        # global parameters Def
        _g_parameters = Keyword("Parameters").suppress()
        _g_parameter = Keyword("Parameter").suppress()
        _type = Keyword("type").suppress()
        _value = Keyword("value").suppress()

        listStr << delimitedList(Group(OCB + delimitedList(values) + CCB))
        mapStr << (OSB + delimitedList(Group(OCB + delimitedList((Group(
            sglQuotedString.setParseAction(removeQuotes) + Suppress(":") + values))) + CCB)) + CSB)
        mapStr.setParseAction(parseActionDict)

        structPair = delimitedList(name + name + Optional(structType))
        structValue = OCB + delimitedList(name + (OCB + _value + (OCB + (name + name) + CCB) + CCB)) + CCB
        structStr << (OCB + structValue + CCB)

        param_value << _value + values

        listType = delimitedList(Group(OCB + delimitedList(name) + CCB))

        structType << Group(OCB + structPair + CCB)
        param_type << _type + (name + Optional(listType | structType))

        parameter = Group(_parameter + name("param_name") +
                          OCB + _ref_parameter + name("param_path") + Optional(param_value("param_value")) + CCB)
        parameters = (_parameters + OCB +
                      OneOrMore(parameter + Optional(",").suppress()) + CCB)

        subscriber = Group(_subscriber + name("sub_name") +
                           OCB + _ref_subscriber + name("sub_path") + CCB)
        subscribers = (_subscribers + OCB +
                       OneOrMore(subscriber + Optional(",").suppress()) + CCB)

        publisher = Group(_publisher + name("pub_name") +
                          OCB + _ref_publisher + name("pub_path") + CCB)
        publishers = (_publishers + OCB +
                      OneOrMore(publisher + Optional(",").suppress()) + CCB)

        service = Group(_service + name("srv_name") +
                        OCB + _ref_service + name("srv_path") + CCB)
        services = (_services + OCB +
                    OneOrMore(service + Optional(",").suppress()) + CCB)

        srv_client = Group(_srv_client + name("srv_name") +
                           OCB + _ref_srv_client + name("srv_path") + CCB)
        srv_clients = (_srv_clients + OCB +
                       OneOrMore(srv_client + Optional(",").suppress()) + CCB)

        action_server = Group(_action_server + name("action_name") +
                              OCB + _ref_server + name("action_path") + CCB)
        action_servers = (_action_servers + OCB +
                          OneOrMore(action_server + Optional(",").suppress()) + CCB)

        action_client = Group(_action_client + name("action_name") +
                              OCB + _ref_action_client + name("action_path") + CCB)
        action_clients = (_action_clients + OCB +
                          OneOrMore(action_client + Optional(",").suppress()) + CCB)

        topic_connection = Group(_topic_connection + name("topic_name") +
                                 OCB + _from + ORB + name("from") + CRB + _to +
                                 ORB + name("to") + CRB + CCB)

        topic_connections = (_topic_connections + OCB +
                             OneOrMore(topic_connection + Optional(",").suppress()) + CCB)

        g_parameter = Group(_g_parameter + OCB + _name + name("param_name") +
                            param_type("param_type") + Optional(param_value("param_value")) + CCB)
        g_parameters = (_g_parameters + OCB +
                      OneOrMore(g_parameter + Optional(",").suppress()) + CCB)

        interface = Group(
            _interface +
            OCB +
            _name + name("interface_name") +
            Optional(publishers)("publishers") +
            Optional(subscribers)("subscribers") +
            Optional(services)("services") +
            Optional(srv_clients)("srv_clients") +
            Optional(action_servers)("action_servers") +
            Optional(action_clients)("action_clients") +
            Optional(parameters)("parameters") +
            CCB)

        self.rossystem_grammar = _system + \
            OCB + \
            _name + name("system_name") + \
            _component + ORB + \
            OneOrMore(interface + Optional(",").suppress())("interfaces") + CRB \
            + Optional(topic_connections)("topic_connections") \
            + Optional(g_parameters)("global_parameters") + CCB
        self._model = model
        self._isFile = isFile

    def _parse_from_string(self):
        self._result = self.rossystem_grammar.parseString(self._model)

    def _parse_from_file(self):
        self._result = self.rossystem_grammar.parseFile(self._model)

    def parse(self):
        self._result = ParseResults()
        try:
            if self._isFile:
                self._parse_from_file()
            else:
                self._parse_from_string()
        except Exception as e:
            print(e.args)   # Should set a default 'result'?
        return self._result


if __name__ == "__main__":
    import os
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(
        my_path, "../../resources/robotino.rossystem")
    print(path)

    parser = RosSystemModelParser(path)
    try:
        print(parser.parse().dump())
        # print(parser.parse().interfaces[2].services)
    except Exception as e:
        print(e.args)
