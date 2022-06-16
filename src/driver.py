from neomodel import config
from neograph import simple_load
from graphdatascience import GraphDataScience
from ai import add_graph_properties, eval_forest_features, eval_forest_network, train_sage
import getpass


csv_path = input("Enter path to preprocessed data: ")
username = input("Neo4J username (eg, neo4j): ")
password = getpass.getpass("Neo4J password: ")
host = input("Neo4J Hostname (eg, localhost): ")
database = input("Neo4J Database (eg, neo4j): ")
port = "7687"

config.DATABASE_URL = f"bolt://{username}:{password}@{host}:{port}/{database}"

job = input("What job? ").lower()

if job == "load":
    simple_load.SimpleGraph().run_import(csv_path)
elif job == "feature":
    eval_forest_features.run(csv_path)
elif job == "network":
    eval_forest_network.run(csv_path)
else:
    gds = GraphDataScience(f"bolt://{host}:{port}", auth=(username, password))
    gds.set_database(database)

    if job == "prop":
        add_graph_properties.add_properties(gds)
    elif job == "sage":
        train_sage.train(gds)
    elif job == "tune":
        lrs = [0.005, 0.01, 0.05, 0.1, 0.2]
        for lr in lrs:
            train_sage.train(gds, lr)
            print(f"Evaluating LR of {lr}:")
            eval_forest_network.run(csv_path)