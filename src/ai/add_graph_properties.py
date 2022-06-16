def add_properties(gds):
    exists = bool(gds.graph.exists("mimic")["exists"])
    if exists:
        G = gds.graph.get("mimic")
        gds.graph.drop(G)

    gds.run_cypher("MATCH ()-[r:SIMILAR]-() DELETE r")
    gds.run_cypher("MATCH (a) REMOVE a.degree")
    gds.run_cypher("MATCH (a) REMOVE a.embedding")

    G, _ = gds.graph.project(
        'mimic',
        ['Visit', 'Sex', 'Race', 'Diagnosis', 'CareSite', 'Age'],
        ['age_at_visit', 'has_medical_hx', 'has_parent_dx', 'of_sex', 'visit_race', 'visit_site']
    )

    try:
        mutate = gds.degree.write(
            G,
            writeProperty="degree"
        )
    except Exception as ex:
        raise ex