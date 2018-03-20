#!/usr/bin/env python

from scipy.interpolate import *
from numpy import pi, sin
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons, AxesWidget
from pathlib import Path

# \/ Vertical slider \/

class VertSlider(AxesWidget):
    """
    A slider representing a floating point range.

    For the slider to remain responsive you must maintain a
    reference to it.

    The following attributes are defined
      *ax*        : the slider :class:`matplotlib.axes.Axes` instance

      *val*       : the current slider value

      *hline*     : a :class:`matplotlib.lines.Line2D` instance
                     representing the initial value of the slider

      *poly*      : A :class:`matplotlib.patches.Polygon` instance
                     which is the slider knob

      *valfmt*    : the format string for formatting the slider text

      *label*     : a :class:`matplotlib.text.Text` instance
                     for the slider label

      *closedmin* : whether the slider is closed on the minimum

      *closedmax* : whether the slider is closed on the maximum

      *slidermin* : another slider - if not *None*, this slider must be
                     greater than *slidermin*

      *slidermax* : another slider - if not *None*, this slider must be
                     less than *slidermax*

      *dragging*  : allow for mouse dragging on slider

    Call :meth:`on_changed` to connect to the slider event
    """
    def __init__(self, ax, label, valmin, valmax, valinit=0.5, valfmt='%1.2f',
                 closedmin=True, closedmax=True, slidermin=None,
                 slidermax=None, dragging=True, **kwargs):
        """
        Create a slider from *valmin* to *valmax* in axes *ax*.

        Additional kwargs are passed on to ``self.poly`` which is the
        :class:`matplotlib.patches.Rectangle` which draws the slider
        knob.  See the :class:`matplotlib.patches.Rectangle` documentation
        valid property names (e.g., *facecolor*, *edgecolor*, *alpha*, ...).

        Parameters
        ----------
        ax : Axes
            The Axes to put the slider in

        label : str
            Slider label

        valmin : float
            The minimum value of the slider

        valmax : float
            The maximum value of the slider

        valinit : float
            The slider initial position

        label : str
            The slider label

        valfmt : str
            Used to format the slider value, fprint format string

        closedmin : bool
            Indicate whether the slider interval is closed on the bottom

        closedmax : bool
            Indicate whether the slider interval is closed on the top

        slidermin : Slider or None
            Do not allow the current slider to have a value less than
            `slidermin`

        slidermax : Slider or None
            Do not allow the current slider to have a value greater than
            `slidermax`


        dragging : bool
            if the slider can be dragged by the mouse

        """
        AxesWidget.__init__(self, ax)

        self.valmin = valmin
        self.valmax = valmax
        self.val = valinit
        self.valinit = valinit
        self.poly = ax.axhspan(valmin, valinit, 0, 1, **kwargs)

        self.hline = ax.axhline(valinit, 0, 1, color='r', lw=1)

        self.valfmt = valfmt
        ax.set_xticks([])
        ax.set_ylim((valmin, valmax))
        ax.set_yticks([])
        ax.set_navigate(False)

        self.connect_event('button_press_event', self._update)
        self.connect_event('button_release_event', self._update)
        if dragging:
            self.connect_event('motion_notify_event', self._update)
        self.label = ax.text(0.5, 1.03, label, transform=ax.transAxes,
                             verticalalignment='center',
                             horizontalalignment='center')

        self.valtext = ax.text(0.5, -0.03, valfmt % valinit,
                               transform=ax.transAxes,
                               verticalalignment='center',
                               horizontalalignment='center')

        self.cnt = 0
        self.observers = {}

        self.closedmin = closedmin
        self.closedmax = closedmax
        self.slidermin = slidermin
        self.slidermax = slidermax
        self.drag_active = False

    def _update(self, event):
        """update the slider position"""
        if self.ignore(event):
            return

        if event.button != 1:
            return

        if event.name == 'button_press_event' and event.inaxes == self.ax:
            self.drag_active = True
            event.canvas.grab_mouse(self.ax)

        if not self.drag_active:
            return

        elif ((event.name == 'button_release_event') or
              (event.name == 'button_press_event' and
               event.inaxes != self.ax)):
            self.drag_active = False
            event.canvas.release_mouse(self.ax)
            return

        val = event.ydata
        if val <= self.valmin:
            if not self.closedmin:
                return
            val = self.valmin
        elif val >= self.valmax:
            if not self.closedmax:
                return
            val = self.valmax

        if self.slidermin is not None and val <= self.slidermin.val:
            if not self.closedmin:
                return
            val = self.slidermin.val

        if self.slidermax is not None and val >= self.slidermax.val:
            if not self.closedmax:
                return
            val = self.slidermax.val

        self.set_val(val)

    def set_val(self, val):
        xy = self.poly.xy
        xy[1] = 0, val
        xy[2] = 1, val
        self.poly.xy = xy
        self.valtext.set_text(self.valfmt % val)
        if self.drawon:
            self.ax.figure.canvas.draw_idle()
        self.val = val
        if not self.eventson:
            return
        for cid, func in self.observers.items():
            func(val)

    def on_changed(self, func):
        """
        When the slider value is changed, call *func* with the new
        slider position

        A connection id is returned which can be used to disconnect
        """
        cid = self.cnt
        self.observers[cid] = func
        self.cnt += 1
        return cid

    def disconnect(self, cid):
        """remove the observer with connection id *cid*"""
        try:
            del self.observers[cid]
        except KeyError:
            pass

    def reset(self):
        """reset the slider to the initial value if needed"""
        if (self.val != self.valinit):
            self.set_val(self.valinit)
            
