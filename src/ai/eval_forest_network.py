####################################################
# Function to train and evaluate a random forest
# using MIMIC or generated data based on GraphSAGE
# embeddings to predict whether a visit will have a
# length of stay <6 days vs >=6 days. sklearn 
# ordinal encoder for appropriate variables.
# Source data file used to get list of visits and
# and ground truth label.
####################################################

from models.simple_graph import *
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (classification_report, confusion_matrix,
                             roc_auc_score)
from sklearn.model_selection import train_test_split
from tqdm import tqdm


def run(csv_path):
    X = []
    y = []

    # Count number of lines in file for TQDM
    with open(csv_path) as mimic_data:
        num_lines = 0
        for line in mimic_data:
            num_lines += 1

    with open(csv_path) as mimic_data:
        i = 0
        for line in tqdm(mimic_data, total=num_lines, desc="Load data from input file..."):
            i += 1
            entry = line.strip().replace('"', "").split(",")
            
            if i == 1:
                continue

            # Get visit ID and LOS label
            visit_id = entry[0]
            los_over = entry[5]

            # Get visit node from Neo4j so we can get the embedding
            visit = Visit.nodes.get(visit_id = visit_id)

            # Add embedding and label to lists
            X.append(visit.embedding)
            y.append(los_over)


    # splitting 80:20
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # training RF
    clf = RandomForestClassifier(
        random_state=42,
        min_samples_leaf=2,
        bootstrap=True,
        max_samples=0.8
    )
    clf.fit(X_train, y_train)

    # create predictions from test split
    y_pred = clf.predict(X_test)

    # print stats
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()

    print("AUC:", roc_auc_score(y_test, clf.predict_proba(X_test)[:,1]))

    print("\n")
    print(f"TN: {tn} TP: {tp} FN: {fn} FP: {fp}")
    print("\n")
    print(classification_report(y_test, y_pred, target_names=["LOS<6", "LOS>6"]))
