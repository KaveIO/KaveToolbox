# Small library to make correlograms. Pandas contains autocorrelations, but not general cross-correlations.
# Use autocorrelation_plot and crosscorrelation_plot to make plots, the rest is deprecated.
#
# Autored by: Lodewijk Nauta for KPMG, 2015-09-11

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import collections
from scipy.stats.stats import pearsonr
from pandas.tools.plotting import autocorrelation_plot


def crosscorrelation_plot(series1, series2, ax=None, **kwds):
    """Cross correlation plot for time series. (Correlogram)

    Parameters:
    -----------
    series1: Time series
    series2: Time series
    ax: Matplotlib axis object, optional
    kwds : keywords
        Options to pass to matplotlib plotting method

    When the two series are of unequal length,
    the smaller one will be padded with zeros to
    match the larger set.
    (Numerical Recipes 2007, page 649.)

    Returns:
    -----------
    ax: Matplotlib axis object
    """
    n1, n2 = len(series1), len(series2)
    data1, data2 = np.asarray(series1), np.asarray(series2)
    # Pad the shorter data set with zeros [Numerical Recipes 2007, page 649]
    if n1 > n2:
        data2 = np.append(data2, np.zeros(n1 - n2))
    elif n2 > n1:
        data1 = np.append(data1, np.zeros(n2 - n1))
    n = max(n1, n2)

    if ax is None:
        ax = plt.gca(xlim=(1, n), ylim=(-1.0, 1.0))
    mean1, mean2 = np.mean(data1), np.mean(data2)
    c1, c2 = np.sum((data1 - mean1) ** 2) / \
        float(n), np.sum((data2 - mean2) ** 2) / float(n)
    c1, c2 = np.sqrt(c1), np.sqrt(c2)

    def r(h):
        return ((data1[:n - h] - mean1) *
                (data2[h:] - mean2)).sum() / n / (c1 * c2)
    x = np.arange(n) + 1
    y = map(r, x)  # Note: In pandas this is called lmap
    z95 = 1.959963984540054
    z99 = 2.5758293035489004
    ax.axhline(y=z99 / np.sqrt(n), linestyle='--', color='grey')
    ax.axhline(y=z95 / np.sqrt(n), color='grey')
    ax.axhline(y=0.0, color='black')
    ax.axhline(y=-z95 / np.sqrt(n), color='grey')
    ax.axhline(y=-z99 / np.sqrt(n), linestyle='--', color='grey')
    ax.set_xlabel("Lag")
    ax.set_ylabel("Correlation")
    ax.plot(x, y, **kwds)
    if 'label' in kwds:
        ax.legend()
    ax.grid()
    return ax

# Deprecated code below


def correlogram_list(input_1, input_2, periodic=True, mode='np'):
    """Calculate the cross correlation list for list or series.

    Parameters:
    -----------
    series1: List or series
    series2: List or series
    periodic: Calculate the crosscorrelation using periodic
    boundary conditions.
    mode: correlation mode on how to calculate the cross correlation:
            'np' = np.correlate
            'pearson' = scipy.stats.stats.pearsonr
    kwargs : keywords
        Options to pass to matplotlib plotting method

    Plot the cross correlation of the two input lists.

    Returns:
    -----------
    List.
    """
    correlator = dict(np=np.correlate, pearson=pearsonr)
    assert mode in correlator.keys(), 'Mode not valid.'
    f_cor = correlator[mode]

    # Error for data length
    assert len(input_1) == len(input_2), "Length of input unequal"
    # We choose number two for no reason whatsoever. It should be symmetric.
    data = input_2
    result = []
    if not periodic:
        for i in range(len(data)):
            if i == 0:
                corr = f_cor(input_1, input_2)
            else:
                corr = f_cor(input_1[i:], input_2[:-i])
            corr = [corr[0]]
            result.append(*corr)
    elif periodic:
        coll = collections.deque(data)
        for i in range(len(data)):
            coll.rotate(1)
            corr = f_cor(input_1, list(coll))
            corr = [corr[0]]
            result.append(*list(corr))
    else:
        print 'ERROR: periodic flag not set properly.'
        return 0
    return result


def correlogram(input_1, input_2, periodic=True, mode='np', **kwargs):
    """Cross correlation plot for time series. (Correlogram)

    Parameters:
    -----------
    series1: List or series
    series2: List or series
    periodic: Calculate the crosscorrelation using periodic
    boundary conditions.
    kwargs : keywords
        Options to pass to matplotlib plotting method and
        mode.

    Plot the cross correlation of the two input lists.

    Returns:
    -----------
    Matplotlib plot.
    """
    mode = kwargs.pop('mode', 'np')  # Why is this here?
    corr_list = correlogram_list(
        input_1, input_2, periodic=periodic, mode=mode)
    plt.plot(np.arange(len(input_1)), corr_list, **kwargs)


def autocorrelogram(input_1, periodic=True, mode='np', **kwargs):
    """Autocorrelation plot for time series. (Autocorrelogram)

    Parameters:
    -----------
    input_1: List or series
    periodic: Calculate the crosscorrelation using periodic
    boundary conditions.
    kwargs : keywords
        Options to pass to matplotlib plotting method and
        mode.

    Plot the autocorrelation of the two input lists.

    Returns:
    -----------
    Matplotlib plot.
    """
    correlogram(input_1, input_1, periodic=periodic, **kwargs)
