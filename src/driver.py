#####################################################
# Driver application to load formatted or generated
# CSV data into Neo4J, add computed properties, and
# train/evaluate model performance for LOS prediction
# task.
#####################################################

import getpass

from graphdatascience import GraphDataScience
from neomodel import config
import os
import json
import random

from ai import (add_graph_properties, eval_forest_features,
                eval_forest_network, train_sage)
from neograph import simple_load

csv_path = None
username = None
password = None
host = None
database = None
port = None

if os.path.exists("data/config.json"):
    with open("data/config.json") as config_file:
        config_data = json.loads(config_file.read())
        if "csv_path" in config_data:
            csv_path = config_data["csv_path"]
        if "username" in config_data:
            username = config_data["username"]
        if "password" in config_data:
            password = config_data["password"]
        if "host" in config_data:
            host = config_data["host"]
        if "database" in config_data:
            database = config_data["database"]
        if "port" in config_data:
            port = config_data["port"]

if csv_path is None:
    csv_path = input("Enter path to preprocessed data: ")
if username is None:
    username = input("Neo4J username (eg, neo4j): ")
if password is None:
    password = getpass.getpass("Neo4J password: ")
if host is None:
    host = input("Neo4J Hostname (eg, localhost): ")
if port is None:
    port = "7687"
if database is None:
    database = input("Neo4J Database (eg, neo4j): ")

# This sets the connection string using the neomodel library
config.DATABASE_URL = f"bolt://{username}:{password}@{host}:{port}/{database}"

job = input("What job? ").lower()

if job == "loadnorel": # Load from the processed data into neo4j without dx code relationships
    simple_load.SimpleGraph().run_import(csv_path)
elif job == "loadrel": # Load from the processed data into neo4j with dx code relationships
    simple_load.SimpleGraph().run_import(csv_path, import_dx_rel=True)
elif job == "feature": # Run performance evaluation on tabular data using a random forest
    eval_forest_features.run(csv_path)
elif job == "network": # Run performance evaluation on network data using a random forest
    eval_forest_network.run(csv_path)
else: # Otherwise load GraphDataScience to add network properties and train GraphSAGE
    gds = GraphDataScience(f"bolt://{host}:{port}", auth=(username, password))
    gds.set_database(database)

    if job == "prop": # Add computed properties to graph
        add_graph_properties.add_properties(gds)
    elif job == "sage": # Train GraphSAGE
        train_sage.train(gds)
    elif job == "tune": # Test multiple learning rates on GraphSAGE+random forest
        lrs = [0.005, 0.01, 0.05, 0.1, 0.2]
        for lr in lrs:
            train_sage.train(gds, lr)
            print(f"Evaluating LR of {lr}:")
            eval_forest_network.run(csv_path)
    elif job == "replicate":
        aucs = []
        for a in range(0,10):
            gds = GraphDataScience(f"bolt://{host}:{port}", auth=(username, password))
            gds.set_database(database)
            train_sage.train(gds, lr=0.1, seed=random.randint(0,20000000))
            auc = eval_forest_network.run(csv_path, seed=random.randint(0,20000000))
            aucs.append(auc)
        print(f"Database used: {database}")
        print(aucs)