import matplotlib.pyplot as plt
import numpy as np
from argparse import ArgumentParser
from base import basemap, remove_empty, Sector, plot_neighbour, plot_current


def get_sectors():
    sectors = {}

    with open('sectors.txt') as f:
        lines = f.readlines()
        for line in lines:
            if line != '\n':
                splits = line.split(' ')
                coords = splits[-4:]
                rest = splits[:-4]
                sector = ' '.join(rest).split('Â·')
                if sector[1] not in sectors.keys():
                    sectors[sector[-3]] = Sector(sector[1], sector[2], sector[3][:3])
                    sectors[sector[-3]].add_coordinate(coords[1], coords[0])
                else:
                    sectors[sector[-3]].add_coordinate(coords[1], coords[0])
    return sectors


def main(sis, annotate, scale, levels, group, neighbours):
    sis = sis.split(',')
    neighbours = neighbours.split(',')
    fig, ax = plt.subplots()

    # Initialise Basemap for coordinate transformation
    m = basemap()

    if levels is None:
        min_level, max_level = 600, 0
    else:
        min_level, max_level = levels

    # Import sectors from GNG file
    sectors = get_sectors()
    if not group:
        if all(si not in sectors.keys() for si in sis):
            print('No sector found')
            return None

    # Plot main sector and calculate upper/lower levels
    for key, val in sectors.items():
        for si in sis:
            if group:
                if si in key:
                    plot_current(val, ax, m, False)
                    if levels is None:
                        if val.lower_level < min_level:
                            min_level = val.lower_level
                        if val.upper_level > max_level:
                            max_level = val.upper_level
            else:
                if si == key:
                    plot_current(val, ax, m, False)
                    if levels is None:
                        if val.lower_level < min_level:
                            min_level = val.lower_level
                        if val.upper_level > max_level:
                            max_level = val.upper_level

    # Axis plot limits
    x_min, x_max = ax.get_xlim()
    x_shift = np.abs((x_max - x_min) / 2)
    y_min, y_max = ax.get_ylim()
    y_shift = np.abs((y_max - y_min) / 2)
    ax.set_xlim((x_min - scale * x_shift, x_max + scale * x_shift))
    ax.set_ylim((y_min - scale * y_shift, y_max + scale * y_shift))

    # Plot neighbouring sectors
    for key, val in sectors.items():
        for si in sis:
            if group:
                if si not in key and (
                        min_level < val.lower_level < max_level or min_level < val.upper_level < max_level):
                    plot_neighbour(val, ax, m, key in neighbours)
            else:
                if si != key and (min_level < val.lower_level < max_level or min_level < val.upper_level < max_level):
                    plot_neighbour(val, ax, m, key in neighbours)

    # Plot main sector again
    for key, val in sectors.items():
        for si in sis:
            if group:
                if si in key:
                    plot_current(val, ax, m, annotate)
            else:
                if si == key:
                    plot_current(val, ax, m, annotate)

    ax.set_aspect('equal', adjustable='box')
    plt.axis(False)
    file_name = '-'.join(sis) + '.svg'
    plt.savefig(file_name if file_name != '.svg' else 'all.svg')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('sectors', type=str, help='Sector IDs to be plotted as main, separated by ,'
                                                  "e.g. HEF,GED,KIR")
    parser.add_argument('-a', '--annotate', action='store_true', help='If set, plots SI, Lower, Upper, '
                                                                      'annotation')
    parser.add_argument('-s', '--scale', type=float, help='Float, how far beyond primary sector to plot,'
                                                          ' default 0', default=0)
    parser.add_argument('-l', '--levels', type=int, nargs=2, help='Tuple lower upper, levels for which to plot '
                                                                  ' secondary sectors. If no tuple is given, '
                                                                  'the minimum and maximum values of the primary'
                                                                  ' sector are used.', default=None)
    parser.add_argument('-g', '--group', action='store_true', help='Group flag, if set plots all sectors beginning with'
                                                                   ' Sector otherwise only plots sectors with'
                                                                   ' given IDs')
    parser.add_argument('-n', '--neighbours', type=str, help='Sector IDs of neighbouring sectors for which to'
                                                             ' add labels', default='')
    args = parser.parse_args()
    main(args.sectors, args.annotate, args.scale, args.levels, args.group, args.neighbours)
