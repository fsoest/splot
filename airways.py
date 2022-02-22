import matplotlib.pyplot as plt
from splot import remove_empty, convert, basemap
from tqdm import tqdm


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


class Waypoint:
    def __init__(self, name, x, y):
        self.name = name
        self.x = convert(x)
        self.y = convert(y)


def make_airways():
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


if __name__ == '__main__':
    airways = make_airways()
    fig, ax = plt.subplots()

    airways['T178'].plot(ax)

    ax.set_aspect('equal', adjustable='box')
    plt.axis(False)
    plt.show()
