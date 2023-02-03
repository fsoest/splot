import matplotlib.pyplot as plt
import numpy as np
from argparse import ArgumentParser
from base import basemap, plot_neighbour, plot_current, get_sectors_with_copx, get_airways, get_fixes, header, get_sectors
import os


def main(sis, annotate, scale, levels, group, neighbours, airways, waypoints, coloured, dotted):
    sis = sis.split(',')
    if neighbours is not None:
        neighbours = neighbours.split(',')
    if dotted is not None:
        dotted = dotted.split(',')
    fig, ax = plt.subplots(nrows=1, ncols=1)

    # Initialise Basemap for coordinate transformation
    m = basemap()

    if levels is not None:
        min_level, max_level = levels

    # Import sectors from GNG file
    sectors = get_sectors()
    sel_sectors = []
    if waypoints is not None:
        fixes = get_fixes()
    else:
        fixes = []
    if not group:
        if all(si not in sectors.keys() for si in sis):
            print('No sector found')
            return None

    def plot_main():
        for key, val in sectors.items():
            for i, si in enumerate(sis):
                if group:
                    if si in key:
                        plot_current(val, ax, m, annotate, coloured, i)
                else:
                    if si == key:
                        plot_current(val, ax, m, annotate, coloured, i)

    plot_main()

    # Axis plot limits
    x_min, x_max = ax.get_xlim()
    x_shift = np.abs((x_max - x_min) / 2)
    y_min, y_max = ax.get_ylim()
    y_shift = np.abs((y_max - y_min) / 2)
    ax.set_xlim((x_min - scale * x_shift, x_max + scale * x_shift))
    ax.set_ylim((y_min - scale * y_shift, y_max + scale * y_shift))
    ax.set_aspect('equal', adjustable='box')
    ax.axis(False)

    # Plot neighbouring sectors
    if levels is not None:
        for key, val in sectors.items():
            for si in sis:
                is_key_in_dotted = key in dotted if dotted is not None else False
                is_key_in_neighbours = key in neighbours if neighbours is not None else False
                if group:
                    if (si not in key) and ((
                            min_level < val.lower_level < max_level or min_level < val.upper_level < max_level)
                                            or is_key_in_neighbours or is_key_in_dotted):
                        plot_neighbour(val, ax, m, is_key_in_neighbours, is_key_in_dotted)
                else:
                    if si != key and ((min_level < val.lower_level < max_level or min_level < val.upper_level < max_level)
                            or is_key_in_neighbours):
                        plot_neighbour(val, ax, m, is_key_in_neighbours, is_key_in_dotted)
    else:
        if neighbours is not None:
            for key, val in sectors.items():
                for neighbour in neighbours:
                    if neighbour in key:
                        plot_neighbour(val, ax, m, key in neighbours)
        if dotted is not None:
            for dot in dotted:
                if dot in key:
                    plot_neighbour(val, ax, m, key in neighbours, True)

    #Plot main sector again
    plot_main()

    if airways is not None:
        airways = airways.split(',')
        airway_dict = get_airways()
        for airway in airways:
            airway_dict[airway].plot(ax, m)

    if waypoints is not None:
        waypoints = waypoints.split(',')
        for waypoint in waypoints:
            fixes[waypoint].annotate(ax, m)

    if not os.path.exists('output'):
        os.makedirs('output')
    file_name = 'output/' + '-'.join(sis) + '.svg'
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
                                                             ' add labels, either e.g. GIN1,GIN2 or GIN,TAU', default=None)
    parser.add_argument('-w', '--airways', type=str, help='Airways to plot, separated by ,', default=None)
    parser.add_argument('-y', '--waypoints', type=str, help='Waypoints to plot, separated by ,', default=None)
    parser.add_argument('-f', '--coloured', action='store_true', help='If set, sectors have different colours')
    parser.add_argument('-d', '--dotted', type=str, help='Sector IDs (GIN1,GIN2 or GIN,TAU) of sectors to plot with dashed lines', default=None)

    args = parser.parse_args()
    main(args.sectors, args.annotate, args.scale, args.levels, args.group, args.neighbours, args.airways,
         args.waypoints, args.coloured, args.dotted)
