from matplotlib import pyplot as plt

from skyfield.api import Star, load, wgs84, N, S, W, E
from skyfield.data import hipparcos, mpc, stellarium
import dsos
from starmap_utils import get_target, get_limit, add_telrad_circles, add_constellations
from skyfield.projections import build_stereographic_projection
from datetime import datetime
from pytz import timezone

# time `t` we use for everything else.

AMS = timezone('Europe/Amsterdam')
ts = load.timescale()
t = ts.from_datetime(AMS.localize(datetime(2022, 1, 19, 22, 0, 0)))
# 180 = South 0 = North
degrees = 0.0


amsterdam = wgs84.latlon(52.377956*N, 4.897070*E, elevation_m=28).at(t)
position = amsterdam.from_altaz(alt_degrees=90, az_degrees=degrees)

# An ephemeris from the JPL provides Sun and Earth positions.

eph = load('de421.bsp')
sun = eph['sun']
earth = eph['earth']

# The Hipparcos mission provides our star catalog.

with load.open(hipparcos.URL) as f:
    stardata = hipparcos.load_dataframe(f)

# DSO's from stellarium

with open('data/catalog.txt') as f:
    dsodata = dsos.load_dataframe(f)

# And the constellation outlines come from Stellarium.  We make a list
# of the stars at which each edge stars, and the star at which each edge
# ends.

url = ('https://raw.githubusercontent.com/Stellarium/stellarium/master'
       '/skycultures/modern_st/constellationship.fab')

with load.open(url) as f:
    consdata = stellarium.parse_constellations(f)

url2 = ('https://raw.githubusercontent.com/Stellarium/stellarium/master'
       '/skycultures/modern_st/star_names.fab')

with load.open(url2) as f2:
    star_names = stellarium.parse_star_names(f2)


# Center on Orion nebula as an example
# select the DSO you want centered in the view
# target = (dsodata.label == "M42")
# hip, target_dso = get_target(dsodata, target)

field_of_view_degrees = 18.0
limiting_magnitude = 4.0
dso_limit_magnitude = 6.0

for i, d in dsodata.iterrows():
    hip = i
    target_dso = d
    dso = Star.from_dataframe(d)

    center = earth.at(t).observe(dso)
    projection = build_stereographic_projection(center)

    # Now that we have constructed our projection, compute the x and y
    # coordinates that each star will have on the plot.

    star_positions = earth.at(t).observe(Star.from_dataframe(stardata))
    stardata['x'], stardata['y'] = projection(star_positions)

    # Create a True/False mask marking the stars bright enough to be
    # included in our plot.  And go ahead and compute how large their
    # markers will be on the plot.

    bright_stars = (stardata.magnitude <= limiting_magnitude)
    magnitude = stardata['magnitude'][bright_stars]
    marker_size = (0.6 + limiting_magnitude - magnitude) ** 2.0

    # Time to build the figure!

    fig, ax = plt.subplots(figsize=[2.0976, 2.0976], dpi=281.94)

    # Draw telrad circles

    add_telrad_circles(ax, 'black', 'white')

    # Draw the constellation lines.

    add_constellations(ax, consdata, stardata, 'black')

    # Draw the stars.

    ax.scatter(stardata['x'][bright_stars], stardata['y'][bright_stars],
               s=marker_size, color='black')

    # Finally, title the plot and set some final parameters.

    limit = get_limit(field_of_view_degrees)

    ax.text(0, -0.05, target_dso['label'], color='black',
            ha='center', va='top', fontsize=8, weight='bold', zorder=1).set_alpha(0.5)

    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    ax.set_aspect(1.0)

    # Save.
    plt.style.context('dark_background')
    plt.axis('off')
    fig.savefig(f"images/{target_dso['label']}.png", bbox_inches='tight', pad_inches=0, facecolor='white')
    plt.close(fig)
