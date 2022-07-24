####################################################
# Load formatted data from CSV into Neo4J using OGM
# (neomodel). Individiuals models defined in:
# models.simple_graph
####################################################

import json
import os

from models.simple_graph import *
from tqdm import tqdm


class SimpleGraph:
    def run_import(self, csv_path, import_dx_rel = False):
        try:
            if import_dx_rel:
                if not os.path.exists("resources/icd9_categories.json"):
                    # https://raw.githubusercontent.com/sirrice/icd9/master/codes_pretty_printed.json
                    # and save as resources/icd9_categories.json
                    print("Please download ICD9 diagnosis and group list per code comments")
                    exit()
                    
                with open('resources/icd9_categories.json') as icd_file:
                    data = json.load(icd_file)
                    for record_group in tqdm(data, total=len(data), desc="Loading dx data..."):
                        last = None
                        for record in record_group:
                            if record['code'] is None or len(record['code']) < 1:
                                continue

                            cur_icd = record['code'].replace('.', '')
                            cur_dx = Diagnosis.get_or_create(
                                {
                                    "icd": cur_icd
                                }
                            )

                            if last is not None:
                                cur_dx[0].parent_dx.connect(last[0])
                            last = cur_dx

            # Count number of lines for use in TQDM
            num_lines = 0
            with open(csv_path) as mimic_data:
                for line in mimic_data:
                    num_lines += 1

            # Reopen file for processing
            with open(csv_path) as mimic_data:
                header = []

                i = 0
                for line in tqdm(mimic_data, total=num_lines, desc="Loading data..."):
                    i += 1
                    # Strip newlines, remote quotes from strings, and split CSV
                    entry = line.strip().replace('"', "").split(",")
                    
                    # Get field names from header
                    if i == 1:
                        header = entry
                        continue # Since header, now move on to read/process data
                    
                    # When a data row, get variables and add to Neo4J via neomodel
                    visit_id = entry[0]
                    sex = entry[1]
                    care_site = entry[2]
                    race = entry[3]
                    age = entry[4]

                    # sex_node = Sex.get_or_create(
                    #     {
                    #         "label": sex.lower()
                    #     }
                    # )
                    care_site_node = CareSite.get_or_create(
                        {
                            "site_id": str(care_site).lower()
                        }
                    )
                    # race_node = Race.get_or_create(
                    #     {
                    #         "label": race.lower()
                    #     }
                    # )
                    # age_node = Age.get_or_create(
                    #     {
                    #         "label": age.lower()
                    #     }
                    # )
                    visit_node = Visit.create_or_update(
                        {
                            "visit_id": str(visit_id).lower(),
                            "age": age.lower(),
                            "race": race.lower(),
                            "sex": sex.lower()
                        }
                    )
                    
                    # Connect each of the data elements to the visit node
                    visit_node[0].care_site.connect(care_site_node[0])
                    # visit_node[0].sex.connect(sex_node[0])
                    # visit_node[0].race.connect(race_node[0])
                    # visit_node[0].age.connect(age_node[0])

                    # Add diagnosis nodes and connect to the visit
                    for z in range(7, len(header)):
                        if entry[z] == "1" or entry[z] == 1:
                            icd9 = header[z].replace(".", "")
                            cur_dx = Diagnosis.get_or_create(
                                        {
                                            "icd": icd9
                                        }
                                    )
                            visit_node[0].dx.connect(cur_dx[0])

        except Exception as ex:
            print(ex)
