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

def produce_plots(input_image, dom_image, overall_image):
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
    # debug = False
    # if debug == True:
    #     print(raw.shape, img.shape)
    #     plt.figure(figsize=(20,10))
    #     plt.subplot(121), plt.imshow(raw), plt.axis('off') 
    #     plt.subplot(122), plt.imshow(img), plt.axis('off') 
    #     plt.show()

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
    output_shape=(1300, 1300, 3)
    avg_patch = np.ones(shape=output_shape, dtype=np.uint8)*np.uint8(average)
    dom_patch = np.ones(shape=output_shape, dtype=np.uint8)*np.uint8(np.round(dominant))

    output_test = np.ones(shape=(675,1200,3), dtype=np.uint8)*np.uint8(np.round(dominant))
    im_rgb = cv2.cvtColor(output_test, cv2.COLOR_BGR2RGB)
    cv2.imwrite(dom_image, im_rgb)

    indices = np.argsort(counts)[::-1]   
    freqs = np.cumsum(np.hstack([[0], counts[indices]/float(counts.sum())]))
    rows = np.int_(output_shape[0]*freqs)

    all_patch = np.zeros(shape=output_shape, dtype=np.uint8)
    for i in range(len(rows) - 1):
        all_patch[rows[i]:rows[i + 1], :, :] += np.uint8(palette[indices[i]])

    fig, (ax0, ax1, ax2) = plt.subplots(1, 3, figsize=(16,9))
    ax0.imshow(avg_patch)
    ax0.set_title(f'Average Color ({avg_hex})', fontsize=15)
    ax0.axis('off')
    ax1.imshow(dom_patch)
    ax1.set_title(f'Dominant Color ({dom_hex})', fontsize=15)
    ax1.axis('off')
    ax2.imshow(all_patch)
    ax2.set_title(f'Top {n_colors} Colors', fontsize=15)
    ax2.axis('off')
    plt.savefig(overall_image)

    return dom_hex

if __name__ == "__main__":
    dom_color = produce_plots("./example/example.png", "./example/dominant.png", "./example/overall.png")