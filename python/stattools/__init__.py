##############################################################################
#
# Copyright 2016 KPMG Advisory N.V. (unless otherwise stated)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
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
"""
Stattools is a collection of statistical methods which don't otherwise appear in numpy/root/r

At the moment, we have two sub modules:
- confidencecalc: calculate a multi-edge configence window based on confidence levels
   finds an area around the peak containing x% of the points
   by gradually lowering a watershed line through the data
   Copes with none monotonous data.
   See the example notebook for more information and usage

- hypergeometrictools: simple helper functions for hypergeometric calculations
"""
from stattools.confidencecalc import quantileCalc
