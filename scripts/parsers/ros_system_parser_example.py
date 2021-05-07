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

import imp

from ros_model_parser.rossystem_parser import RosSystemModelParser
from pyparsing import *
import os.path
import rospy
from rospkg import RosPack

def rossystem_parser_test():
    rp = RosPack()
    model_path = os.path.join(rp.get_path("ros_model_parser"),"resources/test.rossystem")
    rossystem_parser = RosSystemModelParser(model_path)
    static_model = rossystem_parser.parse()
    print(static_model);

if __name__ == '__main__':
    try:
        rossystem_parser_test()
    except rospy.ROSInterruptException:
        pass
