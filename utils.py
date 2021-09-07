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
import cv2
import numpy as np
from skimage import io
import matplotlib.pyplot as plt
from datetime import datetime
import os
from twitterutils.twitterutils import tweet
from sun_data import CityObserver, SunData

# Globals
image_dir = "./images"
raw_dir = os.path.join(image_dir, "raw")
processed_dir = os.path.join(image_dir, "daily")

def get_time_schedule():
    # Get current day, set at 17:00 UTC for middle of the day
    day = datetime.now().strftime("%Y/%m/%d 17:00")

    # Grand Forks, ND Lat, Long, Elev (Meters)
    observer = CityObserver('47.925259', '-97.032852', 257, day)

    # Compute Sun Data
    sun_data = SunData(observer)

    # Return Time Schedule
    return sun_data.get_time_list()

def capture_image(filename):
    """ Captures an image using NodeJS and Puppeteer and saves it to a png file """

    try:
        os.system("node capture_image.js " + filename)
    except:
        return False

    return True

def capture_image_and_tweet():
    """ Captures an image and tweets the colors """
 
    now = datetime.now()

    baseline_filename = now.strftime("%Y_%m_%d_%H_%M")
    baseline_folder = now.strftime("%Y_%m_%d")
    time_ran = now.strftime("%-I:%M %p")

    try:
        raw_daily_directory = os.path.join(raw_dir, baseline_folder)
        processed_daily_directory = os.path.join(processed_dir, baseline_folder)

        os.makedirs(raw_daily_directory, exist_ok=True)
        os.makedirs(processed_daily_directory, exist_ok=True)

        raw_file = os.path.join(raw_daily_directory, baseline_filename+"_raw.png")
        dom_file = os.path.join(processed_daily_directory, baseline_filename+"_dom.png")
        avg_file = os.path.join(processed_daily_directory, baseline_filename+"_avg.png")
        overall_file = os.path.join(processed_daily_directory, baseline_filename+"_overall.png")

        if capture_image(raw_file) == False:
            print("Error Occurred When Capturing Image...")
            return

        dom_color, avg_color, color_list = produce_plots(raw_file,
                                                        dom_file,
                                                        avg_file,
                                                        overall_file)

        # print("Average Color: " + avg_color)
        # print("Dominant Color: " + dom_color)

        tweet_text = f"The top colors in the sky for Grand Forks, ND at {time_ran} are (in order of dominance):"

        for c in color_list:
            tweet_text += f"\n{c}"

        # Tweet Overall Graphic
        previous_id = tweet(tweet_text, image_path=overall_file, enable_tweet=True)

        # Tweet Average Graphic
        tweet_text =  f"The average color of the sky in Grand Forks, ND at {time_ran} is {avg_color}. Read more about this color: https://encycolorpedia.com/{avg_color[1:]}"
        previous_id = tweet(tweet_text, image_path=avg_file, in_reply_to_status_id=previous_id, enable_tweet=True)

        # Tweet Dominant Graphic
        tweet_text =  f"The dominant color of the sky in Grand Forks, ND at {time_ran} is {dom_color}. Read more about this color: https://encycolorpedia.com/{dom_color[1:]}"
        previous_id = tweet(tweet_text, image_path=dom_file, in_reply_to_status_id=previous_id, enable_tweet=True)

        print(f"Successful Run: {time_ran}")

    except Exception as e:
        print(f"Failed Run: {time_ran}\n" + str(e))

    return

def tweet_civil_twilight_start():
    """ Sends a tweet about civil twilight starting """
    try:
        now = datetime.now()

        time_ran = now.strftime("%-I:%M %p")

        tweet_text = f"It is now Civil Twilight at {time_ran} in Grand Forks, ND"
        tweet(tweet_text, enable_tweet=True)
    except Exception as e:
        print(f"Failed Run: {time_ran}\n" + str(e))

def tweet_sunrise():
    """ Sends a tweet about sunrise """
    try:
        now = datetime.now()

        time_ran = now.strftime("%-I:%M %p")

        tweet_text = f"The sun has now risen at {time_ran} in Grand Forks, ND"
        tweet(tweet_text, enable_tweet=True)
    except Exception as e:
        print(f"Failed Run: {time_ran}\n" + str(e))

