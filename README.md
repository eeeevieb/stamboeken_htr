### Install Mini-conda
Documentation: https://docs.anaconda.com/miniconda/

### Conda Create Environment

Create the environment from the environment.yml file:
```bash
conda env create -f environment.yml
```

### Run Script
1. ```bash
   cd loghi
   ```
2. Change PATHS in [loghi/scripts/inference-pipeline.sh](loghi/scripts/inference-pipeline.sh), as specified in loghi module
3. type command
   ```bash
   scripts/inference-pipeline.sh ../images_samples/
   ```

### Loghi Instruction:
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