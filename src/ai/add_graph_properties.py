####################################################
# Function to add graph computed properties to the 
# graph model. Need at least 1 numeric property to
# include in GraphSAGE - this provides a graph-
# realted metric based on connectedness of each
# node
####################################################

def add_properties(gds):
    # Check if we've built the projection before using GDS
    exists = bool(gds.graph.exists("mimic")["exists"])

    # If we have, drop it - could do this more selectively, but it builds quickly 
    # at this so can just drop the full projection as well as previously computed
    # properties and relationships with cypher
    if exists: 
        G = gds.graph.get("mimic")
        gds.graph.drop(G)

    gds.run_cypher("MATCH (a) REMOVE a.degree") # Property for GDS-computed degree
    gds.run_cypher("MATCH (a) REMOVE a.embedding") # Property for GraphSAGE embedding

    # Now we create a projection so we can compute and write the degree property
    # Not the most elegant approach, but easy try/catch to handle either the
    # graph with ICD9 hierarchy or the one without (no "has_parent_dx" relationship)
    G = None
    try:
        G, _ = gds.graph.project(
            'mimic',
            ['Visit', 'Sex', 'Race', 'Diagnosis', 'CareSite', 'Age'],
            ['age_at_visit', 'has_medical_hx', 'has_parent_dx', 'of_sex', 'visit_race', 'visit_site']
        )
    except Exception as ex:
        G, _ = gds.graph.project(
            'mimic',
            ['Visit', 'Sex', 'Race', 'Diagnosis', 'CareSite', 'Age'],
            ['age_at_visit', 'has_medical_hx', 'of_sex', 'visit_race', 'visit_site']
        )

    try:
        gds.degree.write( # Compute and write the degree for each node in the graph
            G,
            writeProperty="degree"
        )
    except Exception as ex:
        raise ex