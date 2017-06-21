##############################################################################
#
# Copyright 2016 KPMG Advisory N.V. (unless otherwise stated)
#
# Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
##############################################################################
import sys
import __future__
if sys.version_info[0] < 3:
    print("The Python version is %s.%s.%s" % sys.version_info[:3])
    print("These tests require Python 3")
    sys.exit(1)

import base
import definedscripttests

mods = [definedscripttests]

if __name__ == "__main__":
    base.parallel(mods)
