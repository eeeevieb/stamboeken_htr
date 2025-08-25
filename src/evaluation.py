import re
from lxml import etree
from shapely.geometry import Polygon
from shapely.validation import make_valid
from statistics import mean 
import os
import numpy as np
import argparse

def get_arguments():
    parser = argparse.ArgumentParser(description="Evaluation script. Calculates mIoU, recall, precision and F1")

    parser.add_argument("-e", "--experiment_results", help="Path to experiment results folder", type=str, required=True)
    parser.add_argument("-gt", "--ground_truth", help="Path to ground truth folder", type=str, required=True)

    args = parser.parse_args()

    return args

def coords_to_int(coords):
    """
        Turns coordinates as string to coordinates in a list of tuples of ints, eg [(410, 3137), (410, 3139), (412, 3141), (410, 3137)]

        agrs:
            coordinates (from an xml file) as a string
        
        returns:
            coordinates as [(int,int)]
    """
    coords_full = []
    for coord in coords.split(" "):
        coord_new = coord.split(",")
        coord_new[0] = int(coord_new[0])
        coord_new[1] = int(coord_new[1])
        coords_full.append((coord_new[0], coord_new[1]))
    
    return coords_full


def calc_miou(path_exp, path_gt):
    """
        Calculates intersection over union and true positives of two sets of regions (one experiment result and one ground truth) on one image per region label. 
        Also calculates how many regions are predicted per label in given image.

        Two ways of evaluating are used:
        - Evaluation 1: a prediction is correct when the IoU is over 0.5
        - Evaluation 2: a predcition is correct when the intersection is over 0.9

        args:
            path_exp: path to experiment result xml file
            path_gt: path to ground truth xml file

        returns:
            - iou: the intersection over union of the regions, float
            - iou_per_label: the intersection over union per region label, {float:string}
            - true_positives_per_label: amount of true predicted regions per label according to evaluation 1
            - regions_per_label_exp: amount of predicted regions per label
            - regions_per_label_gt: amount of ground truth regions per label
            - eval2: true positives according to evaluation 2
    """

    iou_per_label = {"Name": [], "Award": [], "Birth Place": [], "Birth Date": [], "Father": [],
                    "Mother": [], "Religion": [], "Marriage Location": [], "Spouse": [],
                    "Children": [], "Rank": [], "Ship": [], "Departure": [], "Death Date": [],
                    "Death Place": [], "Retirement": [], "Repatriation": [], "Text": []}
    ious = []
    true_positives_per_label = {"Name": 0, "Award": 0, "Birth Place": 0, "Birth Date": 0, "Father": 0,
                    "Mother": 0, "Religion": 0, "Marriage Location": 0, "Spouse": 0,
                    "Children": 0, "Rank": 0, "Ship": 0, "Departure": 0, "Death Date": 0,
                    "Death Place": 0, "Retirement": 0, "Repatriation": 0, "Text": 0}
    regions_per_label_exp = {"Name": 0, "Award": 0, "Birth Place": 0, "Birth Date": 0, "Father": 0,
                    "Mother": 0, "Religion": 0, "Marriage Location": 0, "Spouse": 0,
                    "Children": 0, "Rank": 0, "Ship": 0, "Departure": 0, "Death Date": 0,
                    "Death Place": 0, "Retirement": 0, "Repatriation": 0, "Text": 0}
    regions_per_label_gt = {"Name": 0, "Award": 0, "Birth Place": 0, "Birth Date": 0, "Father": 0,
                    "Mother": 0, "Religion": 0, "Marriage Location": 0, "Spouse": 0,
                    "Children": 0, "Rank": 0, "Ship": 0, "Departure": 0, "Death Date": 0,
                    "Death Place": 0, "Retirement": 0, "Repatriation": 0, "Text": 0}
    eval2 = {"Name": 0, "Award": 0, "Birth Place": 0, "Birth Date": 0, "Father": 0,
                    "Mother": 0, "Religion": 0, "Marriage Location": 0, "Spouse": 0,
                    "Children": 0, "Rank": 0, "Ship": 0, "Departure": 0, "Death Date": 0,
                    "Death Place": 0, "Retirement": 0, "Repatriation": 0, "Text": 0}
    pols_gt_labels = {}
    
    # get polygons and region count from ground truth xml file
    try:
        root = etree.parse(path_gt)

        result = root.xpath(
            '//ns:TextRegion/ns:TextLine',
            namespaces={'ns': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}
        )

        for line in result:
            # find coords of textlines
            coords = line.find("ns:Coords", namespaces={
                    'ns': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}).get("points")
            # get label
            custom = line.get("custom")
            matches = re.findall(r"type:(.*?);", custom)
            if matches:
                labels = matches[0]
            else: 
                labels = "no label"
            
            # update region count
            regions_per_label_gt[labels] += 1

            # create polygon
            coords_gt_int = coords_to_int(coords)
            pol_gt = Polygon(coords_gt_int)
            pol_gt_fixed = make_valid(pol_gt)

            pols_gt_labels[pol_gt_fixed] = labels

    except etree.XMLSyntaxError:
        print(f"Error parsing {path_gt}. File may be malformed.")

    # get polygons and region count from experiment result xml file
    try:
        root = etree.parse(path_exp)

        result = root.xpath(
            '//ns:TextLine',
            namespaces={'ns': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}
        )

        for line in result:
            # find coords in textlines
            coords_line = line.find("ns:Coords", namespaces={
                    'ns': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'})
            if coords_line is not None:
                coords_exp = line.find("ns:Coords", namespaces={
                    'ns': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}).get("points")
            else:
                break

             # create polygon of coords
            coords_exp_int = coords_to_int(coords_exp)
            pol_exp = Polygon(coords_exp_int)
            pol_exp_fixed = make_valid(pol_exp)

            # get label
            custom = line.get("custom")
            matches = re.findall(r"type:(.*?);", custom)
            if matches:
                label = matches[0]
            else: 
                label = "no label"
            
            regions_per_label_exp[label] += 1

            # loop over ground truth polygons to find intersections with current experiment result polygon
            already_found = False
            for pol_gt_fixed in pols_gt_labels.keys():
                intersect = pol_gt_fixed.intersection(pol_exp_fixed).area

                if intersect > 0:
                    # only count if label is the same
                    if label == pols_gt_labels[pol_gt_fixed]:
                        # calculate IoU
                        union = pol_gt_fixed.union(pol_exp_fixed).area
                        iou = intersect / union
                        ious.append(iou)
                        iou_per_label[label].append(iou)

                        # for evaluation 1
                        if iou >= 0.5:
                            true_positives_per_label[label] += 1

                        # for evaluation 2
                        if intersect >= 0.9:
                            if already_found == False:
                                eval2[label] += 1
                                already_found = True

    except etree.XMLSyntaxError:
        print(f"Error parsing {path_exp}. File may be malformed.")
    
    return ious, iou_per_label, true_positives_per_label, regions_per_label_exp, regions_per_label_gt, eval2

def main(exp_input, gt_input):
    # initiate dicts to store evaluation metrics
    iou_dict = {"Name": [], "Award": [], "Birth Place": [], "Birth Date": [], "Father": [],
                        "Mother": [], "Religion": [], "Marriage Location": [], "Spouse": [],
                        "Children": [], "Rank": [], "Ship": [], "Departure": [], "Death Date": [],
                        "Death Place": [], "Retirement": [], "Repatriation": [], "Text": []}
    ious_all = []
    mean_ious = {"Name": float('nan'), "Award": float('nan'), "Birth Place": float('nan'), "Birth Date": float('nan'), "Father": float('nan'),
                        "Mother": float('nan'), "Religion": float('nan'), "Marriage Location": float('nan'), "Spouse": float('nan'),
                        "Children": float('nan'), "Rank": float('nan'), "Ship": float('nan'), "Departure": float('nan'), "Death Date": float('nan'),
                        "Death Place": float('nan'), "Retirement": float('nan'), "Repatriation": float('nan'), "Text": float('nan')}

    true_positives_per_label_all = {"Name": 0, "Award": 0, "Birth Place": 0, "Birth Date": 0, "Father": 0,
                    "Mother": 0, "Religion": 0, "Marriage Location": 0, "Spouse": 0,
                    "Children": 0, "Rank": 0, "Ship": 0, "Departure": 0, "Death Date": 0,
                    "Death Place": 0, "Retirement": 0, "Repatriation": 0, "Text": 0}
    regions_per_label_exp_all = {"Name": 0, "Award": 0, "Birth Place": 0, "Birth Date": 0, "Father": 0,
                    "Mother": 0, "Religion": 0, "Marriage Location": 0, "Spouse": 0,
                    "Children": 0, "Rank": 0, "Ship": 0, "Departure": 0, "Death Date": 0,
                    "Death Place": 0, "Retirement": 0, "Repatriation": 0, "Text": 0}
    regions_per_label_gt_all = {"Name": 0, "Award": 0, "Birth Place": 0, "Birth Date": 0, "Father": 0,
                    "Mother": 0, "Religion": 0, "Marriage Location": 0, "Spouse": 0,
                    "Children": 0, "Rank": 0, "Ship": 0, "Departure": 0, "Death Date": 0,
                    "Death Place": 0, "Retirement": 0, "Repatriation": 0, "Text": 0}
    all_eval2 = {"Name": 0, "Award": 0, "Birth Place": 0, "Birth Date": 0, "Father": 0,
                    "Mother": 0, "Religion": 0, "Marriage Location": 0, "Spouse": 0,
                    "Children": 0, "Rank": 0, "Ship": 0, "Departure": 0, "Death Date": 0,
                    "Death Place": 0, "Retirement": 0, "Repatriation": 0, "Text": 0}
    precisions_eval1 = {"Name": float('nan'), "Award": float('nan'), "Birth Place": float('nan'), "Birth Date": float('nan'), "Father": float('nan'),
                        "Mother": float('nan'), "Religion": float('nan'), "Marriage Location": float('nan'), "Spouse": float('nan'),
                        "Children": float('nan'), "Rank": float('nan'), "Ship": float('nan'), "Departure": float('nan'), "Death Date": float('nan'),
                        "Death Place": float('nan'), "Retirement": float('nan'), "Repatriation": float('nan'), "Text": float('nan')}
    recalls_eval1 = {"Name": float('nan'), "Award": float('nan'), "Birth Place": float('nan'), "Birth Date": float('nan'), "Father": float('nan'),
                        "Mother": float('nan'), "Religion": float('nan'), "Marriage Location": float('nan'), "Spouse": float('nan'),
                        "Children": float('nan'), "Rank": float('nan'), "Ship": float('nan'), "Departure": float('nan'), "Death Date": float('nan'),
                        "Death Place": float('nan'), "Retirement": float('nan'), "Repatriation": float('nan'), "Text": float('nan')}
    f_ones_eval1 = {"Name": float('nan'), "Award": float('nan'), "Birth Place": float('nan'), "Birth Date": float('nan'), "Father": float('nan'),
                        "Mother": float('nan'), "Religion": float('nan'), "Marriage Location": float('nan'), "Spouse": float('nan'),
                        "Children": float('nan'), "Rank": float('nan'), "Ship": float('nan'), "Departure": float('nan'), "Death Date": float('nan'),
                        "Death Place": float('nan'), "Retirement": float('nan'), "Repatriation": float('nan'), "Text": float('nan')}
    precisions_eval2 = {"Name": float('nan'), "Award": float('nan'), "Birth Place": float('nan'), "Birth Date": float('nan'), "Father": float('nan'),
                        "Mother": float('nan'), "Religion": float('nan'), "Marriage Location": float('nan'), "Spouse": float('nan'),
                        "Children": float('nan'), "Rank": float('nan'), "Ship": float('nan'), "Departure": float('nan'), "Death Date": float('nan'),
                        "Death Place": float('nan'), "Retirement": float('nan'), "Repatriation": float('nan'), "Text": float('nan')}
    recalls_eval2 = {"Name": float('nan'), "Award": float('nan'), "Birth Place": float('nan'), "Birth Date": float('nan'), "Father": float('nan'),
                        "Mother": float('nan'), "Religion": float('nan'), "Marriage Location": float('nan'), "Spouse": float('nan'),
                        "Children": float('nan'), "Rank": float('nan'), "Ship": float('nan'), "Departure": float('nan'), "Death Date": float('nan'),
                        "Death Place": float('nan'), "Retirement": float('nan'), "Repatriation": float('nan'), "Text": float('nan')}
    f_ones_eval2 = {"Name": float('nan'), "Award": float('nan'), "Birth Place": float('nan'), "Birth Date": float('nan'), "Father": float('nan'),
                        "Mother": float('nan'), "Religion": float('nan'), "Marriage Location": float('nan'), "Spouse": float('nan'),
                        "Children": float('nan'), "Rank": float('nan'), "Ship": float('nan'), "Departure": float('nan'), "Death Date": float('nan'),
                        "Death Place": float('nan'), "Retirement": float('nan'), "Repatriation": float('nan'), "Text": float('nan')}


    for root_dir, _, files in os.walk(exp_input):
        for file_name in sorted(files):
            if file_name.endswith(".xml"):
                file_path = os.path.join(root_dir, file_name)
                print(f"Processing xml: {file_path}...")
                gt_path = gt_input + '/' + file_name

                ious_individual, iou_dict_individual, true_positives_per_label_individual, regions_per_label_exp_individual, regions_per_label_gt_individual, individual_eval2 = calc_miou(file_path, gt_path)
                
                # process values of this image into dicts of all image values
                iou_dict = {key: iou_dict[key] + iou_dict_individual[key] for key in iou_dict}
                ious_all.append(ious_individual)
                true_positives_per_label_all = {key: true_positives_per_label_all[key] + true_positives_per_label_individual[key] for key in true_positives_per_label_all}
                regions_per_label_exp_all = {key: regions_per_label_exp_all[key] + regions_per_label_exp_individual[key] for key in regions_per_label_exp_all}
                regions_per_label_gt_all = {key: regions_per_label_gt_all[key] + regions_per_label_gt_individual[key] for key in regions_per_label_gt_all}
                all_eval2 = {key: all_eval2[key] + individual_eval2[key] for key in all_eval2}

    # miou per label
    for label in iou_dict.keys():
        if len(iou_dict[label]) > 0:
            mean_iou = np.nanmean(iou_dict[label])
            mean_ious[label] = mean_iou

    # miou
    all_ious = []
    for values in iou_dict.values():
        for value in values:
            all_ious.append(value)

    # evaluation 1 macro precision
    for label in precisions_eval1.keys():
        if regions_per_label_exp_all[label] != 0:
            precision = true_positives_per_label_all[label] / regions_per_label_exp_all[label]
            precisions_eval1[label] = precision

    # evaluation 1 macro recall 
    for label in recalls_eval1.keys():
        if regions_per_label_gt_all[label] != 0:
            recall = true_positives_per_label_all[label] / regions_per_label_gt_all[label]
            recalls_eval1[label] = recall

    # evaluation 1 macro F1
    for label in precisions_eval1.keys():
        if precisions_eval1[label]+recalls_eval1[label] != 0:
            f_one = (2*precisions_eval1[label]*recalls_eval1[label])/(precisions_eval1[label]+recalls_eval1[label])
            f_ones_eval1[label] = f_one

    # evaluation 2 macro precision
    for label in precisions_eval2.keys():
        if regions_per_label_exp_all[label] != 0:
            precision = all_eval2[label] / regions_per_label_exp_all[label]
            precisions_eval2[label] = precision

    # evaluation 2 macro recall 
    for label in recalls_eval2.keys():
        if regions_per_label_gt_all[label] != 0:
            recall = all_eval2[label] / regions_per_label_gt_all[label]
            recalls_eval2[label] = recall

    # evaluation 2 macro F1
    for label in precisions_eval2.keys():
        if precisions_eval2[label]+recalls_eval2[label] != 0:
            f_one = (2*precisions_eval2[label]*recalls_eval2[label])/(precisions_eval2[label]+recalls_eval2[label])
            f_ones_eval2[label] = f_one

    print("Mean iou per label:", mean_ious)
    print("mIoU:", mean(all_ious))
    print("Macro mIoU:", np.nanmean(list(mean_ious.values())))
    print("Macro precision eval1:", np.nanmean(list(precisions_eval1.values())))
    print("Macro recall eval1:", np.nanmean(list(recalls_eval1.values())))
    print("Macro F1:", np.nanmean(list(f_ones_eval1.values())))
    print("Macro precision eval2:", np.nanmean(list(precisions_eval2.values())))
    print("Macro recall eval2:", np.nanmean(list(recalls_eval2.values())))
    print("Macro F1 eval2:", np.nanmean(list(f_ones_eval2.values())))


if __name__ == "__main__":
    args = get_arguments()
    main(args.experiment_results, args.ground_truth)
