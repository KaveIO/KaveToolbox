import numpy as np
# generating data:
x = np.arange(-10 * np.pi, 10 * np.pi, 0.01)
ygaus = np.exp(-0.5 * ((x)) ** 2)
qc = quantileCalc(x, ygaus)
ygauslvl, intervals = qc.getVerticalQuantile()
print '====simple Gaussian===='
print 'The y-level of the 68% interval:', ygauslvl
print 'The calculated interval:', intervals
qc.plot()

# generating data:
ygaus = np.exp(-0.5 * ((x - 5)) ** 2) + np.exp(-0.5 * ((x + 5)) ** 2)
qc = quantileCalc(x, ygaus)
ygauslvl, intervals = qc.getVerticalQuantile()
print  ygauslvl, intervals
qc.plot()

#a sin**2 function to test the edge effects
ysin = np.sin(x) ** 2
qc = quantileCalc(x, ysin)
ysinlvl, intervals = qc.getVerticalQuantile()
print ysinlvl, intervals
qc.plot()

#a complicated function:
ycomp = np.exp(-0.5 * (x / 10 ** 2)) * np.sin(x) ** 2 * x ** 2
qc = quantileCalc(x, ycomp)
ycomplvl, intervals = qc.getVerticalQuantile()
print ycomplvl, intervals
qc.plot()
