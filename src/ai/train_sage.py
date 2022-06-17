####################################################
# Function to train GraphSAGE using GDS library
####################################################

def train(gds, lr=0.01):
    # Remove existing embeddings if they exist
    print("Removing exisitng embeddings and model")
    gds.run_cypher("MATCH (a) REMOVE a.embedding")

    # Now check if the projection exists, if it does
    # delete it
    exists = bool(gds.graph.exists("mimic")["exists"])
    if exists:
        G = gds.graph.get("mimic")
        gds.graph.drop(G)

    try: # And the same for prior GraphSAGE models
        model = gds.model.get("mimicModel")
        if model.exists():
            model.drop()
    except Exception as ex:
        pass

    # Recreate the projection and include computed properties
    print("Creating projected graph")
    G, _ = gds.graph.project(
        'mimic',
        ['Visit', 'Sex', 'Race', 'Diagnosis', 'CareSite', 'Age'],
        ['age_at_visit', 'has_medical_hx', 'has_parent_dx', 'of_sex', 'visit_race', 'visit_site'],
        nodeProperties=["degree"]
    )

    # Train GraphSAGE using GDS. Many other parameters that can be
    # tuned in GraphSAGE - using defaults except for learning rate and
    # number of epochs. Use the computed degree property from 
    # add_graph_properties.py as the feature property.
    print("Training GraphSAGE")
    model, _ = gds.beta.graphSage.train(
        G,
        modelName = "mimicModel",
        learningRate = lr,
        epochs = 100,
        featureProperties = ["degree"]
    )

    # Print metrics and write individual node embeddings back to Neo4J for later use
    print(model.metrics())

    gds.beta.graphSage.write(
        G,
        writeProperty='embedding',
        modelName='mimicModel'
    )
