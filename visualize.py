# import cv2
import numpy as np
import matplotlib.pyplot as plt 
from typing import Any

import os
from lxml import etree
import re
import csv
import geopandas as gpd
from shapely.geometry import Polygon

from PIL import Image 

import argparse

# image_path = 'stamboeken_htr/bronbeek_stamboeken/NL-HaNA_2.10.50_1_0005.jpg'
# resized_img_path= '/root/Thesis/resized.jpg'
# xml_path = '/root/Thesis/xmls/jeanjacques_gemini.xml'

def get_arguments():
    parser = argparse.ArgumentParser(description="Visualization of regions")

    parser.add_argument("-i", "--image", help="Path to image", type=str, default=None)
    parser.add_argument("-x", "--xml", help="Path to xml file", type=str)
    parser.add_argument("-r", "--resize", help="Resize image to the following dimensions: x y", nargs="+", type=int)

    args = parser.parse_args()

    return args

def get_coords(xml_path):
    """
    Get the coordinates of the difefrent regions from pageXML file

        args: 
            xml_path: path to pageXML file
        returns: 
            dict of different lists of coordinates for each label
    """

    coords = []

    try:
        # Load the XML content (from a file)
        root = etree.parse(xml_path)

        # XPath query to get TextRegion coordinates
        result = root.xpath(
            '//ns:TextRegion',
            namespaces={'ns': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}
        )

        # if result is None:
        #     # Log file name if no TextEquiv tag is found
        #     with open(os.path.join(output_path, "image_htr_error.txt"), "a+") as error_log:
        #         error_log.write(f"{file_path}\n")
        #     print(f"No TextEquiv tag found in {file_path}. Logged in image_htr_error.txt.")

        coords = {}

        for line in result:
            # get label
            label = line.get("custom")
            if label:
                label = label.split("structure", 1)
                label = label[1] if len(label) > 1 else ""
            else:
                label = "no label"

            # get coordinates
            text_coordinates = line.find("ns:Coords", namespaces={
                'ns': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}).get("points")
            region_coords = text_coordinates.split(" ")
            region_coords_full = []
            for coord in region_coords:
                coord_new = coord.split(",")
                coord_new[0] = int(coord_new[0])
                coord_new[1] = int(coord_new[1])
                region_coords_full.append(tuple(coord_new))
            
            coords.setdefault(label, []).append(region_coords_full)

    except etree.XMLSyntaxError:
        print(f"Error parsing {file_path}. File may be malformed.")

    return coords

def visualize_regions(image_path, coords, resize):
    """
    Visualize regions with given coorndinates on given image

        args:
            image_path: path to image on which to plot the regions
            coords: coordinates of the regions to plot, as a list of lists
            resize: if the image needs to be resized, list of new dimensions [x,y], else resize is None
    """

    image = Image.open(image_path)

    # if resize is needed
    if resize:
        resized_img_path= '/root/Thesis/resized.jpg'
        resized = image.resize((resize[0], resize[1]))
        resized.save(resized_img_path)

        img = plt.imread(resized_img_path)
    else:
        img = plt.imread(image_path)

    # dict for colors:
    colors = {0: "red", 1: "green", 2: "blue", 3: "yellow", 4: "orange", 5: "purple"}
    used_labels = set()

    # plot image
    fig, ax = plt.subplots()
    ax.imshow(img)

    # create list of the different polygons
    for counter, item in enumerate(coords.items()):
        polygons = []

        for coord in item[1]:
            polygon = Polygon(coord)
            polygons.append(polygon)

        # loop through polygons and plot them
        for polygon in polygons:
            label = item[0] if item[0] not in used_labels else None
            x, y = polygon.exterior.xy  # Extract coordinates
            ax.plot(x, y, color=colors[counter], linewidth=2, label=label)  # Outline
            ax.fill(x, y, color=colors[counter], alpha=0.3)  # Fill with transparency
            used_labels.add(item[0])

    ax.legend()

    plt.show()
    return


def main(args):
    """
    Plots regions from a pageXML file on a given image
    """

    coords = get_coords(args.xml)
    visualize_regions(args.image, coords, args.resize)

if __name__ == "__main__":
    args = get_arguments()
    main(args)

# get region id from xml
# make different lists of coord for different regions
# different colors fun