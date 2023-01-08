from mpl_toolkits.basemap import Basemap
import numpy as np
from pandas import DataFrame
from matplotlib.colors import to_hex


header = ['FIX', 'NEXT SECTOR', 'DEP', 'ARR', 'C LEVEL', 'D LEVEL']

hatch = ['/', '\\', '|', '-', '+', 'x', 'o', 'O', '.', '*']


def remove_empty(s):
    return s != ''


def basemap():
    return Basemap(width=1, height=1, resolution='l', projection='stere', lat_ts=50, lat_0=50, lon_0=8)


def convert(x):
    deg = int(x[1:4])
    minute = int(x[5:7]) / 60
    sec = int(x[8:10]) / 3600
    thous = int(x[11:]) / 3600 / 1000
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

    def copx_table(self, fixes, m, ax):
        plotted = []
        to_list = []
        fix_list = []
        dep_list = []
        arr_list = []
        climb_level_list = []
        descend_level_list = []

        self.copx.sort(key=lambda x: x.fix)
        for copx in self.copx:
            if copx.fix not in plotted:
                copx.annotate(fixes, ax, m)
                plotted.append(copx.fix)
            fix_list.append(copx.fix)
            to_list.append(copx.to_sector.name)
            dep_list.append(copx.dep)
            arr_list.append(copx.arr)
            climb_level_list.append(str(int(copx.c_level)/100)[:-2] if copx.c_level != '*' else '*')
            descend_level_list.append(str(int(copx.d_level)/100)[:-2] if copx.d_level != '*' else '*')

        df = DataFrame(dict(fix=fix_list, to=to_list, dep=dep_list, arr=arr_list, climb=climb_level_list,
                            descend=descend_level_list))
        # if not df.empty and ax is not None:
        #     ax.table(cellText=df.values, colLabels=header, loc='bottom')
        return df


class Airway:
    def __init__(self, name):
        self.name = name
        self.segments = []

    def add_segment(self, a, b):
        self.segments.append((a, b))

    def plot(self, ax, m):
        for segment in self.segments:
            a, b = segment
            x_1, y_1 = m(a.x, a.y)
            x_2, y_2 = m(b.x, b.y)
            # ax.text(x_1, y_1, a.name)
            # ax.text(x_2, y_2, b.name)
            ax.plot([x_1, x_2], [y_1, y_2], c='#FF0000', linewidth=0.4)


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
            ax.text(x, y, '{0}'.format(self.fix), horizontalalignment='center', verticalalignment='center',
                    fontsize=3, c='#23a819')

    def __str__(self):
        return '{0} -> {1}, {2}, {3}, {4}'.format(self.from_sector.name, self.to_sector.name, self.fix, self.dep,
                                                  self.arr)


class Waypoint:
    def __init__(self, name, x, y):
        self.name = name
        self.x = convert(x)
        self.y = convert(y)

    def annotate(self, ax, m):
        x, y = m(self.x, self.y)
        ax.text(x, y - 3500, '{0}'.format(self.name), horizontalalignment='center', verticalalignment='center',
                fontsize=4, c='#646464', fontfamily='Calibri', fontweight='bold')
        ax.scatter(x, y, marker='^', c='#646464', s=2.5)


def plot_current(sector, ax, m, annotate, coloured, i=0):
    if coloured:
        colors = ['#ffedd9', '#d9fcfe', '#fcdaff', '#fffcd9', '#d9d9ff', '#efffda', '#d8ffe2']
        border_colors = ['#ffc380', '#4df6ff', '#f266ff', '#fff266', '#6666ff', '#b2ff4d', '#66ff8c']
    else:
        colors = ['#f5f5f5']
        border_colors = ['#808080']
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
    ax.plot(x, y, linewidth=0.5, c=border_colors[i % len(colors)])
    ax.fill(x, y, alpha=1, c=colors[i % len(colors)])


def plot_neighbour(sector, ax, m, annotate, dotted=False):
    x = sector.x
    y = sector.y
    x.append(x[0])
    y.append(y[0])
    x, y = m(x, y)
    if dotted:
        ax.plot(x, y, c='#b8b8b8', linewidth=0.5, linestyle=(0, (5, 5)))
    else:
        ax.plot(x, y, c='#8f8f8f', linewidth=0.2, linestyle='solid')

    if annotate:
        ax.text((np.max(x) + np.min(x)) / 2, (np.max(y) + np.min(y)) / 2,
                '{0}\n{1}\n{2}'.format(sector.name, sector.upper_level,
                                       sector.lower_level if sector.lower_level != 0 else 'GND'),
                horizontalalignment='center', verticalalignment='center', fontsize='xx-small', alpha=0.5)


def get_fixes():
    fixes = {}
    with open('fixes.txt') as f:
        lines = f.readlines()
        for line in lines:
            split = line.split(' ')
            if ';' in split:
                fixes[split[0]] = Waypoint(split[0], split[-3], split[-4])
            else:
                fixes[split[0]] = Waypoint(split[0], split[-1], split[-2])
    return fixes


def get_airways():
    airways = {}

    with open('airways.txt') as f:
        lines = f.readlines()
        for line in lines:
            if line != '\n':
                splits = line.split(' ')
                sector_list = list(filter(remove_empty, splits))
                a = Waypoint(sector_list[6][3:], sector_list[2], sector_list[1])
                b = Waypoint(sector_list[8][3:], sector_list[4], sector_list[3])
                airway_name = sector_list[0]
                if airway_name in airways.keys():
                    airways[airway_name].add_segment(a, b)
                else:
                    airways[airway_name] = Airway(airway_name)
                    airways[airway_name].add_segment(a, b)
    return airways


def get_sectors():
    sectors = {}

    with open('sectors.txt') as f:
        lines = f.readlines()
        for line in lines:
            if line != '\n':
                splits = line.split(' ')
                coords = splits[-4:]
                rest = splits[:-4]
                sector = ' '.join(rest).split('@')
                if sector[1] not in sectors.keys():
                    sectors[sector[-3]] = Sector(sector[1], sector[2], sector[3][:3])
                    sectors[sector[-3]].add_coordinate(coords[1], coords[0])
                else:
                    sectors[sector[-3]].add_coordinate(coords[1], coords[0])
    return sectors


def get_sectors_with_copx():
    sectors = get_sectors()
    with open('copx.txt') as f:
        lines = f.readlines()
        for line in lines:
            split = line.split(':')
            from_split = split[6].split('Â·')
            to_split = split[7].split('Â·')
            from_sector = sectors[from_split[1]]
            to_sector = Sector(to_split[1], to_split[2], to_split[3])
            from_sector.add_copx(split[1], split[4], to_sector, split[8], split[9], split[10][:-1], split[3])
    return sectors
