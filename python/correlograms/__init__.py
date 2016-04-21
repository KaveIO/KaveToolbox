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
"""
 Small library to make correlograms. Pandas contains autocorrelations, but not general cross-correlations.
 Use autocorrelation_plot and crosscorrelation_plot to make plots

 The formula for the implemented version of cross-correlate is found here: 
 https://en.wikipedia.org/wiki/Cross-correlation#Time_series_analysis

 .. math:: 
     \\ro_{XX}(\\tau) = E[(X_t - \mu_X)(Y_{t+\\tau} - \mu_Y)] / (\sigma_X \sigma_Y) 
 
 This is the statistical method of calculating cross-correlations.

 Authored by: Lodewijk Nauta for KPMG, 2015-09-15
"""

import numpy as _np
import matplotlib.pyplot as _plt
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
    data1, data2 = _np.asarray(series1), _np.asarray(series2)
    # Pad the shorter data set with zeros [Numerical Recipes 2007, page 649]
    if n1 > n2:
        data2 = _np.append(data2, _np.zeros(n1 - n2))
    elif n2 > n1:
        data1 = _np.append(data1, _np.zeros(n2 - n1))
    n = max(n1, n2)

    if ax is None:
        ax = _plt.gca(xlim=(1, n), ylim=(-1.0, 1.0))
    mean1, mean2 = _np.mean(data1), _np.mean(data2)
    c1, c2 = _np.sum((data1 - mean1) ** 2) / \
        float(n), _np.sum((data2 - mean2) ** 2) / float(n)
    c1, c2 = _np.sqrt(c1), _np.sqrt(c2)

    def r(h):
        return ((data1[:n - h] - mean1) *
                (data2[h:] - mean2)).sum() / n / (c1 * c2)
    x = _np.arange(n) + 1
    y = map(r, x)  # Note: In pandas this is called lmap
    z95 = 1.959963984540054
    z99 = 2.5758293035489004
    ax.axhline(y=z99 / _np.sqrt(n), linestyle='--', color='grey')
    ax.axhline(y=z95 / _np.sqrt(n), color='grey')
    ax.axhline(y=0.0, color='black')
    ax.axhline(y=-z95 / _np.sqrt(n), color='grey')
    ax.axhline(y=-z99 / _np.sqrt(n), linestyle='--', color='grey')
    ax.set_xlabel("Lag")
    ax.set_ylabel("Correlation")
    ax.plot(x, y, **kwds)
    if 'label' in kwds:
        ax.legend()
    ax.grid()
    return ax

__all__=['autocorrelation_plot','crosscorrelation_plot']
