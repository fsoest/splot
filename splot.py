import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.basemap import Basemap
from argparse import ArgumentParser


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

    def add_coordinate(self, x, y):
        self.x.append(convert(x))
        self.y.append(convert(y))


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


def plot_neighbour(sector, ax, m):
    x = sector.x
    y = sector.y
    x.append(x[0])
    y.append(y[0])
    x, y = m(x, y)
    ax.plot(x, y, c='#8f8f8f', linewidth=0.5)
    ax.fill(x, y, alpha=1, c='#ffffff')


def remove_empty(s):
    return s != ''


def make_sectors():
    sectors = {}

    with open('sectors.txt') as f:
        lines = f.readlines()
        for line in lines:
            if line != '\n':
                splits = line.split(' ')
                sector_list = list(filter(remove_empty, splits[:len(splits) - 4]))
                coords = splits[-4:]
                sector = ':'.join(sector_list).split('Â·')
                if sector[-3] not in sectors.keys():
                    sectors[sector[-3]] = Sector(sector[-3], sector[-2], sector[-1])
                    sectors[sector[-3]].add_coordinate(coords[1], coords[0])
                else:
                    sectors[sector[-3]].add_coordinate(coords[1], coords[0])
    return sectors


def main(sis, annotate, scale, levels):
    sis = sis.split(',')
    fig, ax = plt.subplots()

    # Initialise Basemap for coordinate transformation
    m = Basemap(width=1, height=1, resolution='l', projection='stere', lat_ts=50, lat_0=50, lon_0=8)

    if levels is None:
        min_level, max_level = 600, 0
    else:
        min_level, max_level = levels

    # Import sectors from GNG file
    sectors = make_sectors()
    for key, val in sectors.items():
        for si in sis:
            if si in key:
                plot_current(val, ax, m, False)
                if levels is None:
                    if val.lower_level < min_level:
                        min_level = val.lower_level
                    if val.upper_level > max_level:
                        max_level = val.upper_level

    x_min, x_max = ax.get_xlim()
    x_shift = np.abs((x_max - x_min) / 2)
    y_min, y_max = ax.get_ylim()
    y_shift = np.abs((y_max - y_min) / 2)

    ax.set_xlim((x_min - scale * x_shift, x_max + scale * x_shift))
    ax.set_ylim((y_min - scale * y_shift, y_max + scale * y_shift))

    for key, val in sectors.items():
        for si in sis:
            if si not in key and (min_level < val.lower_level < max_level or min_level < val.upper_level < max_level):
                plot_neighbour(val, ax, m)

    for key, val in sectors.items():
        for si in sis:
            if si in key:
                plot_current(val, ax, m, annotate)

    ax.set_aspect('equal', adjustable='box')
    plt.axis(False)
    file_name = '-'.join(sis) + '.svg'
    plt.savefig(file_name if file_name != '.svg' else 'all.svg')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('sectors', type=str, help='Sector IDs to be plotted as main, separated by ,'
                                                           "e.g. HEF,GED,KIR")
    parser.add_argument('-a', '--annotate', type=bool, help='Boolean, whether to plot SI, Lower, Upper, '
                                                                     'default False', default=False)
    parser.add_argument('-s', '--scale', type=float, help='Float, how far beyond primary sector to plot,'
                                                                   ' default 0', default=0)
    parser.add_argument('-l', '--levels', type=int, nargs=2, help='Tuple lower upper, levels for which to plot '
                                                                    ' secondary sectors. If no tuple is given, '
                                                                    'the minimum and maximum values of the primary'
                                                                    ' sector are used.', default=None)
    args = parser.parse_args()

    main(args.sectors, args.annotate, args.scale, args.levels)

