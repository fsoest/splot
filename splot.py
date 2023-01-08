import matplotlib.pyplot as plt
import numpy as np
from argparse import ArgumentParser
from base import basemap, plot_neighbour, plot_current, get_sectors_with_copx, get_airways, get_fixes, header, get_sectors
from pandas import concat


def main(sis, annotate, scale, levels, group, neighbours, airways, copx_bool, waypoints, coloured, dotted):
    sis = sis.split(',')
    neighbours = neighbours.split(',')
    dotted = dotted.split(',')
    if copx_bool:
        fig, ax = plt.subplots(nrows=1, ncols=2)
        ax, ax1 = ax
    else:
        fig, ax = plt.subplots(nrows=1, ncols=1)

    # Initialise Basemap for coordinate transformation
    m = basemap()

    if levels is None:
        min_level, max_level = 600, 0
    else:
        min_level, max_level = levels

    # Import sectors from GNG file
    sectors = get_sectors() # get_sectors_with_copx()
    sel_sectors = []
    fixes = get_fixes()
    if not group:
        if all(si not in sectors.keys() for si in sis):
            print('No sector found')
            return None

    copx_list = []

    # Plot main sector and calculate upper/lower levels
    for key, val in sectors.items():
        for i, si in enumerate(sis):
            if group:
                if si in key:
                    plot_current(val, ax, m, False, coloured, i)
                    sel_sectors.append(val.name)
                    copx_list.append(val.copx_table(fixes, m, ax))
                    # if levels is None:
                    #     if val.lower_level < min_level:
                    #         min_level = val.lower_level
                    #     if val.upper_level > max_level:
                    #         max_level = val.upper_level
            else:
                if si == key:
                    plot_current(val, ax, m, False, coloured, i)
                    copx_list.append(val.copx_table(fixes, m, ax))
                    # if levels is None:
                    #     if val.lower_level < min_level:
                    #         min_level = val.lower_level
                    #     if val.upper_level > max_level:
                    #         max_level = val.upper_level

    # Axis plot limits
    x_min, x_max = ax.get_xlim()
    x_shift = np.abs((x_max - x_min) / 2)
    y_min, y_max = ax.get_ylim()
    y_shift = np.abs((y_max - y_min) / 2)
    ax.set_xlim((x_min - scale * x_shift, x_max + scale * x_shift))
    ax.set_ylim((y_min - scale * y_shift, y_max + scale * y_shift))

    # Plot neighbouring sectors
    if levels is not None:
        for key, val in sectors.items():
            for si in sis:
                if group:
                    if (si not in key) and ((
                            min_level < val.lower_level < max_level or min_level < val.upper_level < max_level)
                                            or (key in neighbours) or (key in dotted)):
                        plot_neighbour(val, ax, m, key in neighbours, key in dotted)
                else:
                    if si != key and ((min_level < val.lower_level < max_level or min_level < val.upper_level < max_level)
                            or (key in neighbours)):
                        plot_neighbour(val, ax, m, key in neighbours, key in dotted)
    for key, val in sectors.items():
        for neighbour in neighbours:
            if neighbour in key:
                plot_neighbour(val, ax, m, True)
        for dot in dotted:
            if dot in key:
                plot_neighbour(val, ax, m, True, True)

    # Plot main sector again
    for key, val in sectors.items():
        for i, si in enumerate(sis):
            if group:
                if si in key:
                    plot_current(val, ax, m, annotate, coloured, i)
            else:
                if si == key:
                    plot_current(val, ax, m, annotate, coloured, i)
    if airways is not None:
        airways = airways.split(',')
        airway_dict = get_airways()
        for airway in airways:
            airway_dict[airway].plot(ax, m)

    ax.set_aspect('equal', adjustable='box')
    ax.axis(False)

    if copx_list and copx_bool:
        ax1.axis(False)
        copx = concat(copx_list, ignore_index=True)
        for index, row in copx.iterrows():
            if row['to'] in sel_sectors:
                copx.drop(index, inplace=True)
        copx.sort_values('fix', inplace=True)
        table = ax1.table(cellText=copx.values, colLabels=header, loc='center')
        table.scale(1, 0.5)

    if waypoints is not None:
        waypoints = waypoints.split(',')
        for waypoint in waypoints:
            fixes[waypoint].annotate(ax, m)

    file_name = 'sectors/' + '-'.join(sis) + '.svg'
    plt.savefig(file_name if file_name != '.svg' else 'all.svg')
    plt.show()


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
    parser.add_argument('-w', '--airways', type=str, help='Airways to plot, separated by ,', default=None)
    parser.add_argument('-c', '--copx', action='store_true', help='Add Copx table to plot')
    parser.add_argument('-y', '--waypoints', type=str, help='Waypoints to plot, separated by ,', default=None)
    parser.add_argument('-f', '--coloured', action='store_true', help='If set, sectors have different colours')
    parser.add_argument('-d', '--dotted', type=str, help='Sector IDs of sectors to plot with dashed lines', default='')

    args = parser.parse_args()
    main(args.sectors, args.annotate, args.scale, args.levels, args.group, args.neighbours, args.airways, args.copx,
         args.waypoints, args.coloured, args.dotted)
