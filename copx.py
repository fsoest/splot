from base import basemap, Sector, get_fixes, plot_current
from splot import get_sectors
from tqdm import tqdm
import matplotlib.pyplot as plt

def get_copx():
    sectors = get_sectors()
    with open('copx.txt') as f:
        lines = f.readlines()
        for line in tqdm(lines):
            split = line.split(':')
            from_split = split[6].split('Â·')
            to_split = split[7].split('Â·')
            from_sector = sectors[from_split[1]]
            to_sector = Sector(to_split[1], to_split[2], to_split[3])
            from_sector.add_copx(split[1], split[4], to_sector, split[8], split[9], split[10][:-1], split[3])

    return sectors


if __name__ == '__main__':
    sector = 'KIR3'
    fig, ax = plt.subplots()
    m = basemap()
    fixes = get_fixes()
    sectors = get_copx()
    plot_current(sectors[sector], ax, m, True)
    for co in sectors[sector].copx:
        co.annotate(fixes, ax, m)

    ax.set_aspect('equal', adjustable='box')

    plt.axis(False)
    plt.show()
