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

# Scripts
### Run Loghi 
1. ```bash
   cd loghi
   ```
2. Change PATHS in [loghi/scripts/inference-pipeline.sh](loghi/scripts/inference-pipeline.sh), as specified in loghi module
3. type command
   ```bash
   scripts/inference-pipeline.sh ../images_samples/
   ```

### Run Loghi on entire stamboeken
```
python run_loghi.py
```

### Information Extraction using Regex Patterns
| Case                                       | Search Keyword or Pattern             | Description                                           | Regex Pattern                              | Captured Information                                  |
|--------------------------------------------|---------------------------------------|-------------------------------------------------------|--------------------------------------------|-------------------------------------------------------|
| **1: Vader (Father)**                      | `Vader`                               | Checks if line contains "Vader"                       | `.*Vader\s+(.+)`                           | Text after "Vader" (Father's name)                    |
| **2: Moeder (Mother)**                     | `Moeder`                              | Checks if line contains "Moeder"                      | `.*Moeder\s+(.+)`                          | Text after "Moeder" (Mother's name)                   |
| **3: Geboorte datum (DOB)**                | `Geboren`                             | Checks if line contains "Geboren"                     | `Geboren\s+(.+)`                           | Text after "Geboren" (Date of Birth)                  |
| **4: Geboorte Plaats (Place of Birth)**    | `te`                                  | Checks if line starts with "te"                       | `^te\s+(.+)`                               | Text after "te" (Place of Birth)                      |
| **5: Laatste Woonplaats (Last Residence)** | `laatst gewoond te`                   | Checks if line contains "laatst gewoond te"           | `laatst\s*gewoond te\s+(.+)`               | Text after "laatst gewoond te" (Last Residence)       |
| **6: Campaigns**                           | `4-digit year followed by place name` | Checks if starts with 4 digit and followed by strings | `\b(\d{4})\s+([a-zA-Z]+[\sa-zA-Z]*)`       | 4 digit as Year, string as place                      |
| **7: Military Postings**                   | `more than 1 date pattern`            | Checks if strings has more than one date patterns     | `.*?[0-9]{1,2}\s[A-Z]+[a-z]*\s[1-9]{4}\.*` | String before the date as Context, date as Event Date |


