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