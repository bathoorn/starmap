from matplotlib.collections import LineCollection, PatchCollection
from matplotlib.patches import Circle
import numpy as np


def generate_constellation_lines(consdata, stardata, polygon=False):
    edges = [edge for name, edges in consdata for edge in edges]
    edges_star1 = [star1 for star1, star2 in edges]
    edges_star2 = [star2 for star1, star2 in edges]
    xy1 = stardata[['x', 'y']].loc[edges_star1].values
    xy2 = stardata[['x', 'y']].loc[edges_star2].values

    if polygon:
        return [xy1]
    else:

        # The constellation lines will each begin at the x,y of one star and end
        # at the x,y of another.  We have to "rollaxis" the resulting coordinate
        # array into the shape that matplotlib expects.

        return np.rollaxis(np.array([xy1, xy2]), 1)


def generate_constellation_borders(consdata):
    edges = [edge for name, edges in consdata for edge in edges]
    lines = [((p1['x'],p1['y']), (p2['x'],p2['y'])) for p1, p2 in edges]
    return lines

def add_constellations(ax, consdata, stardata, colors):
    constellations = LineCollection(generate_constellation_lines(consdata, stardata),
                                    colors=colors, linewidths=0.25, zorder=-1, alpha=0.5)
    ax.add_collection(constellations)


def get_target(data, target):
    for i, d in data[target].iterrows():
        hip = i
        target_dso = d
    return hip, target_dso


def get_limit(field_of_view_degrees):
    angle = np.pi - field_of_view_degrees / 360.0 * np.pi
    return np.sin(angle) / (1.0 - np.cos(angle))


def telrad_radius(degrees):
    telrad_angle = np.pi - degrees / 360.0 * np.pi
    telrad_radius = np.sin(telrad_angle) / (1.0 - np.cos(telrad_angle))
    return telrad_radius


def add_telrad_circles(ax, fgcolor, bgcolor):
    telrad = []
    for deg in [16, 8, 4, 2, 0.2]:
        telrad.append(Circle((0, 0), telrad_radius(deg)))
    ax.add_collection(PatchCollection(telrad, edgecolors=fgcolor, linewidths=0.5,
                                      facecolors=bgcolor, zorder=-2))
