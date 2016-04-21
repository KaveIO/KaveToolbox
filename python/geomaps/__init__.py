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
A simple library with plotting functions to display on a postal-code map
US map or world map.
Required packages are: Pandas, Numpy, Matplotlib
"""

import os
import time
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm
import matplotlib as mpl
from matplotlib.patches import Polygon

postcode_data = os.path.dirname(__file__) + os.sep + 'NLPostcodes.csv'
postcode_gd_polygons = os.path.dirname(__file__) + os.sep + 'geodan_postcode_data.csv'
US_polygons = os.path.dirname(__file__) + os.sep + 'US_States_Polygon_Data.csv'
world_polygons = os.path.dirname(__file__) + os.sep + 'countries.csv'
world_gdp_nom = os.path.dirname(__file__) + os.sep + 'country_gdp_nom.csv'
world_gdp_cap = os.path.dirname(__file__) + os.sep + 'country_gdp_percap.csv'


def Copyright(name, axes, side=None):
    '''
    This is the copyright module that is used in the plotting of the
    maps. By calling this function inside the plotter functions we
    can get a copyright signature in the bottom of the created plot.
    It can be on the left ('l') or the right ('r').
    Note that there is a copyright routine for the github data and
    one for the proprietary geodan data.
    '''
    props = dict(boxstyle='round', facecolor='wheat', alpha=1)
    if name == 'GitHub':
        if side.lower() == 'l':
            axes.text(0, 0, 'Map Data: github.com/johan/world.geo.json', horizontalalignment='left',
                      verticalalignment='bottom', transform=axes.transAxes, fontsize=20, bbox=props)
        elif side.lower() == 'r':
            axes.text(0.5, 0, 'Map Data: github.com/johan/world.geo.json', horizontalalignment='left',
                      verticalalignment='bottom', transform=axes.transAxes, fontsize=20, bbox=props)
    elif name == 'Geodan':
        if side.lower() == 'l':
            axes.text(0, 0, 'Postcode Data: Geodan', horizontalalignment='left', verticalalignment='bottom',
                      transform=axes.transAxes, fontsize=20, bbox=props)
        elif side.lower() == 'r':
            axes.text(0.5, 0, 'Postcode Data: Geodan', horizontalalignment='left', verticalalignment='bottom',
                      transform=axes.transAxes, fontsize=20, bbox=props)
    else:
        print 'Copyright warning: Wrong name given.'


def NumberPlot(df_tmp, min, max, plot_col, item, **kwargs):
    '''
    This plotter will make the polygons if you input
    numbers into the plot. The input is a dataframe.
    A minimum of the input numbers, a maximum, the column
    name that is going to be plotted, and a list of items
    that is missing. (Usually these items are numbers that
    are not in the dataframe when they are expected to be.
    '''
    min_val = min
    max_val = max

    missing = []
    df_tmp.reset_index(inplace=True)
    ### The function below is needed to normalize the colors properly, since they go from x_min to x_max and need to
    # be mapped into 0 to 1.
    ### The function has a feature: if the whole picture has only ONE value/color, it yields np.nan which in turn
    # makes the whole plot grey and tells you there is only one color.
    ### As soon as there is more than one value/color this does not happen, so in most cases it does not occur,
    # but in rare cases it does.
    color_number = float(df_tmp[plot_col].values[0] - min_val) / (
        max_val - min_val)  ### Cast as float because python2.7 does not do this.

    ### Defining the colorscheme.
    if 'color' in kwargs:
        themap = getattr(cm, kwargs['color'])
    else:
        themap = getattr(cm, 'Blues')

    ### Color choosing for the polygon.
    if np.isnan(color_number):
        missing.append(item)
        color = cm.Greys(0.3)
    else:
        color = themap(color_number)

    ### The edgecolor of the polygon.
    if 'edgecolor' in kwargs:
        edgecolor = kwargs['edgecolor']
    else:
        edgecolor = 'black'

    ### Define the polygon and add it to the plot.
    ### Is it a multipolygon face or a polygon face? This gives different plot styles.
    if df_tmp['type'].ix[0] == 'MultiPolygon':
        i = 0
        for j in range(len(df_tmp)):
            if (df_tmp['X'].ix[j] == df_tmp['X'].ix[i]) and (df_tmp['Y'].ix[j] == df_tmp['Y'].ix[i]) and (j > i):
                df_tmp2 = df_tmp.ix[range(i, j + 1)]
                i = j + 1
                ### Plot the polygons
                poly = plt.Polygon(df_tmp2[['X', 'Y']],
                                   facecolor=color,
                                   edgecolor=edgecolor,
                                   zorder=0
                                   )
                poly.set_linewidth(0.1)
                if 'linewidth' in kwargs:
                    poly.set_linewidth(kwargs['linewidth'])
                plt.gca().add_patch(poly)
    elif df_tmp['type'].ix[0] == 'Polygon':
        poly = plt.Polygon(df_tmp[['X', 'Y']],
                           facecolor=color,
                           edgecolor=edgecolor,
                           zorder=0
                           )
        poly.set_linewidth(0.1)
        if 'linewidth' in kwargs:
            poly.set_linewidth(kwargs['linewidth'])
        plt.gca().add_patch(poly)
    return missing


def ColorPlot(df_tmp, plot_col, item, **kwargs):
    '''
    This plotter will make the polygons if you input
    colors into the plot. The input is a dataframe.
    A minimum of the input numbers, a maximum, the column
    name that is going to be plotted, and a list of items
    that is missing. (Usually these items are colors that
    are not in the dataframe when they are expected to be.
    '''
    missing = []
    df_tmp.reset_index(inplace=True)
    color = df_tmp[plot_col][0]
    ### The edgecolor of the polygon.
    if 'edgecolor' in kwargs:
        edgecolor = kwargs['edgecolor']
    else:
        edgecolor = 'black'
    ### Check if the color is defined and adjust color if it is not.
    if not isinstance(color, str):
        if np.isnan(color):
            missing.append(item)
            color = cm.Greys(0.3)
    ### Define the polygon and add it to the plot.
    if df_tmp['type'].ix[0] == 'MultiPolygon':
        i = 0
        for j in range(len(df_tmp)):
            if (df_tmp['X'].ix[j] == df_tmp['X'].ix[i]) and (df_tmp['Y'].ix[j] == df_tmp['Y'].ix[i]) and (j > i):
                df_tmp2 = df_tmp.ix[range(i, j + 1)]
                i = j + 1
                ### Plot the polygons.
                poly = plt.Polygon(df_tmp2[['X', 'Y']],
                                   facecolor=color,
                                   edgecolor=edgecolor,
                                   zorder=0
                                   )
                poly.set_linewidth(0.1)
                if 'linewidth' in kwargs:
                    poly.set_linewidth(kwargs['linewidth'])
                plt.gca().add_patch(poly)
    elif df_tmp['type'].ix[0] == 'Polygon':
        ### Plot the polygons.
        poly = plt.Polygon(df_tmp[['X', 'Y']],
                           facecolor=color,
                           edgecolor=edgecolor,
                           zorder=0
                           )
        poly.set_linewidth(0.1)
        if 'linewidth' in kwargs:
            poly.set_linewidth(kwargs['linewidth'])
        plt.gca().add_patch(poly)
    return missing


def Plotter(df_merge, iter_column, plot_col, **kwargs):
    '''
    This is the plotter function that takes the data and generates
    the plot. It uses the NumerPlot for number input and ColorPlot
    for the color input. The function returns a string if the
    number or colorplot is succesful. If it is not, it returns 0.
    '''
    if df_merge[plot_col].dtype == 'float' or df_merge[plot_col].dtype == 'int':
        min = df_merge[plot_col].min()
        max = df_merge[plot_col].max()

    for item in df_merge[iter_column].unique():
        df_tmp = df_merge[df_merge[iter_column] == item]
        if len(df_tmp) < 3:
            print 'Warning: Invalid items to plot entered, skipping:', item
            print df_tmp
            break
        else:
            if df_tmp[plot_col].dtype == 'float' or df_tmp[plot_col].dtype == 'int':
                missing = NumberPlot(df_tmp, min, max, plot_col, item, **kwargs)
                return_val = 'Number'
            elif df_tmp[plot_col].dtype == 'object':
                missing = ColorPlot(df_tmp, plot_col, item, **kwargs)
                return_val = 'Color'
            else:
                print 'Input format erroneous.'
                return_val = 0
    if missing:
        print 'Warning: missing data at:', missing
    ### NB!!! Now it only returns the last return_val, thats not optimal.
    return return_val


def scatter(postcodes, values, **kwargs):
    """
    Extra kwargs will be forwarded to the scatter plot function.

    Parameters:

    ---

    postcodes = series data corresponding to values
    values = the value to plot in a given postcode
    postaldata = a dataframe containing the rd_x rd_y of these postcodes, if none is given then the csv in
    geomaps.postcode_data is read
    square = True, pad the x and y axis to make the plot square
    colorbar = True, add a colorbar, default true.
    """
    postaldata = None
    square = True
    colorbar = True
    if 'postcodes' in kwargs:
        postcodes = kwargs['postcodes']
        kwargs.pop('postcodes', None)
    if 'values' in kwargs:
        values = kwargs['values']
        kwargs.pop('values', None)
    if 'postaldata' in kwargs:
        postaldata = kwargs['postaldata']
        kwargs.pop('postaldata', None)
    if 'square' in kwargs:
        square = kwargs['square']
        kwargs.pop('square', None)
    if 'colorbar' in kwargs:
        colorbar = kwargs['colorbar']
        kwargs.pop('colorbar', None)
    if postaldata is None:
        if not os.path.exists(postcode_data):
            raise IOError('No postcode data at' + postcode_data)
        postaldata = pd.read_csv(postcode_data)
        postaldata['postcode'] = postaldata['pnum']
    if len(postcodes) != len(values):
        raise KeyError('postcodes and values must be of the same length')
    missing = [postcode for postcode in postcodes if postcode not in postaldata.postcode.values]
    if len(missing):
        print 'Warning: Certain postcodes will not be plotted:', missing
    df = pd.DataFrame()
    df['postcode'] = postcodes
    df['mapped'] = values
    merged = postaldata.merge(df, how='outer', left_on=['postcode'], right_on=['postcode'])
    xs = merged['rd_x']
    ys = merged['rd_y']
    kwargs['x'] = xs
    kwargs['y'] = ys
    kwargs['c'] = merged['mapped']
    xpad = 0
    ypad = 0
    try:
        xmin = min(xs)
        xmax = max(xs)
    except ValueError:
        xmax = xs.max()
        xmin = xs.min()
    try:
        ymin = min(ys)
        ymax = max(ys)
    except ValueError:
        ymax = ys.max()
        ymin = ys.min()
    plt.scatter(**kwargs)
    xsep = xmax - xmin
    ysep = ymax - ymin
    maxsep = ysep
    if xsep > ysep:
        ypad = (ysep - xsep) / 2.
        maxsep = xsep
    else:
        xpad = (xsep - ysep) / 2.
    if square:
        plt.xlim(xmin - xpad - 0.1 * maxsep, xmax + xpad + 0.1 * xsep)
        plt.ylim(ymin - ypad - 0.1 * maxsep, ymax + ypad + 0.1 * xsep)
    if 'ax' in kwargs and colorbar:
        plt.colorbar(ax=kwargs['ax'])
    elif colorbar:
        plt.colorbar()
    return (xmin - 0.05 * maxsep, xmax + 0.05 * maxsep, ymin - 0.05 * maxsep, ymax + 0.05 * maxsep)


def path(postcodes, **kwargs):
    """
    Plot the path between the input postal codes in order. This function
    works with the postal_map function.

    Parameters:

    postcodes is series data corresponding to values.

    ---
    kwargs:

    format: the format of the nodes on the path. From MatPlotLib.
    postaldata: a dataframe containing the XCOORDs and YCOORDs

    If none of the postcodes is given, then the csv in
    geomaps.postcode_data is read.
    """
    postaldata = None
    format = 'v-'
    if 'format' in kwargs:
        format = kwargs['format']
        kwargs.pop('format', None)
    if 'postcodes' in kwargs:
        postcodes = kwargs['postcodes']
        kwargs.pop('postcodes', None)
    if 'postaldata' in kwargs:
        postaldata = kwargs['postaldata']
        kwargs.pop('postaldata', None)
    if postaldata is None:
        if not os.path.exists(postcode_data):
            raise IOError('No postcode data at' + postcode_data)
        postaldata = pd.read_csv(postcode_gd_polygons)
        postaldata = postaldata.drop_duplicates(['XCOORD', 'YCOORD', 'PC4CODE']).reset_index(drop=True)
    missing = [postcode for postcode in postcodes if postcode not in postaldata.PC4CODE.values]
    if len(missing):
        print 'Warning: Certain postcodes will not be plotted:', missing
    df = pd.DataFrame()
    df['postcode'] = postcodes
    merged = postaldata.merge(df, how='inner', left_on=['PC4CODE'], right_on=['postcode'])
    xs = merged['XCOORD']
    ys = merged['YCOORD']
    if 'axes' in kwargs:
        ax = kwargs['axes']
        kwargs.pop('axes', None)
        ax.plot(xs, ys, format, **kwargs)
    else:
        print 'Due to the way MatPlotLib works you have to specify on which Axes you want to plot the Path (in kwargs).'


def postal_map(postcodes, values, location='NL', city=0, **kwargs):
    """
    Give the function a list with postalcode data and
    the values to make a plot with one color that
    represents the number per postcode.

    Parameters

    ----
    kwargs:

    location: give a city name or province name and the plot
    will automatically be cut to this area.

    city: Utrecht and Groningen are both provinces and
    cities, set this to 1 to get the city instead of the
    province.

    pc_level: average the input values on this postal code
    level.

    title: (string) give a title for the plot, if location
    is on, it will automatically be added to the title.

    sidebar: give the title of the colorbar on the side.

    linewidth: the linewidth of the polygon edges.

    color: the color of the polygon faces.

    edgecolor: the color of the polygon edges.

    size: (int) the figsize of the plot. Aspect ratio is
    automatically adjusted.

    copyright: flag set to 'l' or 'r' to indicate if the plot
    is to be published on the left or right side of the plot.
    This adds a 'Geodan' source on the plot. If the flag is
    absent, there will be no copyright stamp.
    """
    ### Grab the data.
    df = pd.DataFrame()
    df['postalcodes'] = postcodes
    df['vals'] = values
    merge_col = 'postalcodes'
    plot_col = 'vals'

    ### Postcode polygon data.
    postalPolyData = pd.read_csv(postcode_gd_polygons)

    ### Check the postalcode level and merge on the right level.
    df_tmp = df.copy()
    df_tmp['len'] = df_tmp[merge_col].apply(lambda x: len(str(int(x))))
    level = str(int(np.ceil(df_tmp.len.mean())))
    if level not in ['1', '2', '3', '4']:
        return 'Error: Postalcode data is not the right format.'
    pc_merge = pd.merge(postalPolyData, df, how='outer', left_on='PC' + level + 'CODE', right_on=merge_col)

    if 'pc_level' in kwargs:
        pc_level = str(kwargs['pc_level'])
        df_av = pc_merge.groupby('PC' + pc_level + 'CODE')[plot_col].mean().reset_index()
        pc_merge = pd.merge(postalPolyData, df_av, how='outer', left_on='PC' + pc_level + 'CODE',
                            right_on='PC' + pc_level + 'CODE')

    ### Location slicing.
    if location.upper() != 'NL':
        print 'INFO: Applying selection on location:', location.title()
        if location.title() in ['Utrecht', 'Groningen']:
            print 'Did you mean the city of the province? For city, set \'city=1\''
            if city == 1:
                pc_merge = pc_merge[pc_merge['WOONPLAATS'] == location.upper()]
            else:
                pc_merge = pc_merge[pc_merge['PROVC_NM'] == location.title()]
        else:
            if location.title() in pc_merge.PROVC_NM.unique():
                pc_merge = pc_merge[pc_merge['PROVC_NM'] == location.title()]
            elif location.upper() in pc_merge.WOONPLAATS.unique():
                pc_merge = pc_merge[pc_merge['WOONPLAATS'] == location.upper()]
            else:
                print 'Warning: Invalid location used. Location is ignored.'

    ### Range for the plot.
    minx = pc_merge['X'].min()
    maxx = pc_merge['X'].max()
    miny = pc_merge['Y'].min()
    maxy = pc_merge['Y'].max()

    ### Figure size and axes.
    ### Because of the smaller sized axes we get a non-unity aspect ratio. This has to be adjusted to get the proper
    # aspect ratio on the maps.
    ### This is done by multiplying with 1.25. (=1/0.8, since the ratio is x:y)
    if 'ax' not in kwargs:
        if 'size' in kwargs:
            size = kwargs['size']
            fig = plt.figure(figsize=(1.25 * size, size * (maxy - miny) / (maxx - minx)))
        else:
            fig = plt.figure(figsize=(1.25 * 12, 12 * (maxy - miny) / (maxx - minx)))
        ax1 = fig.add_axes([0.05, 0., 0.8, 1.0], zorder=0)
    else:
        ax1 = kwargs['ax']

    ### Plot the polygons.
    plotReturn = Plotter(pc_merge, 'PC4CODE', plot_col, **kwargs)

    ### Plot range options.
    plt.axis('off')

    plt.xlim(minx, maxx)
    plt.ylim(miny, maxy)

    ### Title kwarg.
    if 'title' in kwargs:
        title = kwargs['title']
        plt.title(title + ' (' + location.title() + ')', fontsize=20)

    ### Defining the colorscheme.
    if 'color' in kwargs:
        themap = getattr(cm, kwargs['color'])
    else:
        themap = getattr(cm, 'Blues')

    ### Sidebar with normalized colors. Sidebar is only used in number plots.
    if plotReturn == 'Number':
        ax2 = fig.add_axes([0.9, 0., 0.05, 1.0])
        ax2.tick_params(labelsize=20)
        norm = mpl.colors.Normalize(vmin=pc_merge[plot_col].min(), vmax=pc_merge[plot_col].max())
        cb1 = mpl.colorbar.ColorbarBase(ax2,
                                        cmap=themap,
                                        norm=norm
                                        )
        ### Sidebar name kwarg.
        if 'sidebar' in kwargs:
            sidebar = kwargs['sidebar']
            if pc_merge[plot_col].min() == pc_merge[plot_col].max():
                cb1.set_label(sidebar + '\nOnly one value plotted: ' + str(pc_merge[plot_col].max()), fontsize=20,
                              labelpad=20)
            else:
                cb1.set_label(sidebar, fontsize=20, labelpad=20)
        else:
            cb1.set_label('', fontsize=20, labelpad=20)

    ### Geodan copyright tag
    if 'copyright' in kwargs:
        side = kwargs['copyright']
        Copyright('Geodan', ax1, side=side)

    return ax1


def world_map(countries, values, location=['all'], **kwargs):
    """
    Give the function a dataframe that contains the codes
    of country names and the values.
    The merge_col is the column containing the postalcodes.
    The column with values will automatically then be
    plotted.

    Parameters
    ----
    kwargs:

    location: give a list of countries or continents (but
    not combinations!) and the plot will
    automatically be cut to this area. The countries have
    to be in the international shorthand notation, eg.
    SWE = Sweden.

    title: (string) give a title for the plot, if location
    is on, it will automatically be added to the title.

    sidebar: give the title of the colorbar on the side.

    linewidth: the linewidth of the polygon edges.

    color: the color of the polygon faces.

    edgecolor: the color of the polygon edges.

    size: (int) the figsize of the plot. Aspect ratio is
    automatically adjusted.

    copyright: flag set to 'l' or 'r' to indicate if the plot
    is to be published on the left or right side of the plot.
    This adds a 'Github' source on the plot. If the flag is
    absent, there will be no copyright stamp.
    """
    ### Grab the data.
    df = pd.DataFrame()
    df['countries'] = countries
    df['vals'] = values
    merge_col = 'countries'
    plot_col = 'vals'

    ### Rename the input to avoid inconsistencies.
    ### Before this point we used the external names, from this point on they are as defined below.
    df.rename(columns={merge_col: 'countries', plot_col: 'values'}, inplace=True)
    merge_col = 'countries'
    plot_col = 'values'

    ### Poly data.
    PolyData = pd.read_csv(world_polygons)

    pc_merge = pd.merge(PolyData, df, how='outer', left_on='code', right_on=merge_col)

    ### Location slicing.
    if location[0].lower() != 'all':
        location = [loc.title() for loc in location]
        print 'INFO: Applying selection on location.'
        if location[0].upper() in pc_merge.code.unique():
            location = [loc.upper() for loc in location]
            pc_merge = pc_merge[pc_merge['code'].isin(location)]
        elif location[0].title() in pc_merge.continent.unique():
            pc_merge = pc_merge[pc_merge['continent'].isin(location)]
        else:
            print 'Warning: Invalid location used. Location is ignored.'

    ### Range for the plot.
    minx = pc_merge['X'].min()
    maxx = pc_merge['X'].max()
    miny = pc_merge['Y'].min()
    maxy = pc_merge['Y'].max()

    ### Figure size and axes.
    ### Because of the smaller sized axes we get a non-unity aspect ratio. This has to be adjusted to get the proper
    # aspect ratio on the maps.
    ### This is done by multiplying with 1.25.
    if 'ax' not in kwargs:
        if 'size' in kwargs:
            size = kwargs['size']
            fig = plt.figure(figsize=(1.25 * size, size * (maxy - miny) / (maxx - minx)))
        else:
            fig = plt.figure(figsize=(1.25 * 12, 12 * (maxy - miny) / (maxx - minx)))
        ax1 = fig.add_axes([0.05, 0., 0.8, 1.0])
    else:
        ax1 = kwargs['ax']

    ### Plot the polygons.
    plotReturn = Plotter(pc_merge, 'code', plot_col, **kwargs)

    ### Plot range options.
    plt.axis('off')
    plt.xlim(minx, maxx)
    plt.ylim(miny, maxy)

    ### Title kwarg.
    if 'title' in kwargs:
        title = kwargs['title']
        plt.title(title, fontsize=20)

    ### Defining the colorscheme.
    if 'color' in kwargs:
        themap = getattr(cm, kwargs['color'])
    else:
        themap = getattr(cm, 'Blues')

    ### Sidebar with normalized colors. Sidebar is only used in number plots.
    if plotReturn == 'Number':
        ax2 = fig.add_axes([0.9, 0., 0.05, 1.0])
        ax2.tick_params(labelsize=20)
        norm = mpl.colors.Normalize(vmin=pc_merge[plot_col].min(), vmax=pc_merge[plot_col].max())
        cb1 = mpl.colorbar.ColorbarBase(ax2,
                                        cmap=themap,
                                        norm=norm
                                        )
        ### Sidebar name kwarg.
        if 'sidebar' in kwargs:
            sidebar = kwargs['sidebar']
            if pc_merge[plot_col].min() == pc_merge[plot_col].max():
                cb1.set_label(sidebar + '\nOnly one value plotted: ' + str(pc_merge[plot_col].max()), fontsize=20,
                              labelpad=20)
            else:
                cb1.set_label(sidebar, fontsize=20, labelpad=20)
        else:
            cb1.set_label('', fontsize=20, labelpad=20)

    ### Copyright tag
    if 'copyright' in kwargs:
        side = kwargs['copyright']
        Copyright('GitHub', ax1, side=side)

    return ax1


def US_map(states, values, location=['all'], **kwargs):
    """
    Give the function a dataframe that contains the state
    codes US states, such as 'FL', 'CA' and the values.
    The states is the column containing the statecodes.
    The column with values will automatically be plotted.

    Parameters
    ----
    kwargs:

    location: give a list of states and the plot will
    automatically be cut to this area. The states have
    to be in US shorthand notation, eg. NC = North
    Carolina.

    title: (string) give a title for the plot, if location
    is on, it will automatically be added to the title.

    sidebar: give the title of the colorbar on the side.

    linewidth: the linewidth of the polygon edges.

    color: the color of the polygon faces.

    edgecolor: the color of the polygon edges.

    size: (int) the figsize of the plot. Aspect ratio is
    automatically adjusted.

    copyright: flag set to 'l' or 'r' to indicate if the plot
    is to be published on the left or right side of the plot.
    This adds a 'Github' source on the plot. If the flag is
    absent, there will be no copyright stamp.
    """
    ### Grab the data.
    df = pd.DataFrame()
    df['states'] = states
    df['vals'] = values
    merge_col = 'states'
    plot_col = 'vals'

    ### Rename the input to avoid inconsistencies.
    ### Before this point we used the external names, from this point on they are as defined below.
    df.rename(columns={merge_col: 'states', plot_col: 'values'}, inplace=True)
    merge_col = 'states'
    plot_col = 'values'

    ### Poly data.
    PolyData = pd.read_csv(US_polygons)

    state_merge = pd.merge(PolyData, df, how='outer', left_on='StateName', right_on=merge_col)

    ### Location slicing.
    if location[0].lower() != 'all':
        location = [loc.upper() for loc in location]
        print 'INFO: Applying selection on location.'
        if location[0].upper() in state_merge.StateCode.unique():
            state_merge = state_merge[state_merge['StateCode'].isin(location)]
        else:
            print 'Warning: Invalid location used. Location is ignored.'

    ### Range for the plot.
    minx = state_merge['X'].min()
    maxx = state_merge['X'].max()
    miny = state_merge['Y'].min()
    maxy = state_merge['Y'].max()

    ### Figure size and axes.
    ### Because of the smaller sized axes we get a non-unity aspect ratio. This has to be adjusted to get the proper
    # aspect ratio on the maps.
    ### This is done by multiplying with 1.25.
    if 'ax' not in kwargs:
        if 'size' in kwargs:
            size = kwargs['size']
            fig = plt.figure(figsize=(1.25 * size, size * (maxy - miny) / (maxx - minx)))
        else:
            fig = plt.figure(figsize=(1.25 * 12, 12 * (maxy - miny) / (maxx - minx)))
        ax1 = fig.add_axes([0.05, 0., 0.8, 1.0])
    else:
        ax1 = kwargs['ax']

    ### Plot the polygons.
    plotReturn = Plotter(state_merge, 'StateCode', plot_col, **kwargs)

    ### Plot range options.
    plt.axis('off')
    plt.xlim(minx, maxx)
    plt.ylim(miny, maxy)

    ### Title kwarg.
    if 'title' in kwargs:
        title = kwargs['title']
        plt.title(title, fontsize=20)

    ### Defining the colorscheme.
    if 'color' in kwargs:
        themap = getattr(cm, kwargs['color'])
    else:
        themap = getattr(cm, 'Blues')

    ### Sidebar with normalized colors. Sidebar is only used in number plots.
    if plotReturn == 'Number':
        ax2 = fig.add_axes([0.9, 0., 0.05, 1.0])
        ax2.tick_params(labelsize=20)
        ### We need the plotReturn because there is no sidebar in color mode.
        norm = mpl.colors.Normalize(vmin=state_merge[plot_col].min(), vmax=state_merge[plot_col].max())
        cb1 = mpl.colorbar.ColorbarBase(ax2,
                                        cmap=themap,
                                        norm=norm
                                        )
        ### Sidebar name kwarg. We need the plotReturn because there is no sidebar in color mode.
        if 'sidebar' in kwargs:
            sidebar = kwargs['sidebar']
            if state_merge[plot_col].min() == state_merge[plot_col].max():
                cb1.set_label(sidebar + '\nOnly one value plotted: ' + str(state_merge[plot_col].max()), fontsize=20,
                              labelpad=20)
            else:
                cb1.set_label(sidebar, fontsize=20, labelpad=20)
        else:
            cb1.set_label('', fontsize=20, labelpad=20)

    ### Copyright tag
    if 'copyright' in kwargs:
        side = kwargs['copyright']
        Copyright('GitHub', ax1, side=side)

    return ax1