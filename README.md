# Repository Overview

The code in this repository can be used to generate synthetic data or use appropriately formatted data from MIMIC III to populate a graph network in Neo4J and train/evaluate a random forest model for length-of-stay (LOS) prediction. Additional background information can be found in the slides from the Open Data Science Conference (ODSC) Europe 2022 presentation "Healthcare Predictive Modeling with Graph Networks". The slides are in the 'docs' directory and code is in the 'src' directory.

# Running the Code

To generate, load, and evaluate data, first create a Python 3.9 virtual enivornment and install the needed libraries from requirements.txt. An accessible Neo4J database is a requirement. Execute the scripts from the parent directory to generate data and run the driver application.

## Generate data
```
python src/generate_data.py
```

## Load data into Neo4J, train and evaluate models
```
python src/driver.py
```

The script will prompt for the CSV input file (from the generated output or equivalently formatted data), Neo4J connection parameters, and what step of the workflow is being run: load data, compute properties, train GraphSAGE, or train/evaluate a random forest based on either tabular or embedded data. Additional details can be found in the code comments.