from fix_transcript import fix_all
from label_regions import process_all_xml_files
import subprocess
import os
import pty
import argparse

# input: (folder with) stamboeken
# output: (folder with) labeled xml files

input_path = "/root/Thesis/stamboeken_htr/test"
output_path = "/root/Thesis/stamboeken_htr/test"


def get_arguments():
    parser = argparse.ArgumentParser(description="Visualization of regions")

    parser.add_argument("-i", "--input", help="Path to input folder", type=str, required=True)
    parser.add_argument("-o", "--output", help="Path to output folder", type=str, required=True)

    args = parser.parse_args()

    return args


def create_training_data(input_path, output_path):

    # Create transcripts
    try:
        os.chdir("../")
        os.chdir("../")
        os.chdir("loghi")

        # Create new tty
        # otherwise got error: "the input device is not a TTY"
        master_fd, slave_fd = pty.openpty()

        # Call CLI Process
        cmd = "scripts/inference-pipeline.sh " f"{input_path}"

        print("[DEBUG]: {}".format(cmd))
        proc = subprocess.Popen(
            cmd, stdin=slave_fd, stderr=subprocess.STDOUT, shell=True, universal_newlines=True, start_new_session=True
        )

        proc.communicate()
        print(f"Successfully ran bash script: {cmd}")

    except subprocess.CalledProcessError as e:
        print(f"Error running bash script: {e}")

    # Fixing the transcripts
    print("Fixing transcripts")
    fix_all(f"{input_path}/page")

    # Labeling the transcripts
    output_dir = f"{input_path}/labeled"
    os.makedirs(output_dir, exist_ok=True)
    print("Labeling transcripts")
    process_all_xml_files(f"{input_path}/fixed", input_path)


def main(args):
    """
    Plots regions from a pageXML file on a given image
    """

    create_training_data(args.input, args.output)


if __name__ == "__main__":
    args = get_arguments()
    main(args)
