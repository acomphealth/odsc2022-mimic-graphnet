from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, classification_report, roc_auc_score, confusion_matrix
from sklearn import preprocessing
import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None 


def run(csv_path):
    # reading mimic CSV data
    df = pd.read_csv(csv_path)
    y = df["los6"]
    X = df.loc[:, ~df.columns.isin(["visit_occurrence_id","los6","my_los"])]

    # encoding all the ordinal variables (i.e., gender, care site, race, age)
    encoder = preprocessing.OrdinalEncoder()
    X[["gender", "care_site_source_value", "myrace", "myage"]] = encoder.fit_transform(
        X[["gender", "care_site_source_value", "myrace", "myage"]]
    )

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

    # predictions
    y_pred = clf.predict(X_test)

    # print stats
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()

    print("AUC:", roc_auc_score(y_test, clf.predict_proba(X_test)[:,1]))

    print("\n")
    print(f"TN: {tn} TP: {tp} FN: {fn} FP: {fp}")
    print("\n")
    print(classification_report(y_test, y_pred, target_names=["LOS<6", "LOS>6"]))