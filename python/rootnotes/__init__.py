##############################################################################
#
# Copyright 2015 KPMG N.V. (unless otherwise stated)
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
Original file from Alexander Mazurov and Andrey Ustyuzhanin.
Manipulated by Fabian Jansen for KPMG.

More examples: http://mazurov.github.io/webfest2013/

@author jansen.fabian@kpmg.nl
@date 2014-07-01
"""

import ROOT
import tempfile
from IPython.core import display
from ROOT import TH1D, TH2D

HISTOCOUNTER = 0


def TH1D(nbinsx=40, xmin=0, xmax=1, title=None, name=None):
    """Helper method for creating 1D histograms"""
    if title is None:
        title = ''
    if name is not None:
        h = ROOT.gROOT.FindObject(name)
        if h and h is not None:
            return h
        else:
            return TH1D(name, title, nbinsx, xmin, xmax)
    else:
        global HISTOCOUNTER
        HISTOCOUNTER += 1
        name = 'h%d' % HISTOCOUNTER
        return ROOT.TH1D(name, title, nbinsx, xmin, xmax)


def TH2D(nbinsx=40, xmin=0, xmax=1, nbinsy=40, ymin=0, ymax=1, title=None, name=None):
    """Helper method for creating 2D histograms"""
    if title is None:
        title = ''
    if name is not None:
        h = ROOT.gROOT.FindObject(name)
        if h and h is not None:
            return h
        else:
            return TH2D(name, title, nbinsx, xmin, xmax, nbinsy, ymin, ymax)
    else:
        global HISTOCOUNTER
        HISTOCOUNTER += 1
        name = 'h%d' % HISTOCOUNTER
        return ROOT.TH2D(name, title, nbinsx, xmin, xmax, nbinsy, ymin, ymax)


def canvas(name="icanvas", size=(800, 600)):
    """Helper method for creating ROOT canvas"""
    # Check if icanvas already exists
    canvas = ROOT.gROOT.FindObject(name)
    assert len(size) == 2
    if canvas:
        canvas.Clear()
        return canvas
    else:
        return ROOT.TCanvas(name, name, size[0], size[1])


def display_canvas(canvas):
    """Helper method for drawing a ROOT canvas inline"""
    file = tempfile.NamedTemporaryFile(suffix=".png")
    canvas.SaveAs(file.name)
    display.display(display.Image(filename=file.name, format='png', embed=True))

def _display_any(obj):
    file = tempfile.NamedTemporaryFile(suffix=".png")
    obj.Draw()
    ROOT.gPad.SaveAs(file.name)
    ip_img = display.Image(filename=file.name, format='png', embed=True)
    return ip_img._repr_png_()

# register display function with PNG formatter:
png_formatter = get_ipython().display_formatter.formatters['image/png'] # noqa

# Register ROOT types in ipython
#
# In [1]: canvas = rootnotes.canvas()
# In [2]: canvas
# Out [2]: [image will be here]
png_formatter.for_type(ROOT.TCanvas, display_canvas)
png_formatter.for_type(ROOT.TF1, _display_any)

from IPython.core.magic import (Magics, magics_class, cell_magic)

@magics_class
class RootMagics(Magics):
    """Magics related to Root.
    %%rootprint  - Capture Root stdout output and show in result cell
    """

    def __init__(self, shell):
        super(RootMagics, self).__init__(shell)

    @cell_magic
    def rootprint(self, line, cell):
        """Capture Root stdout output and print in ipython notebook."""

        with tempfile.NamedTemporaryFile() as tmpFile:

            ROOT.gSystem.RedirectOutput(tmpFile.name, "w")
            # ns = {}
            # exec cell in self.shell.user_ns, ns
            exec cell in self.shell.user_ns
            ROOT.gROOT.ProcessLine("gSystem->RedirectOutput(0);")
            print tmpFile.read()

# Register
ip = get_ipython()
ip.register_magics(RootMagics)