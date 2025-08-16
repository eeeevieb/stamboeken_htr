import os
from pathlib import Path
from typing import Optional, Sequence

from detectron2.config import CfgNode

from data import dataset
from data.preprocess import Preprocess
from utils.input_utils import clean_input_paths


def preprocess_datasets(
    cfg: CfgNode,
    train: Optional[str | Path | Sequence[str | Path]],
    val: Optional[str | Path | Sequence[str | Path]],
    output_dir: str | Path,
    save_image_locations: bool = True,
):
    """
    Preprocess the dataset(s). Converts ground truth PageXML to label masks for training

    Args:
        cfg (CfgNode): Configuration node.
        train (str | Path | Sequence[str | Path]): Path to dir/txt(s) containing the training images.
        val (str | Path | Sequence[str | Path]): Path to dir/txt(s) containing the validation images.
        output_dir (str | Path): Path to output directory where the processed data will be saved.
        save_image_locations (bool): Flag to save processed image locations (for retraining).

    Raises:
        FileNotFoundError: If a training dir/txt does not exist.
        FileNotFoundError: If a validation dir/txt does not exist.
        FileNotFoundError: If the output dir does not exist.
    """

    if isinstance(output_dir, str):
        output_dir = Path(output_dir)
    if not output_dir.is_dir():
        raise FileNotFoundError(f"Output Folder not found: {output_dir} does not exist")

    process = Preprocess(cfg)  # type: ignore

    train_output_dir = None
    if train is not None:
        train = clean_input_paths(train)
        if not all((missing := path).exists() for path in train):
            raise FileNotFoundError(f"Train File/Folder not found: {missing} does not exist")

        train_output_dir = output_dir.joinpath("train")
        process.set_input_paths(train)
        process.set_output_dir(train_output_dir)
        process.run()

        if save_image_locations:
            if process.input_paths is None:
                raise TypeError("Cannot run when the input path is None")
            # Saving the images used to a txt file
            os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)
            train_image_output_path = Path(cfg.OUTPUT_DIR).joinpath("training_images.txt")

            with train_image_output_path.open(mode="w") as f:
                for path in process.input_paths:
                    f.write(f"{path}\n")

    val_output_dir = None
    if val is not None:
        val = clean_input_paths(val)
        if not all((missing := path).exists() for path in val):
            raise FileNotFoundError(f"Validation File/Folder not found: {missing} does not exist")

        val_output_dir = output_dir.joinpath("val")
        process.set_input_paths(val)
        process.set_output_dir(val_output_dir)
        process.run()

        if save_image_locations:
            if process.input_paths is None:
                raise TypeError("Cannot run when the input path is None")
            # Saving the images used to a txt file
            os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)
            val_image_output_path = Path(cfg.OUTPUT_DIR).joinpath("validation_images.txt")

            with val_image_output_path.open(mode="w") as f:
                for path in process.input_paths:
                    f.write(f"{path}\n")

    dataset.register_datasets(
        train_output_dir,
        val_output_dir,
        train_name="train",
        val_name="val",
    )
