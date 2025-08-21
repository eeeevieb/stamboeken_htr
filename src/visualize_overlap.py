from visualize import get_coords
import matplotlib.pyplot as plt 
from shapely.geometry import Polygon
from PIL import Image 
import argparse

    
def get_arguments():
    parser = argparse.ArgumentParser(description="Visualization of regions to compare ground truth to results of experiment")

    parser.add_argument("-i", "--image", help="Path to image", type=str, required=True)
    parser.add_argument("-g", "--groundtruth", help="Path to ground truth xml file", type=str, required=True)
    parser.add_argument("-e", "--experiment", help="Path to experiment result xml file", type=str, required=True)

    args = parser.parse_args()

    return args

def visualize_overlap(image_path, gt, exp):
    """
    Visualizes regions of two xml files, mainly ground truth and experiment results, on one image to compare regions

        args:
            image_path: path to image on which to plot the regions, as a string
            gt: path to ground truth xml file, as a strig
            exp: path to experiment result xml file, as a string
    """
    coords_gt = get_coords(gt)
    coords_exp = get_coords(exp)

    image = Image.open(image_path)

    img = plt.imread(image_path)

    used_labels = set()

    # plot image
    fig, ax = plt.subplots()
    ax.set_axis_off()
    ax.imshow(img)

    # create list of the different polygons of ground truth
    for counter, item in enumerate(coords_gt[0].items()):
        polygons = []

        for coord in item[1]:
            try:
                polygon = Polygon(coord)
                polygons.append(polygon)
            except:
                continue

        # loop through polygons and plot them
        for polygon in polygons:
            label = 'Ground Truth' if 'Ground Truth' not in used_labels else None
            x, y = polygon.exterior.xy
            ax.plot(x, y, color="red", linewidth=0.8, label=label)
            ax.fill(x, y, color="red", alpha=0.3)
            used_labels.add('Ground Truth')


    # create list of the different polygons of experiment result
    for counter, item in enumerate(coords_exp[0].items()):
        polygons = []

        for coord in item[1]:
            polygon = Polygon(coord)
            polygons.append(polygon)

        # loop through polygons and plot them
        for polygon in polygons:
            label = 'Experiment' if 'Experiment' not in used_labels else None
            x, y = polygon.exterior.xy
            ax.plot(x, y, color="blue", linewidth=0.8, label=label)
            ax.fill(x, y, color="blue", alpha=0.3)
            used_labels.add('Experiment')

    ax.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')

    plt.tight_layout()
    plt.show()

def main(args):

    visualize_overlap(args.image, args.groundtruth, args.experiment)

if __name__ == "__main__":
    args = get_arguments()
    main(args)


