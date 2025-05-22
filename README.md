# Set-up
#### 1. Install Mini-conda
Documentation: https://docs.anaconda.com/miniconda/

#### 2. Conda Create Environment

Create the environment from the environment.yml file:
```bash
conda env create -f environment.yml
```

#### 3. Loghi Instruction:
1. Pull loghi repo here 
```bash
git clone git@github.com:knaw-huc/loghi.git
```
2. Pull all the docker containers as per instructions
```bash
docker pull loghi/docker.laypa
docker pull loghi/docker.htr
docker pull loghi/docker.loghi-tooling
```
3. Go to: https://surfdrive.surf.nl/files/index.php/s/YA8HJuukIUKznSP and download 
   - a laypa model ("general") for detection of baselines and 
   - a loghi-htr model("float32-generic-2023-02-15") for HTR.
4. Specify the parameter paths accordingly (see original documentation of loghi)
5. Run command to run the loghi inference script:
```bash
scripts/inference-pipeline.sh ../images_samples/
```

# Training a laypa model
### Create environment

Create the environment from the environment.yml file in the laypa folder:
```bash
cd laypa
conda env create -f environment.yml
```

### Train model
Training data can be found in stamboeken_htr/training_data. 

Train/test/val split can be made using laypa tooling:

```bash
python tooling/dataset_creation.py -i stamboeken_htr/training_data -o training_data_split
```

To train the model using these data:
```bash
python train.py -c configs/config_stamboeken.yaml -t training_data_split/train_filelist.txt -v training_data_split/val_filelist.txt
```

Specify number of GPUs with ```--num_gpus NUM_GPUS```. Default is 1.
The numbber of iterations, checkpoints and images per batch can also be specified, using the ```--opts``` argument.

Example command for 2 gpus, 32 images per batch, checkpoint periond of 1000 iterations and 10,000 iterations total. Defaults can be found in laypa/configs/config_stamboeken.yaml.
```bash
python train.py -c configs/config_stamboeken.yaml -t training_data_split/train_filelist.txt -v training_data_split/val_filelist.txt --num-gpus=2 --opts SOLVER.IMS_PER_BATCH 32 SOLVER.CHECKPOINT_PERIOD 1000 SOLVER.MAX_ITER 10000
```

For full documentation of the train function, see the [laypa documentation](https://github.com/stefanklut/laypa).

# Scripts
## HTR
1. ```bash
   cd loghi
   ```
2. Change PATHS in [loghi/scripts/inference-pipeline.sh](loghi/scripts/inference-pipeline.sh), as specified in loghi module
3. type command
   ```bash
   scripts/inference-pipeline.sh ../images_samples/
   ```

## HTR on an entire stamboeken collections
```
python run_loghi.py
```

## Extract Information using Regex Patterns
| Case                                       | Search Keyword or Pattern             | Description                                           | Regex Pattern                              | Captured Information                                  |
|--------------------------------------------|---------------------------------------|-------------------------------------------------------|--------------------------------------------|-------------------------------------------------------|
| **1: Vader (Father)**                      | `Vader`                               | Checks if line contains "Vader"                       | `.*Vader\s+(.+)`                           | Text after "Vader" (Father's name)                    |
| **2: Moeder (Mother)**                     | `Moeder`                              | Checks if line contains "Moeder"                      | `.*Moeder\s+(.+)`                          | Text after "Moeder" (Mother's name)                   |
| **3: Geboorte datum (DOB)**                | `Geboren`                             | Checks if line contains "Geboren"                     | `Geboren\s+(.+)`                           | Text after "Geboren" (Date of Birth)                  |
| **4: Geboorte Plaats (Place of Birth)**    | `te`                                  | Checks if line starts with "te"                       | `^te\s+(.+)`                               | Text after "te" (Place of Birth)                      |
| **5: Laatste Woonplaats (Last Residence)** | `laatst gewoond te`                   | Checks if line contains "laatst gewoond te"           | `laatst\s*gewoond te\s+(.+)`               | Text after "laatst gewoond te" (Last Residence)       |
| **6: Campaigns**                           | `4-digit year followed by place name` | Checks if starts with 4 digit and followed by strings | `\b(\d{4})\s+([a-zA-Z]+[\sa-zA-Z]*)`       | 4 digit as Year, string as place                      |
| **7: Military Postings**                   | `more than 1 date pattern`            | Checks if strings has more than one date patterns     | `.*?[0-9]{1,2}\s[A-Z]+[a-z]*\s[1-9]{4}\.*` | String before the date as Context, date as Event Date |


## Extract Information using LLM

```
python Llama.py
```