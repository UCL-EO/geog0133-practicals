import ephem
import itertools
import numpy as np

import scipy.constants
from datetime import datetime
from datetime import timedelta


def solar_model(secs, mins, hours, days, months, years, lats, longs, 
                julian_offset='2000/1/1'):
    """A function that calculates the solar zenith angle (sza, in
    degrees), the Earth-Sun distance (in AU), and the instantaneous 
    downwelling solar radiation in mol(photons) per square meter per
    second for a set of time(s) and geographical locations. """
    solar_constant = 1361. #W/m2
    # energy content of PAR quanta
    energy_par = 220.e-3 # MJmol-1
    # Define the observer
    observer = ephem.Observer()
    # Additionally, add a julian date offset
    if julian_offset != 0:
        julian_offset = ephem.julian_date(julian_offset)
    # Ensure we can easily iterate over all inputs
    # Even if they're scalars
    secs = np.atleast_1d(secs)
    mins = np.atleast_1d(mins)
    hours = np.atleast_1d(hours)
    months = np.atleast_1d(months)
    days = np.atleast_1d(days)
    years = np.atleast_1d(years)
    lats = np.atleast_1d(lats)
    longs = np.atleast_1d(longs)

    # What we return
    julian_day = []
    sza = []
    earth_sun_distance = []
    
    for second, minute, hour, day, month, year, lati, longi in \
        itertools.product(
            secs,mins,hours,days,months,years,lats,longs):
        hour = int(hour)
        minute = int(minute)
        second = int(second)
        observer.date = \
            f'{year:04d}/{month:d}/{day:d} {hour:d}:{minute:d}:{second:d}'
        
        observer.lon = f'{longi:f}'
        observer.lat = f'{lati:f}'
        solar_position = ephem.Sun(observer)
        solar_altitude = max([0, solar_position.alt * 180./np.pi])
        this_sza = 90. - solar_altitude
        this_distance_earth_sun = solar_position.earth_distance
        jd = ephem.julian_date(f'{year:04d}/{month:d}/{day:d}') - julian_offset
        jd += hour/24. + minute/60./24. + second/(3600*24) + 1
        julian_day.append(jd)
        sza.append(this_sza)
        earth_sun_distance.append(this_distance_earth_sun)
    
    julian_day = np.array(julian_day)
    sza = np.array(sza)
    earth_sun_distance = np.array(earth_sun_distance)
    iloc = np.argsort(julian_day)
    julian_day = julian_day[iloc]
    sza = sza[iloc]
    earth_sun_distance = earth_sun_distance[iloc]
    solar_radiation = solar_constant/(earth_sun_distance**2)
    # Express radiation in mol(photons) / (m^2 s)
    solar_radiation = solar_radiation/energy_par
    return julian_day, sza, earth_sun_distance, solar_radiation


