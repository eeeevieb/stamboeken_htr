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


def get_arguments():
    parser = argparse.ArgumentParser(description="Visualization of regions")

    parser.add_argument("-i", "--image", help="Path to image", type=str, default=None)
    parser.add_argument("-x", "--xml", help="Path to xml file", type=str)
    parser.add_argument(
        "-r", "--resize", help="Whether the image should be resized or not, add if needs to be resized", action="store_true"
    )

    args = parser.parse_args()

    return args


def get_coords(xml_path):
    """
    Get the coordinates of the different regions as well as (new) dimensions from pageXML file

        args:
            xml_path: path to pageXML file
        returns:
            dict of different lists of coordinates for each label
    """

    coords = []

    try:
        # Load the XML content (from a file)
        root = etree.parse(xml_path)

        # get image dimensions from xml
        image_width = root.find(
            "ns:Page", namespaces={"ns": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"}
        ).get("imageWidth")
        image_height = root.find(
            "ns:Page", namespaces={"ns": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"}
        ).get("imageHeight")
        print(image_width, image_height)

        # XPath query to get TextRegion coordinates
        result = root.xpath(
            "//ns:TextRegion/ns:TextLine", namespaces={"ns": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"}
        )

        coords = {}

        for line in result:
            # get label
            label = line.get("custom")
            if label:
                label = label.split("structure", 1)
                label = label[1] if len(label) > 1 else "no label"
            else:
                label = "no label"

            # get coordinates
            text_coordinates = line.find(
                "ns:Coords", namespaces={"ns": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"}
            ).get("points")
            region_coords = text_coordinates.split(" ")
            region_coords_full = []
            for coord in region_coords:
                coord_new = coord.split(",")
                coord_new[0] = int(coord_new[0])
                coord_new[1] = int(coord_new[1])
                region_coords_full.append((coord_new[0], coord_new[1]))

            coords.setdefault(label, []).append(region_coords_full)

    except etree.XMLSyntaxError:
        print(f"Error parsing {xml_path}. File may be malformed.")
    return coords, (image_width, image_height)


def visualize_regions(image_path, coords, resize):
    """
    Visualize regions with given coorndinates on given image

        args:
            image_path: path to image on which to plot the regions, as a string
            coords: coordinates of the regions to plot, as a list of lists
            resize: if the image needs to be resized, as a boolean
    """

    image = Image.open(image_path)

    # if resize is needed
    if resize:
        resized_img_path = "/root/Thesis/resized.jpg"
        resized = image.resize((int(coords[1][0]), int(coords[1][1])))
        resized.save(resized_img_path)
        img = plt.imread(resized_img_path)
    else:
        img = plt.imread(image_path)

    # dict for colors:
    colors = {0: "red", 1: "green", 2: "blue", 3: "yellow", 4: "orange", 5: "purple", 6: "pink", 7: "cyan"}
    used_labels = set()

    # plot image
    fig, ax = plt.subplots()
    ax.set_axis_off()
    ax.imshow(img)

    # create list of the different polygons
    for counter, item in enumerate(coords[0].items()):
        polygons = []

        for coord in item[1]:
            polygon = Polygon(coord)
            polygons.append(polygon)

        # loop through polygons and plot them
        for polygon in polygons:
            label = item[0] if item[0] not in used_labels else None
            x, y = polygon.exterior.xy  # Extract coordinates
            ax.plot(x, y, color=colors[counter], linewidth=0.8, label=label)  # Outline
            ax.fill(x, y, color=colors[counter], alpha=0.3)  # Fill with transparency
            used_labels.add(item[0])

    ax.legend(bbox_to_anchor=(1.05, 1.0), loc="upper left")

    plt.tight_layout()
    plt.savefig("/root/Thesis/visualizations/region_visualization.jpg", dpi=500)
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
