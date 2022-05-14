#!/usr/bin/env python3
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import numpy as np
from ut61eplus import UT61EPLUS

dmm = UT61EPLUS()
utname = dmm.getName()
fig = plt.figure()
ax  = fig.add_subplot(1, 1, 1)
xs  = [0]
ys  = [0]
i   = 1

def animate(i, xs, ys):
    mesure=dmm.takeMeasurement()
    if not mesure.overload :
        xs.append(i)
        ys.append(mesure.display_decimal)
    ax.clear()
    ax.plot(xs, ys, label=mesure.mode)
    xs = xs[-50:]
    ys = ys[-50:]
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title(utname)
    plt.ylabel(mesure.display_unit)
    plt.legend()
    plt.axis([0 if i < 50 else i-50, 50 if i < 50 else i, min(ys), max(ys)])
    i=i+1

ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys), interval=200)
plt.show()
