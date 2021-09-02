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

if __name__ == "__main__":
    schedule.every().day.at("06:00").do(capture_image_and_tweet)
    schedule.every().day.at("07:00").do(capture_image_and_tweet)
    schedule.every().day.at("08:00").do(capture_image_and_tweet)
    schedule.every().day.at("09:00").do(capture_image_and_tweet)
    schedule.every().day.at("10:00").do(capture_image_and_tweet)
    schedule.every().day.at("11:00").do(capture_image_and_tweet)
    schedule.every().day.at("12:00").do(capture_image_and_tweet)
    schedule.every().day.at("13:00").do(capture_image_and_tweet)
    schedule.every().day.at("14:00").do(capture_image_and_tweet)
    schedule.every().day.at("15:00").do(capture_image_and_tweet)
    schedule.every().day.at("16:00").do(capture_image_and_tweet)
    schedule.every().day.at("17:00").do(capture_image_and_tweet)
    schedule.every().day.at("18:00").do(capture_image_and_tweet)
    schedule.every().day.at("19:00").do(capture_image_and_tweet)
    schedule.every().day.at("20:00").do(capture_image_and_tweet)
    schedule.every().day.at("21:00").do(capture_image_and_tweet)
    schedule.every().day.at("22:00").do(capture_image_and_tweet)

    while True:
        schedule.run_pending()
        sleep(1)