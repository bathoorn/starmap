import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection, PolyCollection

from skyfield.api import Star, load, wgs84, N, S, W, E
from skyfield.data import hipparcos, mpc, stellarium
import dsos
import constellation_bounds
import constellation_centers
from skyfield.projections import build_stereographic_projection
from datetime import datetime
from pytz import timezone

# time `t` we use for everything else.

AMS = timezone('Europe/Amsterdam')
ts = load.timescale()
t = ts.from_datetime(AMS.localize(datetime(2023, 11, 15, 22, 0, 0)))
# 180 = South 0 = North
degrees = 0.0


amsterdam = wgs84.latlon(52.377956*N, 4.897070*E, elevation_m=28).at(t)
position = amsterdam.from_altaz(alt_degrees=90, az_degrees=degrees)

# An ephemeris from the JPL provides Sun and Earth positions.

eph = load('de421.bsp')
sun = eph['sun']
earth = eph['earth']

# Center on Albireo middle of Summer Triangle

albireo = Star(ra_hours=(19, 30, 45.40),
               dec_degrees=(27, 57, 55.0))

# The Hipparcos mission provides our star catalog.

with load.open(hipparcos.URL) as f:
    stardata = hipparcos.load_dataframe(f)

# DSO's from stellarium

with open('data/catalog.txt') as f:
    dsodata = dsos.load_dataframe(f)

with open('data/lines_in_18.txt') as fc:
    constdata = constellation_bounds.load_dataframe(fc)

with open('data/centers_18.txt') as fc:
    centersdata = constellation_centers.load_dataframe(fc)

# And the constellation outlines come from Stellarium.  We make a list
# of the stars at which each edge stars, and the star at which each edge
# ends.

url = ('https://raw.githubusercontent.com/Stellarium/stellarium/master'
       '/skycultures/western_SnT/constellationship.fab')

with load.open(url) as f:
    consdata = stellarium.parse_constellations(f)

url2 = ('https://raw.githubusercontent.com/Stellarium/stellarium/master'
       '/skycultures/western_SnT/star_names.fab')

with load.open(url2) as f2:
    star_names = stellarium.parse_star_names(f2)
    starnames = {hip: name for hip, name in star_names}



def generate_constellation_lines(data, polygon=False):
    edges = [edge for name, edges in data for edge in edges]
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

def generate_constellation_borders(data):
    xy1 = pd.DataFrame(columns=['x', 'y'])
    xy2 = pd.DataFrame(columns=['x', 'y'])
    for segm, line in data:
        p1 = []
        p2 = []
        for i, point in enumerate(line.iterrows()):
            if i == 0:
                p1 = [point[1]['x'], point[1]['y']]
            else:
                p2 = [point[1]['x'], point[1]['y']]
                xy1.loc[len(xy2)] = p1
                xy2.loc[len(xy2)] = p2
                p1 = p2

    return np.rollaxis(np.array([xy1, xy2]), 1)

# We will center the chart on the comet's middle position.

center = earth.at(t).observe(albireo)
#projection = build_stereographic_projection(center)
projection = build_stereographic_projection(position)
field_of_view_degrees = 180.0
limiting_magnitude = 6.0
dso_limit_magnitude = 8.0

# Now that we have constructed our projection, compute the x and y
# coordinates that each star will have on the plot.

star_positions = earth.at(t).observe(Star.from_dataframe(stardata))
stardata['x'], stardata['y'] = projection(star_positions)

dso_positions = earth.at(t).observe(Star.from_dataframe(dsodata))
dsodata['x'], dsodata['y'] = projection(dso_positions)

cons_borders = earth.at(t).observe(Star.from_dataframe(constdata))
constdata['x'], constdata['y'] = projection(cons_borders)
constsegments = constdata.groupby('segment')

cons_centers = earth.at(t).observe(Star.from_dataframe(centersdata))
centersdata['x'], centersdata['y'] = projection(cons_centers)

# Create a True/False mask marking the stars bright enough to be
# included in our plot.  And go ahead and compute how large their
# markers will be on the plot.

bright_stars = (stardata.magnitude <= limiting_magnitude)
magnitude = stardata['magnitude'][bright_stars]
marker_size = (0.7 + limiting_magnitude - magnitude) ** 2.0

bright_dsos = (dsodata.magnitude <= dso_limit_magnitude)
dso_magnitude = dsodata['magnitude'][bright_dsos]
dso_size = (0.9 + dso_limit_magnitude - dso_magnitude) ** 2.0

# Time to build the figure!

fig, ax = plt.subplots(figsize=[24, 24])

# Draw Horizon as dashed line
# 24 points horizon

horizon = []
h0 = projection(amsterdam.from_altaz(alt_degrees=0, az_degrees=0.0))
for i in range(1, 73):
    delta = 5.0
    current = i * delta
    h1 = projection(amsterdam.from_altaz(alt_degrees=0, az_degrees=current))
    horizon.append([h0, h1])
    h0 = h1

ax.add_collection(LineCollection(horizon,
                         colors='#00f2', linewidths=1, linestyle='dashed', zorder=-1, alpha=0.5))

# Draw the constellation lines.

constellations = LineCollection(generate_constellation_lines(consdata),
                                colors='#00f2', linewidths=1, zorder=-1, alpha=0.5)
ax.add_collection(constellations)

# Draw constellation borders.
borders = LineCollection(generate_constellation_borders(constsegments),
                                colors='#00f2', linewidths=1, zorder=-1, alpha=0.5, linestyles='dashed')
ax.add_collection(borders)


# Draw the stars.

ax.scatter(stardata['x'][bright_stars], stardata['y'][bright_stars],
           s=marker_size, color='k')

ax.scatter(dsodata['x'][bright_dsos], dsodata['y'][bright_dsos],
           s=dso_size, color='red')

# Finally, title the plot and set some final parameters.

angle = np.pi - field_of_view_degrees / 360.0 * np.pi
limit = np.sin(angle) / (1.0 - np.cos(angle))


print(f"starnames = {starnames}")
for i, s in stardata[bright_stars].iterrows():
    if -limit < s['x'] < limit and -limit < s['y'] < limit:
        if i in starnames:
            print(f"star {starnames[i]} mag {s['magnitude']}")
            ax.text(s['x'] + 0.004, s['y'] - 0.004, starnames[i], color='k',
                    ha='left', va='top', fontsize=6, weight='bold', zorder=1).set_alpha(0.5)

for i, d in dsodata[bright_dsos].iterrows():
    if -limit < d['x'] < limit and -limit < d['y'] < limit:
        # print(f"dso {d['label']} mag {d['magnitude']}")
        ax.text(d['x'] + 0.004, d['y'] - 0.004, d['label'], color='red',
                ha='left', va='top', fontsize=9, weight='bold', zorder=1).set_alpha(0.5)

for i, c in centersdata.iterrows():
    if -limit < c['x'] < limit and -limit < c['y'] < limit:
        print(f"constallation {i} x {c['x']} y {c['y']}")
        ax.text(c['x'], c['y'], i, color='red',
                ha='left', va='top', fontsize=24, weight='bold', zorder=1).set_alpha(0.35)

ax.set_xlim(-limit, limit)
ax.set_ylim(-limit, limit)
ax.xaxis.set_visible(True)
ax.yaxis.set_visible(True)
ax.set_aspect(1.0)
ax.set_title(f"To the South in Amsterdam on {t.utc_strftime('%Y %B %d %H:%M')}")

# Save.

fig.savefig('summer-triangle.png', bbox_inches='tight')