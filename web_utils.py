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
from bs4 import BeautifulSoup

import requests
import os
from urllib.request import urlretrieve

def download_images_and_create_animation(base_url, destination_folder, output_filename, framerate=30, hold_last_frame_duration_s=0):
    """ Takes in a URL and creates an mp4 animation with a given framerate """

    os.makedirs(destination_folder, exist_ok=True)

    # Make the base url is complete
    if base_url[-1] != "/":
        base_url += "/"

    # Setup Requests
    r  = requests.get(base_url)
    data = r.text
    soup = BeautifulSoup(data, features="lxml")

    # Keep track of number of images downloaded and last name
    count = 0
    image = ""

    image_list = []

    # Collect all relevant links
    for link in soup.find_all('a'):
        image = link.get('href')
        if (".gif" in image or ".png" in image or ".jpg" in image):
            # print(base_url + image)
            image_list.append(image)

    # Retreive the images
    for image in image_list:
        try:
            urlretrieve(base_url + image, os.path.join(destination_folder, image))
            count += 1
        except:
            #print(f"Failed: {base_url + image}")
            pass

    # If there were more than two images, attempt to create an animation
    if (count > 1):
        images_path = os.path.abspath(os.path.join(destination_folder, "*"+image[-4:]))
        animation_path = os.path.abspath(os.path.join(destination_folder, output_filename))
        if hold_last_frame_duration_s > 0:
            hold = f"-vf tpad=stop_mode=clone:stop_duration={hold_last_frame_duration_s}"
        else:
            hold = ""
        try:
            _ = os.system(f"ffmpeg -y -hide_banner -loglevel error -framerate {framerate} -pattern_type glob -i '{images_path}' -c:v libx264 -pix_fmt yuv420p {hold} {animation_path}")
            return animation_path
        except:
            return None

    return None

if __name__ == "__main__":
    # base_url = "https://services.swpc.noaa.gov/images/animations/lasco-c3/lasco/"
    # destination_folder = "./animation/lasco-c3/2021-09-12"
    # output_filename = "animation.mp4"
    # framerate = 30
    # download_images_and_create_animation(base_url, destination_folder, output_filename, framerate=framerate)

    # base_url = "https://services.swpc.noaa.gov/images/animations/ctipe/tec/"
    # destination_folder = "./animation/electrons/2021-09-12"
    # output_filename = "animation.mp4"
    # framerate = 30
    # download_images_and_create_animation(base_url, destination_folder, output_filename, framerate=framerate, hold_last_frame_duration_s=3)

    # base_url = "https://services.swpc.noaa.gov/images/animations/suvi/secondary/304/"
    # destination_folder = "./animation/sun/2021-09-12"
    # output_filename = "animation.mp4"
    # framerate = 30
    # download_images_and_create_animation(base_url, destination_folder, output_filename, framerate=framerate)

    base_url = "https://services.swpc.noaa.gov/images/animations/ovation/north/"
    destination_folder = "./animation/aurora/2021-09-12"
    output_filename = "animation.mp4"
    framerate = 60
    download_images_and_create_animation(base_url, destination_folder, output_filename, framerate=framerate, hold_last_frame_duration_s=3)

    
