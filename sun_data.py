#!/usr/bin/env python
# encoding: utf-8

# Copyright (c) 2021-2023 Grant Hadlich
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
from typing import List, Tuple, Optional, Dict, Any
import ephem
import time
from datetime import datetime, timezone, timedelta
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

class CityObserver:
    """
    CityObserver class is a tool to get information about the sun's position and daylight in a particular city.

    Attributes
    ----------
    observer : ephem.Observer
        An ephem.Observer object with the location of the city
    time_list : list
        A list of the times of interest for the given location and date
    sunrise_time_str : str
        The time of the sunrise in the format "HH:MM:SS"
    sunset_time_str : str
        The time of the sunset in the format "HH:MM:SS"
    day_length : int
        The length of the day in seconds

    Methods
    -------
    get_time_list() -> List[str]
        Returns a list of times of interest for the current location and date
    get_sunrise_sunset() -> Tuple[str, str, int]
        Returns the time of the sunrise, sunset, and length of day for the current location and date
    create_daylight_plot(output_file: str, day: Optional[datetime] = None, custom_colors: Optional[Dict] = None) -> None
        Creates a plot of the sun's position over the course of a day, with optional custom colors for different times of day.
        The plot is saved to the specified output_file.
    """

    def __init__(self, lat: str, long: str, elev: int, day: str) -> None:
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
        day : str
            The date and time of the observation in the format of 'yyyy/mm/dd hh:mm'.
        """
        self.city = ephem.Observer()
        self.city.pressure = 0
        self.city.horizon = '-0:34'
        self.city.lat, self.city.lon = lat, long
        self.city.date = day # '2021/09/03 17:00'
        self.city.elev = elev

    def set_horizon_normal(self) -> None:
        """Sets horizon to normal level"""
        self.city.horizon = '-0:34'

    def set_horizon_civil_twilight(self) -> None:
        """Sets horizon to civil twilight level"""
        self.city.horizon = '-6'

    def get_city(self) -> ephem.Observer:
        """Returns PyEphem Observer object"""
        return self.city

class SunData:
    """
    A class to calculate sunrise, sunset and daylight information for a given location and time.
    
    This class uses the PyEphem library to calculate the position of the sun at a given time and location. 
    It uses the sunrise and sunset times to calculate the duration of daylight, as well as the start and end of civil twilight.
    The class also has the capability to create a plot of the elevation of the sun over a given day.
    
    Attributes
    ----------
    observer : ephem.Observer
        The observer object containing the latitude, longitude, and elevation of the location.
    sunrise_time : datetime.datetime
        The time of sunrise for the current day.
    sunset_time : datetime.datetime
        The time of sunset for the current day.
    civil_twilight_start : datetime.datetime
        The time civil twilight begins for the current day.
    civil_twilight_end : datetime.datetime
        The time civil twilight ends for the current day.
    day_length : int
        The duration of daylight in seconds for the current day.
    time_list : List[str]
        A list of times in the format 'HH:MM' representing each hour of the day, starting with the start of civil twilight and ending with the end of civil twilight.
    sunrise_time_str : str
        The time of sunrise for the current day in the format 'HH:MM:SS'.
    sunset_time_str : str
        The time of sunset for the current day in the format 'HH:MM:SS'.
    
    Methods
    -------
    get_time_list() -> List[str]
        Returns a list of times in the format 'HH:MM' representing each hour of the day, starting with the start of civil twilight and ending with the end of civil twilight.
    get_sunrise_sunset() -> Tuple[str, str, int]
        Returns a tuple containing the time of sunrise, time of sunset, and duration of daylight in seconds for the current day.
    create_daylight_plot(output_file: str, day: Optional[datetime.datetime] = None, custom_colors: Optional[Dict] = None) -> None
        Creates a plot of the elevation of the sun over a given day and saves it to the specified output file.
        If no day is specified, the plot will be created for the current day.
        If custom colors are specified, the plot will use those colors instead of the default color scheme.
    """

    def __init__(self, observer) -> None:
        sun = ephem.Sun()

        # Save off observer
        self.observer = observer

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

    def get_time_list(self) -> List[str]:
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

    def get_sunrise_sunset(self) -> Tuple[str, str, int]:
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

    def create_daylight_plot(self, output_file: str, day: Optional[datetime] = None, custom_colors: Optional[Dict[str, Any]] = None) -> None:
        """ Creates a daylight plot for the current day 

        Parameters
        ----------
        output_file : str
            Path of the output file to save the plot
        day : datetime, optional
            Day to create the plot for, default is None which uses the current day
        custom_colors : dict, optional
            Dictionary containing a list of color values and corresponding data values to use a custom colormap for the plot

        Returns
        -------
        None
        """

        # Get current day
        if day == None:
            day = datetime.now()

        city = self.observer.get_city()

        # Get current day and UTC Offset as ephem only works with UTC
        current_local_time = time.localtime()
        utc_offset = 0
        if current_local_time.tm_isdst == 1:
            utc_offset = 5
        else:
            utc_offset = 6

        # Find Midnight UTC
        midnight_utc = datetime(day.year, day.month, day.day, utc_offset, 0, 0, 0)

        sun = ephem.Sun()

        # Set up x/y and labels
        x = range(24*60)
        y = []
        x_raw_label = []
        x_labels = []

        # Create temp variable for loop
        current_time = midnight_utc

        # Cycle through each hour to get sun position
        for i in x:
            city.date = current_time.strftime("%Y/%m/%d %H:%M")

            # Every hour create an x-tick
            if (i % 60 == 0):
                x_raw_label.append(i)
                x_labels.append((current_time - timedelta(hours=utc_offset)).strftime("%-I:%M %p"))

            sun.compute(city)

            # Compute altitude angle and convert to decimal
            alt = str(sun.alt)
            deg, m, s = alt.split(":")
            deg, m, s = int(deg), float(m), float(s)

            if "-" in alt:
                sign = -1
            else:
                sign = 1

            deg = sign * (abs(deg) + m/60 + s/3600)

            # Add decimal degrees to y axis list
            y.append(deg)

            # Increment Time
            current_time += timedelta(minutes=1)

        # Add Final Label
        x_raw_label.append(x[-1])
        x_labels.append((current_time - timedelta(hours=utc_offset)).strftime("%-I:%M %p"))

        # Create Plot
        fig = plt.figure(figsize=(16,9))
        plt.title(f"Daylight in Grand Forks, ND on {midnight_utc.strftime('%Y-%m-%d')}", fontsize=20)
        plt.plot(x,y, 'k--', linewidth=0)
        plt.ylim([-70,70])
        plt.xlim([x[0], x[-1]])
        plt.xticks(x_raw_label, x_labels, rotation=45, ha="right", fontsize=15)
        plt.yticks(fontsize=15)
        plt.ylabel("Sun Elevation ($^\circ$)", fontsize=20)
        plt.xlabel("@gfndskycolor", fontsize=10)
        plt.tight_layout()

        # Fill in the colors of the plot
        x = np.array(x)
        y = np.array(y)
        plt.fill_between(x, y, 0,
                        where=(y < 0),
                        alpha=0.85, color='black', interpolate=True)

        # Custom Color Map if Data is Available
        if (custom_colors != None):
            norm=plt.Normalize(
                        np.min(x),
                        np.max(x))

            cvals = custom_colors['cvals']
            colors = custom_colors['colors']

            tuples = list(zip(map(norm,cvals), colors))
            cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", tuples)

            for i in x:
                plt.fill_between(x, y, 0,
                                where=((y >= 0) & (x==i)),
                                alpha=1.0, color=cmap(norm(i)), interpolate=True)

            plt.title(f"Dominant Colors of the Sky for Grand Forks, ND on {midnight_utc.strftime('%Y-%m-%d')}", fontsize=20)
        else:
            plt.fill_between(x, y, 0,
                            where=(y >= 0),
                            alpha=1.0, color='#88a9d2', interpolate=True)

        # Save Figure
        plt.savefig(output_file)
        # plt.show()
        fig.clear()
        plt.close('all')

        return


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

    # Create Plot of Today
    cvals  = [0, 6*60+54, 8*60, 9*60, 10*60, 11*60, 12*60, 13*60, 14*60, 15*60, 16*60, 17*60, 18*60, 19*60,19*60+56, 1439]
    colors = ["#000000", "#9e9dad", "#719ed2", "#5c8abf", "#4c81bd", "#3c74b3", "#4d81bb", "#4170aa", "#999cab", "#9b9ca7", "#818da3", "#6787ae", "#5a779b", "#4d6684", "#a1abb7", "#000000"]

    custom_colors = dict()
    custom_colors['cvals'] = cvals
    custom_colors['colors'] = colors

    sun_data.create_daylight_plot("./test.png", custom_colors=custom_colors)
