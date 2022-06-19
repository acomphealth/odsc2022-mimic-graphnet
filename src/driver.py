#####################################################
# Driver application to load formatted or generated
# CSV data into Neo4J, add computed properties, and
# train/evaluate model performance for LOS prediction
# task.
#####################################################

import getpass

from graphdatascience import GraphDataScience
from neomodel import config

from ai import (add_graph_properties, eval_forest_features,
                eval_forest_network, train_sage)
from neograph import simple_load

csv_path = input("Enter path to preprocessed data: ")
username = input("Neo4J username (eg, neo4j): ")
password = getpass.getpass("Neo4J password: ")
host = input("Neo4J Hostname (eg, localhost): ")
database = input("Neo4J Database (eg, neo4j): ")
port = "7687"

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