# /\ Vertical slider /\

# g_ : global objects.
# gc_: 'const' global objects; never supposed to
# appear left of '=' after initialization.

# * * Snippets * *

g_table_name    = "table"
g_table_size    = 100

gc_table_src = (
    "uint16_t {}[{}] ="
    "{"
    "table here"
    "}"
)

# * * Global state * *

gc_fig = plt.figure(figsize=(12,12))
gc_ax  = gc_fig.add_subplot(111)

gc_sl_n = 5
gc_sl = [(None, None)] * gc_sl_n # (i, slider); is (i)t necessary? Let it be...
g_sl_valinit = 0.0               # Floating 0.0 is essential.

g_curve_x = np.linspace(0, gc_sl_n, gc_sl_n)
g_curve_y = np.array([g_sl_valinit]*gc_sl_n)
gc_i_x    = np.linspace(0, gc_sl_n, g_table_size)      # Interpolate to these points.

g_bottom_y, g_top_y = -1.0, 1.0

# * * Helpers * *

def plot_curve():
    f_spline = interp1d(g_curve_x, g_curve_y, kind='cubic')
    y_is     = f_spline(gc_i_x)
    gc_ax.clear()
    gc_ax.plot(g_curve_x, g_curve_y, 'o')
    gc_ax.plot(gc_i_x, y_is, '--')
    gc_ax.set_xlim([0, gc_sl_n])
    gc_ax.set_ylim([g_bottom_y, g_top_y])

# * * Event handlers * *

def sliders_on_changed(value):
    for slider in gc_sl:
        i, s = slider
        g_curve_y[i] = s.val
    plot_curve()

def reset_button_on_clicked(mouse_event):
    for slider in gc_sl:
        i, s = slider
        s.reset()

def export_button_on_clicked(mouse_event):
    np.save(g_table_name, g_curve_y)
    
def import_button_on_clicked(mouse_event):
    f = Path(g_table_name + ".npy")
    if f.is_file():
        g_curve_y = np.load(f)
        for slider in gc_sl:
            i, s = slider
            s.set_val(g_curve_y[i])
        plot_curve()

def color_radios_on_clicked(label):
    # ~ line.set_color(label)
    gc_fig.canvas.draw_idle()

def main():
    sl_step, sl_x, sl_y, sl_w, sl_h = (0.155, 0.25, 0.03, 0.03, 0.4)
    axis_color, hover_color = 'lightgoldenrodyellow', '0.975'

    # * * Create widgets * *

    # Adjust the subplots region to leave some space for the sliders and buttons
    gc_fig.subplots_adjust(left=0.25, bottom=0.50)
    
    for i, slider in enumerate(gc_sl):
        sl_ax    = gc_fig.add_axes([sl_x + i*sl_step, sl_y, sl_w, sl_h], facecolor=axis_color)
        gc_sl[i] = i, VertSlider(sl_ax, f"S{i}:", g_bottom_y, g_top_y, valinit=g_sl_valinit)
        
    # Draw the initial plot
    plot_curve()

    for slider in gc_sl:
        i, s = slider
        s.on_changed(sliders_on_changed)


    br = Button(gc_fig.add_axes([0.025, 0.5, 0.15, 0.04]),
                'Reset', color=axis_color, hovercolor=hover_color)
    br.on_clicked(reset_button_on_clicked)

    be = Button(gc_fig.add_axes([0.025, 0.84, 0.15, 0.04]),
                'Export', color=axis_color, hovercolor=hover_color)
    be.on_clicked(export_button_on_clicked)

    bi = Button(gc_fig.add_axes([0.025, 0.78, 0.15, 0.04]),
                'Import', color=axis_color, hovercolor=hover_color)
    bi.on_clicked(import_button_on_clicked)

    rbc = RadioButtons(gc_fig.add_axes([0.025, 0.6, 0.15, 0.15], facecolor=axis_color),
                      ('red', 'blue', 'green'), active=0)
    rbc.on_clicked(color_radios_on_clicked)

    # * * Run the show * *
    plt.show()

if __name__ == '__main__':
    main()
