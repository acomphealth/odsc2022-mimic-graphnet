def train(gds, lr=0.01):
    print("Removing exisitng embeddings and model")
    gds.run_cypher("MATCH (a) REMOVE a.embedding")
    exists = bool(gds.graph.exists("mimic")["exists"])
    if exists:
        G = gds.graph.get("mimic")
        gds.graph.drop(G)
    try:
        model = gds.model.get("mimicModel")
        if model.exists():
            model.drop()
    except Exception as ex:
        pass

    print("Creating projected graph")
    G, _ = gds.graph.project(
        'mimic',
        ['Visit', 'Sex', 'Race', 'Diagnosis', 'CareSite', 'Age'],
        ['age_at_visit', 'has_medical_hx', 'has_parent_dx', 'of_sex', 'visit_race', 'visit_site'],
        nodeProperties=["degree"]
    )

    print("Training GraphSAGE")
    model, _ = gds.beta.graphSage.train(
        G,
        modelName = "mimicModel",
        learningRate = lr,
        epochs = 100,
        featureProperties = ["degree"]
    )

    print(model.metrics())

    gds.beta.graphSage.write(
        G,
        writeProperty='embedding',
        modelName='mimicModel'
    )
