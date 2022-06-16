from neomodel import config
from models.simple_graph import *
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, classification_report, roc_auc_score, confusion_matrix


def run(csv_path):
    X = []
    y = []

    with open(csv_path) as mimic_data:
        num_lines = 0
        for line in mimic_data:
            num_lines += 1

    with open(csv_path) as mimic_data:
        i = 0
        for line in tqdm(mimic_data, total=num_lines, desc="Load MIMIC data..."):
            i += 1
            entry = line.strip().replace('"', "").split(",")
            
            if i == 1:
                continue

            visit_id = entry[0]
            los = float(entry[6])
            los_over = entry[5]

            visit = Visit.nodes.get(visit_id = visit_id)

            X.append(visit.embedding)
            y.append(los_over)


    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42)

    clf = RandomForestClassifier(
        random_state=42,
        min_samples_leaf=2,
        bootstrap=True,
        max_samples=0.8
    )

    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()

    print("AUC:", roc_auc_score(y_test, clf.predict_proba(X_test)[:,1]))

    print("\n")
    print(f"TN: {tn} TP: {tp} FN: {fn} FP: {fp}")
    print("\n")
    print(classification_report(y_test, y_pred, target_names=["LOS<6", "LOS>6"]))