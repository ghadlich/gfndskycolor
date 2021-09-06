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
from utils import produce_plots
from utils import capture_image_and_tweet

import schedule
from time import sleep
from utils import get_time_schedule
from utils import tweet_civil_twilight_start
from utils import tweet_sunrise
from utils import tweet_sunset
from utils import tweet_civil_twilight_end

def create_schedule():
    """
    Creates a dynamic schedule based on twilight and sunrise/sunset
    """
    sched = get_time_schedule()

    schedule.every().day.at(sched[0]).do(run_twilight_start)
    sched.pop(0)
    schedule.every().day.at(sched[0]).do(run_sunrise)
    sched.pop(0)

    schedule.every().day.at(sched[-1]).do(run_twilight_end)
    sched.pop()
    schedule.every().day.at(sched[-1]).do(run_sunset)
    sched.pop()

    for t in sched:
        schedule.every().day.at(t).do(run_tweeter)

    # This job will be scheduled forever
    return

def run_twilight_start():
    """ Sends a tweet about the start of civil twilight and captures image """
    tweet_civil_twilight_start()
    return run_tweeter()

def run_sunrise():
    """ Sends a tweet about the sunrise and captures image """
    tweet_sunrise()
    return run_tweeter()

def run_sunset():
    """ Sends a tweet about the sunset and captures image """
    tweet_sunset()
    return run_tweeter()

def run_twilight_end():
    """ Sends a tweet about the end of civil twilight and captures image """
    tweet_civil_twilight_end()
    return run_tweeter()

def run_tweeter():
    """ Captures image and sends tweet """
    capture_image_and_tweet()
    return schedule.CancelJob

if __name__ == "__main__":
    # schedule.every().day.at("06:00").do(capture_image_and_tweet)
    # schedule.every().day.at("07:00").do(capture_image_and_tweet)
    # schedule.every().day.at("08:00").do(capture_image_and_tweet)
    # schedule.every().day.at("09:00").do(capture_image_and_tweet)
    # schedule.every().day.at("10:00").do(capture_image_and_tweet)
    # schedule.every().day.at("11:00").do(capture_image_and_tweet)
    # schedule.every().day.at("12:00").do(capture_image_and_tweet)
    # schedule.every().day.at("13:00").do(capture_image_and_tweet)
    # schedule.every().day.at("14:00").do(capture_image_and_tweet)
    # schedule.every().day.at("15:00").do(capture_image_and_tweet)
    # schedule.every().day.at("16:00").do(capture_image_and_tweet)
    # schedule.every().day.at("17:00").do(capture_image_and_tweet)
    # schedule.every().day.at("18:00").do(capture_image_and_tweet)
    # schedule.every().day.at("19:00").do(capture_image_and_tweet)
    # schedule.every().day.at("20:00").do(capture_image_and_tweet)
    # schedule.every().day.at("21:00").do(capture_image_and_tweet)
    # schedule.every().day.at("22:00").do(capture_image_and_tweet)

    # Set an event to schedule the day
    schedule.every().day.at("03:15").do(create_schedule)

    while True:
        schedule.run_pending()
        sleep(1)
