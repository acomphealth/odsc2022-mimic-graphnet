####################################################
# neomodel models to reprsent the LOS data in Neo4J
####################################################

from neomodel import (ArrayProperty, RelationshipFrom, RelationshipTo,
                      StringProperty, FloatProperty, StructuredNode)


class Visit(StructuredNode):
    visit_id = StringProperty(unique_index=True)
    embedding = ArrayProperty()

    sex = StringProperty()
    race = StringProperty()
    age = StringProperty()

    #sex = RelationshipTo("Sex", "of_sex")
    care_site = RelationshipTo("CareSite", "visit_site")
    #race = RelationshipTo("Race", "visit_race")
    #age = RelationshipTo("Age", "age_at_visit")

    dx = RelationshipTo("Diagnosis", "has_medical_hx")


class Diagnosis(StructuredNode):
    icd = StringProperty(unique_index=True)
    embedding = ArrayProperty()

    child_dx = RelationshipFrom("Diagnosis", "has_parent_dx")
    parent_dx = RelationshipTo("Diagnosis", "has_parent_dx")
    visits = RelationshipFrom("Visit", "has_medical_hx")


# class Age(StructuredNode):
#     label = StringProperty(unique_index=True)
#     embedding = ArrayProperty()

#     visits = RelationshipFrom("Visit", "age_at_visit")


# class Race(StructuredNode):
#     label = StringProperty(unique_index=True)
#     embedding = ArrayProperty()

#     visits = RelationshipFrom("Visit", "visit_race")


# class Sex(StructuredNode):
#     label = StringProperty(unique_index=True)
#     embedding = ArrayProperty()

#     visits = RelationshipFrom("Visit", "of_sex")


class CareSite(StructuredNode):
    site_id = StringProperty(unique_index=True)
    embedding = ArrayProperty()

    visits = RelationshipFrom("Visit", "visit_site")
