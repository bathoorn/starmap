import ligo.skymap.plot
from matplotlib import pyplot as plt
from skyfield.api import Star, load, wgs84, N, S, W, E
from skyfield.data import hipparcos, mpc, stellarium
import dsos
import constellation_bounds
import constellation_centers
from datetime import datetime
from pytz import timezone

from astropy.coordinates import SkyCoord, EarthLocation
from astropy import coordinates as coord
from astropy.time import Time
from astropy import units as u
import numpy as np


# time `t` we use for everything else.

AMS = timezone('Europe/Amsterdam')
ts = load.timescale()
t = ts.from_datetime(AMS.localize(datetime(1976, 10, 17, 5, 25, 0)))
# 180 = South 0 = North
degrees = 0.0


amsterdam = wgs84.latlon(52.377956*N, 4.897070*E, elevation_m=28).at(t)
position = amsterdam.from_altaz(alt_degrees=90, az_degrees=degrees)

# An ephemeris from the JPL provides Sun and Earth positions.

eph = load('de421.bsp')
sun = eph['sun']
earth = eph['earth']
planet_names = {
    'mercury': 199,
    'venus': 299,
    'mars': 499,
    'jupiter': 5,
    'saturn': 6,
    'uranus': 7,
    'neptune': 8,
    'pluto': 9,
    'moon': 301
}
planets = {name: eph[id] for name, id in planet_names.items()}

# The Hipparcos mission provides our star catalog.

with load.open(hipparcos.URL) as f:
    stardata = hipparcos.load_dataframe(f)

star_positions = earth.at(t).observe(Star.from_dataframe(stardata))

# Create a True/False mask marking the stars bright enough to be
# included in our plot.  And go ahead and compute how large their
# markers will be on the plot.

limiting_magnitude = 6.0
bright_stars = (stardata.magnitude <= limiting_magnitude)
magnitude = stardata['magnitude'][bright_stars]
marker_size = (0.7 + limiting_magnitude - magnitude) ** 2.0

ra = stardata['ra_hours'][bright_stars]
dec = stardata['dec_degrees'][bright_stars]

time = Time.now()
coos = SkyCoord(ra, dec, frame='icrs', unit=(u.hourangle, u.deg), obstime=time)

# Time to build the figure!

fig = plt.figure(figsize=[10, 10])
ax = plt.axes(projection='geo globe')
ax.grid()
ax.compass(1,1,0.1)

# Draw the stars.

ax.scatter(ra, dec,
           s=marker_size+5, color='black')

ax.scatter(stardata['ra_degrees'][bright_stars], stardata['dec_degrees'][bright_stars],
           s=marker_size, color='black', alpha=0.75)

plt.show()