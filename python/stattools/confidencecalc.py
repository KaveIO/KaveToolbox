##############################################################################
#
# Copyright 2016 KPMG N.V. (unless otherwise stated)
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
from scipy.interpolate import InterpolatedUnivariateSpline
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.path as mpath


class quantileCalc:
    """
    This class is built for calculating the confidence intervals from the y-direction. The result will be a list of
    intervals of which the combined integral under the normalized curve reaches the desired confidence interval.

    USAGE:
    -Generate x-points-
    x = np.arange(-10*np.pi,10*np.pi,0.01)
    -Generate y-points-
    ygaus = np.exp(-0.5*((x))**2)
    -calculating the quantiles-
    qc = quantileCalc(x, ygaus)
    -the results-
    ygauslvl, intervals = qc.getVerticalQuantile()
    print  ygauslvl, intervals
    -plotting-
    qc.plot()

    """

    def __init__(self, xpts, ypts, lvl=0.682, numiter=30):
        """
        The constructor:
        It takes the input variables and stores them. It also normalizes the data and computes the vertical quantiles.

        - xpts: a numpy array with the x points of the data
        - ypts: a numpy array with the y points of the data
        - lvl: the requested confidence interval
        - numiter: the number of iterations
        """
        self.x = xpts
        self.y = ypts
        self.level = lvl
        self.niter = numiter
        self.__normalize()
        self.ylevel, self.intervals = self.__calcVerticalQuantile()


    def plot(self):
        Path = mpath.Path
        fig, ax = plt.subplots()
        xmin = self.x.min()
        xmax = self.x.max()

        path_data = [(Path.MOVETO, (xmin, self.ylevel)), (Path.LINETO, (xmax, self.ylevel))]
        x_lvl, y_lvl = self.__mkpaths(path_data)

        x_border, y_border = self.__mkpaths(path_data)

        plt.plot(self.x, self.y, 'r-', x_border, y_border, 'g-', x_lvl, y_lvl, 'g-')

        plt.fill_between(self.x, self.y, where=self.y > self.ylevel, interpolate=True, hatch='/')

        plt.show()

    def getVerticalQuantile(self):
        return self.ylevel, self.intervals

    def __mkpaths(self, path_data):
        codes, verts = zip(*path_data)
        path = mpath.Path(verts, codes)
        x, y = zip(*path.vertices)
        return x, y

    def __calcVerticalQuantile(self):
        # start from the max value
        ymax = self.y.max()
        ymin = self.y.min()
        # level adjuster methods
        adjustlvl = lambda ylvl, maxlvl, step: ylvl + step * (maxlvl - ylvl)
        raiselvl = lambda ylvl, step: adjustlvl(ylvl, ymax, step)
        lowerlvl = lambda ylvl, step: adjustlvl(ylvl, ymax, -step)

        #create the splined dataset representation
        datarep = InterpolatedUnivariateSpline(self.x, self.y)

        #walk downwards and compute integral
        step = 0.5
        ylow = raiselvl(ymin, step)
        points = []

        prevdiff = -1
        prevstep = step
        prevylow = ylow

        for i in range(self.niter):
            #create the splined dataset and solve for the roots
            points = self.__getPoints(InterpolatedUnivariateSpline(self.x, self.y - ylow).roots(), datarep)
            #print 'points', points
            integral = self.__computeIntegral(points, datarep)
            diff = abs(integral - self.level)
            #print step, ylow, diff

            if prevdiff > diff:
                #wrong direction: go back and take a smaller step
                ylow = prevylow
                step = step / 2.0
                points = self.__getPoints(InterpolatedUnivariateSpline(self.x, self.y - ylow).roots(), datarep)
                integral = self.__computeIntegral(points, datarep)

            #if integral larger than level, raise lower bound
            if integral > self.level:
                ylow = raiselvl(ylow, step)
                #if integral smaller than level, lower the lower bound
            else:
                ylow = lowerlvl(ylow, step)

            prevylow = ylow
            prevstep = step
            prevdiff = diff

        return ylow, np.array(points)

    def __normalize(self):
        val = InterpolatedUnivariateSpline(self.x, self.y).integral(self.x.min(), self.x.max())
        self.y = self.y / val

    def __computeIntegral(self, points, data):
        val = 0
        for x1, x2 in points:
            val += data.integral(x1, x2)
        return val

    def __getPoints(self, rootlist, thedata):
        points = []
        # There must be a positive integral between two points
        # two cases:
        #1) begin and end root are edge-values
        theder = lambda x: thedata.derivatives(x)[1]
        if len(rootlist) == 0:
            return [(self.x.min(), self.x.max())]
        if (theder(rootlist[0]) < 0) & (theder(rootlist[-1]) < 0):
            #only begin edge effects
            points = [(self.x.min(), rootlist[0])]
            rootlist = np.delete(rootlist, 0)
        elif (theder(rootlist[0]) > 0) & (theder(rootlist[-1]) > 0):
            #only end edge effects
            points = [(rootlist[-1], self.x.max())]
            rootlist = np.delete(rootlist, -1)
        elif (theder(rootlist[0]) > 0) & (theder(rootlist[-1]) > 0):
            #both begin and end edge effects
            points = [(self.x.min(), rootlist[0]), (rootlist[-1], self.x.max())]
            rootlist = np.delete(rootlist, 0)
            rootlist = np.delete(rootlist, -1)

        for i in range(0, len(rootlist), 2):
            points.append((rootlist[i], rootlist[i + 1]))

        return points


def getLeftQuantile(histo, level=0.67):
    """
    Gets the quantile levels from a ROOT histogram. This function calculates the integral of the normalized histogram
    and returns the bin center of the bin where the level is first reached. The computation starts from left to right.
    """
    val = 0
    integralarr = histo.GetIntegral()
    nbins = histo.GetNbinsX()
    thebin = 0
    for i in range(nbins):
        if integralarr[i] > level:
            thebin = i
            break

    val = histo.GetXaxis().GetBinCenter(thebin)
    return val


def testVerticalQuantile():
    """
    This is the test method for the vertical Quantile class
    """

    import numpy as np
    # generating data:
    x = np.arange(-10 * np.pi, 10 * np.pi, 0.01)
    ygaus = np.exp(-0.5 * ((x)) ** 2)
    qc = quantileCalc(x, ygaus)
    ygauslvl, intervals = qc.getVerticalQuantile()
    print  ygauslvl, intervals
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


if __name__ == "__main__":
    testVerticalQuantile()
