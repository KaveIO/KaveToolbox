##############################################################################
#
# Copyright 2016 KPMG N.V. (unless otherwise stated)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
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
import numpy as np
from stattools import *
# generating data:
x = np.arange(-10 * np.pi, 10 * np.pi, 0.01)
ygaus = np.exp(-0.5 * ((x)) ** 2)
qc = quantileCalc(x, ygaus)
print dir(qc)
ygauslvl, intervals = qc.getquantilevertical()
print '====simple Gaussian===='
print 'The y-level of the 68% interval:', ygauslvl
print 'The calculated interval:', intervals
qc.plot()

# generating data:
ygaus = np.exp(-0.5 * ((x - 5)) ** 2) + np.exp(-0.5 * ((x + 5)) ** 2)
qc = quantileCalc(x, ygaus)
ygauslvl, intervals = qc.getquantilevertical()
print ygauslvl, intervals
qc.plot()

# a sin**2 function to test the edge effects
ysin = np.sin(x) ** 2
qc = quantileCalc(x, ysin)
ysinlvl, intervals = qc.getquantilevertical()
print ysinlvl, intervals
qc.plot()

# a complicated function:
ycomp = np.exp(-0.5 * (x / 10 ** 2)) * np.sin(x) ** 2 * x ** 2
qc = quantileCalc(x, ycomp)
ycomplvl, intervals = qc.getquantilevertical()
print ycomplvl, intervals
qc.plot()
