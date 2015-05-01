from confidenceCalc import quantileCalc


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
    print '====Simple Gaussian===='
    print 'Mean = 0, Sigma = 1'
    print 'The 68% confidence interval:'
    print 'Interval found at y = %f' % ygauslvl
    print 'The interval is: ', intervals
    print 'Plotting....'
    qc.plot()

    # generating data:
    ygaus = np.exp(-0.5 * ((x - 5) / 3) ** 2) + np.exp(-0.5 * ((x + 5)) ** 2)
    qc = quantileCalc(x, ygaus)
    ygauslvl, intervals = qc.getVerticalQuantile()
    print '\n====Double Gaussian===='
    print 'Mean1 = +5, Sigma1 = 3'
    print 'Mean2 = -5, Sigma2 = 1'
    print 'The 68% confidence interval:'
    print 'Interval found at y = %f' % ygauslvl
    print 'The intervals are: ', intervals
    print 'Plotting....'
    qc.plot()

    #a complicated function:
    ycomp = np.sin(x) ** 2 * x ** 2
    qc = quantileCalc(x, ycomp)
    ycomplvl, intervals = qc.getVerticalQuantile()
    print '\n====Sin^2(x) * x^2 ===='
    print 'The 68% confidence interval:'
    print 'Interval found at y = %f' % ygauslvl
    print 'The intervals are: ', intervals
    print 'Plotting....'
    qc.plot()


if __name__ == "__main__":
    testVerticalQuantile()