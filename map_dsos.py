from skyfield.api import Star, load, wgs84, N, S, W, E, position_of_radec, load_constellation_map, load_constellation_names
import dsos
import constellation_bounds
import constellation_centers
from datetime import datetime
from pytz import timezone
import json
from skyfield.functions import load_bundled_npy
a = load_bundled_npy('constellations.npz')
print(a['sorted_ra'])
print(a['sorted_dec'])
print(a['radec_to_index'])
print(a['indexed_abbreviations'])

# time `t` we use for everything else.

AMS = timezone('Europe/Amsterdam')
ts = load.timescale()
t = ts.from_datetime(AMS.localize(datetime(2022, 1, 19, 22, 0, 0)))
# 180 = South 0 = North
degrees = 0.0


amsterdam = wgs84.latlon(52.377956*N, 4.897070*E, elevation_m=28).at(t)
position = amsterdam.from_altaz(alt_degrees=90, az_degrees=degrees)

# An ephemeris from the JPL provides Sun and Earth positions.

# DSO's from stellarium

with open('data/catalog.txt') as f:
    dsodata = dsos.load_dataframe(f)

with open('data/lines_in_18.txt') as fc:
    constdata = constellation_bounds.load_dataframe(fc)

with open('data/centers_18.txt') as fc:
    centersdata = constellation_centers.load_dataframe(fc)


class Constellation:
    def __init__(self):
        self.find_constellation = load_constellation_map()
        self.names = dict(load_constellation_names())
        print(f"constellations = {self.names}")

    def __call__(self, ra, dec):
        p = position_of_radec(ra, dec)
        abrv = self.find_constellation(p)
        name = self.names.get(abrv)
        return f"{name} ({abrv})"


in_constellation = Constellation()
def transform(data):
    return {
        "Name": data["label"],
        "Constellation": in_constellation(data["ra_hours"], data["dec_degrees"]),
        "Magnitude": data["magnitude"],
        "Right Ascention": data["ra_degrees"],
        "Declination": data["dec_degrees"],
    }

with open('messier_data.json', 'w') as output:
    for i, d in dsodata.iterrows():
        output.write(json.dumps(transform(dict(d)))+"\n")


# edge18.txt format
# Bytes 	Format 	Unit 	Explanation
# 1- 3 	A3 		Key of 1st vertex
# 5- 7 	A3 		Key of 2nd vertex
# 9 	A1 		Edge type: [M]eridian or [P]arallel
# 10 	A1 		Edge direction: + increasing or - decreasing
# 12-13 	I2 	hrs 	Right ascension B1875 (hours) of 1st vertex
# 15-16 	I2 	min 	Right ascension B1875 (minutes) of 1st vertex
# 18-19 	I2 	sec 	Right ascension B1875 (seconds) of 1st vertex
# 21 	A1 		Declination B1875 (sign) of 1st vertex
# 22-23 	I2 	deg 	Declination B1875 (degrees) of 1st vertex
# 25-26 	I2 	arcmin 	Declination B1875 (minutes) of 1st vertex
# 28-29 	I2 	arcsec 	Declination B1875 (seconds) of 1st vertex
# 31-32 	I2 	hrs 	Right ascension B1875 (hours) of 2nd vertex
# 34-35 	I2 	min 	Right ascension B1875 (minutes) of 2nd vertex
# 37-38 	I2 	sec 	Right ascension B1875 (seconds) of 2nd vertex
# 40 	A1 		Declination B1875 (sign) of 2nd vertex
# 41-42 	I2 	deg 	Declination B1875 (degrees) of 2nd vertex
# 44-45 	I2 	arcmin 	Declination B1875 (minutes) of 2nd vertex
# 47-48 	I2 	arcsec 	Declination B1875 (seconds) of 2nd vertex
# 50-57 	A8 		Constellation abbreviations