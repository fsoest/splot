from mpl_toolkits.basemap import Basemap
import numpy as np


def remove_empty(s):
    return s != ''


def basemap():
    return Basemap(width=1, height=1, resolution='l', projection='stere', lat_ts=50, lat_0=50, lon_0=8)


def convert(x):
    deg = int(x[1:4])
    minute = int(x[5:7]) / 60
    sec = int(x[8:10]) / 3600
    thous = int(x[11:]) / 3600 / 100
    return deg + minute + sec + thous


class Sector:
    def __init__(self, name, lower_level, upper_level):
        self.name = name
        self.lower_level = int(lower_level)
        self.upper_level = int(upper_level)
        self.x = []
        self.y = []
        self.copx = []

    def add_coordinate(self, x, y):
        self.x.append(convert(x))
        self.y.append(convert(y))

    def add_copx(self, dep, arr, to_sector, climb_level, descend_level, name, fix):
        self.copx.append(Copx(dep, arr, self, to_sector, climb_level, descend_level, name, fix))


class Airway:
    def __init__(self, name):
        self.name = name
        self.segments = []

    def add_segment(self, a, b):
        self.segments.append((a, b))

    def plot(self, ax):
        m = basemap()
        for segment in self.segments:
            a, b = segment
            x_1, y_1 = m(a.x, a.y)
            x_2, y_2 = m(b.x, b.y)
            ax.plot([x_1, x_2], [y_1, y_2], c='k')
            ax.text(x_1, y_1, a.name)
            ax.text(x_2, y_2, b.name)


class Copx:
    def __init__(self, dep, arr, from_sector: Sector, to_sector: Sector, climb_level: int, descend_level, name, fix):
        self.dep = dep
        self.arr = arr
        self.from_sector = from_sector
        self.to_sector = to_sector
        self.c_level = climb_level
        self.d_level = descend_level
        self.name = name
        self.fix = fix

    def annotate(self, fixes, ax, m):
        if self.fix != '*':
            waypoint = fixes[self.fix]
            x, y = m(waypoint.x, waypoint.y)
            ax.text(x, y, '{0}\n{1}\n{2}'.format(self.fix, self.d_level, self.to_sector.name),
                    horizontalalignment='center', verticalalignment='center', fontsize='xx-small')

    def __str__(self):
        return '{0} -> {1}, {2}'.format(self.from_sector.name, self.to_sector.name, self.fix)


class Waypoint:
    def __init__(self, name, x, y):
        self.name = name
        self.x = convert(x)
        self.y = convert(y)


def plot_current(sector, ax, m, annotate):
    x = sector.x
    y = sector.y
    x.append(x[0])
    y.append(y[0])
    x, y = m(x, y)
    if annotate:
        ax.text((np.max(x) + np.min(x)) / 2, (np.max(y) + np.min(y)) / 2,
                '{0}\n{1}\n{2}'.format(sector.name, sector.upper_level,
                                       sector.lower_level if sector.lower_level != 0 else 'GND'),
                horizontalalignment='center', verticalalignment='center', fontsize='xx-small')
    ax.plot(x, y, c='k', linewidth=0.5)
    ax.fill(x, y, alpha=1, c='#fef0e5')


def plot_neighbour(sector, ax, m, annotate):
    x = sector.x
    y = sector.y
    x.append(x[0])
    y.append(y[0])
    x, y = m(x, y)
    ax.plot(x, y, c='#8f8f8f', linewidth=0.5)
    if annotate:
        ax.text((np.max(x) + np.min(x)) / 2, (np.max(y) + np.min(y)) / 2,
                '{0}\n{1}\n{2}'.format(sector.name, sector.upper_level,
                                       sector.lower_level if sector.lower_level != 0 else 'GND'),
                horizontalalignment='center', verticalalignment='center', fontsize='xx-small')
    ax.fill(x, y, alpha=1, c='#ffffff')


def get_fixes():
    fixes = {}
    with open('fixes.txt') as f:
        lines = f.readlines()
        for line in lines:
            split = line.split(' ')
            fixes[split[0]] = Waypoint(split[0], split[-1], split[-2])
    return fixes