def tweet_sunset():
    """ Sends a tweet about sunset """
    try:
        now = datetime.now()

        time_ran = now.strftime("%-I:%M %p")

        tweet_text = f"The sun has now set at {time_ran} in Grand Forks, ND"
        tweet(tweet_text, enable_tweet=True)
    except Exception as e:
        print(f"Failed Run: {time_ran}\n" + str(e))

def tweet_civil_twilight_end():
    """ Sends a tweet about civil twilight ending """
    try:
        now = datetime.now()

        time_ran = now.strftime("%-I:%M %p")

        tweet_text = f"Civil Twilight has now ended at {time_ran} in Grand Forks, ND"
        tweet(tweet_text, enable_tweet=True)
    except Exception as e:
        print(f"Failed Run: {time_ran}\n" + str(e))

def produce_plots(input_image, dom_image, avg_image, overall_image):
    """ Takes an an input image and outputs:
         - Dominant Color Image
         - Overall Summary of Colors Image

        Returns:
         - Dominant Color in Hex
    """

    # Open Input Image
    raw = io.imread(input_image)[:, :, :-1]

    # Slice Out Interesting Part
    mid_y = int(raw.shape[0]/2)
    mid_x = int(raw.shape[1]/2)
    img = raw[mid_y-450:mid_y-175, mid_x-500:mid_x+800]

    # Show Cropping
    # plt.figure(figsize=(20,10))
    # plt.subplot(121), plt.imshow(raw), plt.axis('off')
    # plt.subplot(122), plt.imshow(img), plt.axis('off')
    # plt.show()

    # Find the top N colors by k-means clustering 
    pixels = np.float32(img.reshape(-1, 3))

    n_colors = 10
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
    flags = cv2.KMEANS_RANDOM_CENTERS

    _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
    _, counts = np.unique(labels, return_counts=True)

    # Compute Average and Dominant Colors
    average = img.mean(axis=0).mean(axis=0)
    dominant = palette[np.argmax(counts)]
    dom_hex = '#%02x%02x%02x' % tuple(np.uint8(np.round(dominant)))
    avg_hex = '#%02x%02x%02x' % tuple(np.uint8(np.round(average)))

    # Plot Results
    output_shape=(1600, 900, 3)
    avg_patch = np.ones(shape=output_shape, dtype=np.uint8)*np.uint8(average)
    dom_patch = np.ones(shape=output_shape, dtype=np.uint8)*np.uint8(np.round(dominant))

    output_test = np.ones(shape=(675,1200,3), dtype=np.uint8)*np.uint8(np.round(dominant))
    im_rgb = cv2.cvtColor(output_test, cv2.COLOR_BGR2RGB)
    cv2.imwrite(dom_image, im_rgb)

    output_test = np.ones(shape=(675,1200,3), dtype=np.uint8)*np.uint8(np.round(average))
    im_rgb = cv2.cvtColor(output_test, cv2.COLOR_BGR2RGB)
    cv2.imwrite(avg_image, im_rgb)

    indices = np.argsort(counts)[::-1]
    freqs = np.cumsum(np.hstack([[0], counts[indices]/float(counts.sum())]))
    rows = np.int_(output_shape[0]*freqs)

    # Keep Ordered List of Dominant Colors
    color_list = list()

    for i in indices:
        hex_color = '#%02x%02x%02x' % tuple(np.uint8(np.round(palette[i])))

        if hex_color not in color_list:
            color_list.append(hex_color)

    all_patch = np.zeros(shape=output_shape, dtype=np.uint8)
    for i in range(len(rows) - 1):
        all_patch[rows[i]:rows[i + 1], :, :] += np.uint8(palette[indices[i]])

    fig, (ax0, ax1, ax2) = plt.subplots(1, 3, figsize=(16,9))
    ax0.imshow(avg_patch)
    ax0.set_title(f'Average Color ({avg_hex})', fontsize=20)
    ax0.axis('off')
    ax1.imshow(dom_patch)
    ax1.set_title(f'Dominant Color ({dom_hex})', fontsize=20)
    ax1.axis('off')
    ax2.imshow(all_patch)
    ax2.set_title(f'Top {len(color_list)} Colors', fontsize=20)
    ax2.axis('off')
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(overall_image)
    plt.close('all')

    return dom_hex, avg_hex, color_list

if __name__ == "__main__":
    dom_color, avg_color, color_list = produce_plots("./example/example.png",
                                                     "./example/dominant.png",
                                                     "./example/average.png",
                                                     "./example/overall.png")