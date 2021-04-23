#!/usr/bin/env python
#
# Copyright 2021 Fraunhofer Institute for Manufacturing Engineering and Automation (IPA)
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

## ROS MODEL METAMODEL ##

class RosModel(object):
    def __init__(self):
        self.packages = list()

    def add_package(self, package):
        self.packages.append(package)

    def dump_xtext_model(self):
        ros_model_str = "PackageSet {\n"
        for package in self.packages:
            ros_model_str += package.dump_xtext_model() + ",\n"
        ros_model_str = ros_model_str[:-2]
        ros_model_str += "}"
        return ros_model_str

class Package(object):
    def __init__(self, name):
        self.name = name
        self.artifacts=ArtifactSet()

    def add_artifact(self, artifact):
        self.artifacts.add(artifact)

    def dump_xtext_model(self):
        ros_model_str = "  CatkinPackage "+self.name+" {\n"
        ros_model_str += self.artifacts.dump_xtext_model()
        ros_model_str += "}"
        return ros_model_str

class ArtifactSet(set):
    def get_list(self):
        return [x.get_dict() for x in self]

    def dump_xtext_model(self):
        if len(self) == 0:
            return ""
        str_ = ""
        for elem in self:
            str_ += elem.dump_xtext_model() + ",\n"
        str_ = str_[:-2]
        str_ += "}"
        return str_

class Artifact(object):
    def __init__(self, name, node):
        self.name = name
        self.node=node

    def dump_xtext_model(self):
        ros_model_str = "    Artifact "+self.name+" {\n"
        ros_model_str += self.node.dump_xtext_model()
        ros_model_str += "}"
        return ros_model_str

class Node(object):
    def __init__(self, name):
        self.name = name
        self.action_clients = InterfaceSet()
        self.action_servers = InterfaceSet()
        self.publishers = InterfaceSet()
        self.subscribers = InterfaceSet()
        self.service_clients = InterfaceSet()
        self.service_servers = InterfaceSet()
        self.params = ParameterSet()

    def add_publisher(self, name, topic_type):
      self.publishers.add(Interface(name,topic_type))
    def add_subscriber(self, name, topic_type):
      self.subscribers.add(Interface(name, topic_type))

    def add_service_server(self, name, srv_type):
      self.service_servers.add(Interface(name, srv_type))
    def add_service_client(self, name, srv_type):
      self.service_clients.add(Interface(name, srv_type))

    def add_action_client(self, name, act_type):
      self.action_servers.add(Interface(name, act_type))
    def add_action_server(self, name, act_type):
      self.action_clients.add(Interface(name, act_type))

    def add_parameter(self, name, type, value=None):
      self.params.add(Parameter(name, type, value))

    def dump_xtext_model(self):
        ros_model_str = "      Node { name " + self.name
        ros_model_str += self.service_servers.dump_xtext_model(
            "        ", "ServiceServer", "service", "ServiceServers")
        ros_model_str += self.service_clients.dump_xtext_model(
            "        ", "ServiceClients", "service", "ServiceClients")
        ros_model_str += self.publishers.dump_xtext_model(
            "        ", "Publisher", "message", "Publishers")
        ros_model_str += self.subscribers.dump_xtext_model(
            "        ", "Subscriber", "message", "Subscribers")
        ros_model_str += self.action_servers.dump_xtext_model(
            "        ", "ActionServer", "action", "ActionServers")
        ros_model_str += self.action_clients.dump_xtext_model(
            "        ", "ActionClient", "action", "ActionClients")
        ros_model_str += self.params.dump_xtext_model(
            "        ", "Parameters", "Parameters")
        ros_model_str += "}\n"
        return ros_model_str

class Interface(object):
    def __init__(self, name, type, namespace=""):
        self.fullname = name
        self.namespace = namespace
        self.name = name[len(self.namespace)-1:]
        self.type = type

    def dump_xtext_model(self, indent, name_type, interface_type):
        return ("%s%s { name '%s' %s '%s'}") % (
            indent, name_type, self.fullname, interface_type, self.type.replace("/", "."))

class Parameter(object):
    def __init__(self, name, type, value, namespace=""):
        self.fullname = name
        self.namespace = namespace
        self.name = name[len(self.namespace)-1:]
        self.value = value
        self.type = self.get_type(value)
        self.count = 0

    def __eq__(self, other):
        if self.value == other.value and self.fullname == other.fullname:
            return True
        else:
            return False

    def get_type(self, value):
        param_type = type(value)
        param_type = (str(type)).replace("<type '", "").replace("'>", "")
        if param_type == 'float':
            return 'Double'
        elif param_type == 'bool':
            return 'Boolean'
        elif param_type == 'int':
            return 'Integer'
        elif param_type == 'str':
            return 'String'
        elif param_type == 'list' or param_type == 'dict':
            if ":" in str(value):
                return 'Struct'
            else:
                return 'List'
        else:
            return param_type

    def set_value(self, value, indent):
        str_param_value = ""
        if self.type == "String":
            str_param_value += "'"+self.value+"'"
        elif self.type == "Boolean":
            str_param_value += str(self.value).lower()
        elif self.type == "List":
            str_param_value += str(self.value).replace(
                "[", "{").replace("]", "}")
        elif self.type == 'Struct':
            str_param_value += self.value_struct(self.value[0], indent+"  ")
        else:
            str_param_value += str(value)
        return str_param_value

    def get_dict(self):
        return {"Value": self.value, "Fullname": self.fullname,
                "Namespace": self.namespace, "Name": self.name}

    def dump_xtext_model(self, indent="", value=""):
        str_param = "%sParameter { name '%s' type %s " % (
            indent, self.fullname, self.type)
        if self.type == 'Struct':
            str_param += self.types_struct(self.value[0], indent)
            #str_param = str_param[:-2]
        if self.type == 'List':
            str_param += self.form_list(self.value)
        str_param += "}"
        return str_param

class InterfaceSet(set):
    def get_list(self):
        return [x.get_dict() for x in self]

    def dump_xtext_model(self, indent="", name_type="", interface_type="", name_block=""):
        if len(self) == 0:
            return ""
        str_ = ("\n%s%s {\n") % (indent, name_block)
        for elem in self:
            str_ += elem.dump_xtext_model(indent+"  ", name_type, interface_type) + ",\n"
        str_ = str_[:-2]
        str_ += "}"
        return str_

class ParameterSet(set):
    def get_list(self):
        return [x.get_dict() for x in self]

    def iteritems(self):
        return [(x.fullname, x.type) for x in self]

    def iterkeys(self):
        return [x.fullname for x in self]

    def dump_xtext_model(self, indent="", value="", name_block=""):
        if len(self) == 0:
            return ""
        str_ = ("\n%s%s {\n") % (indent, name_block)
        for elem in self:
            str_ += elem.dump_xtext_model(indent+"  ", value) + ",\n"
        str_ = str_[:-2]
        str_ += "}"
        return str_
