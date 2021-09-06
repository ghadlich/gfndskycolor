#!/usr/bin/env python
# encoding: utf-8

# Copyright (c) 2021 Grant Hadlich
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE. 
import ephem
from datetime import datetime, timezone, timedelta

class CityObserver:
    def __init__(self, lat, long, elev, day):
        """
        This class takes a latitude, longitude, and elevation and returns a
        PyEphem Observer object.

        Parameters
        ----------
        lat : str
            The latitude of the location.
        long : str
            The longitude of the location.
        elev : int
            The elevation of the location.
        """
        self.city = ephem.Observer()
        self.city.pressure = 0
        self.city.horizon = '-0:34'
        self.city.lat, self.city.lon = lat, long
        self.city.date = day # '2021/09/03 17:00'
        self.city.elev = elev

    def set_horizon_normal(self):
        self.city.horizon = '-0:34'

    def set_horizon_civil_twilight(self):
        self.city.horizon = '-6'

    def get_city(self):
        return self.city



class SunData:
    def __init__(self, observer):
        sun = ephem.Sun()

        # Get Civil Twilight Start and end
        observer.set_horizon_civil_twilight()
        city = observer.get_city()
        sun.compute(city)

        # Get UTC Sunrise and Sunset
        self.twilight_start_time_utc = city.previous_rising(sun, use_center=True).datetime()
        self.twilight_end_time_utc   = city.next_setting(sun, use_center=True).datetime()

        # Get Set to Local Timezone
        self.twilight_start_time_str = self.twilight_start_time_utc.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime("%-I:%M:%S %p")
        self.twilight_end_time_str   = self.twilight_end_time_utc.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime("%-I:%M:%S %p")

        # Get Sunrise and Sunset
        observer.set_horizon_normal()
        city = observer.get_city()
        sun.compute(city)

        # Get UTC Sunrise and Sunset
        self.sunrise_time_utc = city.previous_rising(sun).datetime()
        self.sunset_time_utc = city.next_setting(sun).datetime()

        # Get Set to Local Timezone
        self.sunrise_time_str = self.sunrise_time_utc.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime("%-I:%M:%S %p")
        self.sunset_time_str = self.sunset_time_utc.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime("%-I:%M:%S %p")

        # Calculate Length
        self.day_length = (self.sunset_time_utc - self.sunrise_time_utc).total_seconds()

        # Calculate Time List
        # First Entry is Civil Twilight
        # Second Entry is Sunrise
        # n - 1 Entry is Sunset
        # n Entry is Civil Twilight
        time_list = [self.twilight_start_time_utc.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime("%H:%M"), 
                     self.sunrise_time_utc.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime("%H:%M")]

        # Ignore Times within 10 mins of sunrise and sunset
        sunrise_buffer = self.sunrise_time_utc+timedelta(minutes=10)
        sunset_buffer = self.sunset_time_utc-timedelta(minutes=10)

        # Time to be cycled through
        next_time = self.sunrise_time_utc

        while (next_time < self.sunset_time_utc):
            # Add an hour and get to top of the hour
            next_time = next_time.replace(minute=0, second=0, microsecond=0)+timedelta(hours=1)

            if (next_time > sunrise_buffer and 
                next_time < sunset_buffer):
                time_list.append(next_time.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime("%H:%M"))

        # Add in Sunset Time
        time_list.append(self.sunset_time_utc.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime("%H:%M"))

        # Add in Civil Twilight End
        time_list.append(self.twilight_end_time_utc.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime("%H:%M"))

        self.time_list = time_list

    def get_time_list(self):
        """
        Returns
        -------
        time_list : str -> List
            time_list[0]   = HH:MM of Civil Twilight Start
            time_list[1]   = HH:MM of Sunrise
            time_list[...] = HH:00
            time_list[n-1] = HH:MM of Sunrise
            time_list[n]   = HH:MM of Civil Twilight End
        """
        return self.time_list

    def get_sunrise_sunset(self):
        """
        Returns
        -------
        rising_time : str
            Sunrise time in the format "HH:MM:SS"
        setting_time : str
            Sunset time in the format "HH:MM:SS"
        day_length : int
            Length of day in seconds
        """
        return self.sunrise_time_str, self.sunset_time_str, self.day_length


if __name__ == "__main__":
    # Get current day, set at 17:00 UTC for middle of the day
    day = datetime.now().strftime("%Y/%m/%d 17:00")

    # Grand Forks, ND Lat, Long, Elev (Meters)
    observer = CityObserver('47.925259', '-97.032852', 257, day)

    sun_data = SunData(observer)

    rising_time, setting_time, day_length = sun_data.get_sunrise_sunset()
    print(rising_time)
    print(setting_time)
    print(day_length)
    print(sun_data.get_time_list())
