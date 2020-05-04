# wd.py
# WikiData things

import csv
from pprint import pprint

from qwikidata.entity import WikidataItem, WikidataLexeme, WikidataProperty
from qwikidata.linked_data_interface import get_entity_dict_from_api

from qwikidata.sparql import (get_subclasses_of_item,
                              return_sparql_query_results)


def hospi_ll(lat,lng):

    sparql_query = """
    SELECT ?place ?placeLabel ?geo WHERE {{
  ?place wdt:P31/wdt:P279* wd:Q16917;  # Hospitals
         wdt:P17 wd:Q30;            # In US
 SERVICE wikibase:around {{
      ?place wdt:P625 ?location .
      bd:serviceParam wikibase:center"Point({lng} {lat})"^^geo:wktLiteral.
      bd:serviceParam wikibase:radius ".5" .
      bd:serviceParam wikibase:distance ?distance .
    }}
 SERVICE wikibase:label {{
 bd:serviceParam wikibase:language "en" .
 }}
}}""".format(lat=lat,lng=lng)

    res = return_sparql_query_results(sparql_query)

    # pprint(res['results']['bindings'])

    for row in res['results']['bindings']:
        print(row['place']['value'])
        print(row['placeLabel']['value'])
        print()

    return res

    print("import sys; sys.exit()"); import code; code.interact(local=locals())


def q(word):

    sparql_query = """
SELECT ?item ?itemLabel ?itemDescription WHERE {{
    SERVICE wikibase:mwapi {{
      bd:serviceParam wikibase:endpoint "www.wikidata.org";
                      wikibase:api "EntitySearch";
                      mwapi:search "{word}";
                      mwapi:language "en";
                      mwapi:limit "1".
      ?item wikibase:apiOutputItem mwapi:item.
      ?num wikibase:apiOrdinal true.
  }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}}""".format(word=word)

    # print(sparql_query)

    res = return_sparql_query_results(sparql_query)
    # pprint(res)
    for item in res['results']['bindings']:
        # pprint(item)
        # print(item['itemLabel']['value'])
        # print(item['itemDescription']['value'])
        # print(item['item']['value'])
        print("{label}: {description} {uri}\n".format(
            label=item['itemLabel']['value'],
            description=item['itemDescription']['value'],
            uri=item['item']['value']))


def tag_qs():
    tags = """
Doctor office
Dentist office
Food pantry
Post office
"""

    with open("tags.csv") as csvfile:
        rows = list(csv.DictReader(csvfile))

    d = {}
    for row in rows:
        d[row['label']] = row

    for k in d:
        print("{label}: {description} https://www.wikidata.org/wiki/{id}\n".format(**d[k]))

    for tag in tags.split('\n'):
        if not tag:
            continue
        if tag in d:
            continue

        print(tag)
        # q(tag)

def test():
    # random bits of code to test other bits of code.

    # q("Hospital")
    # q("Urgent Care Clinic")
    # q("Nursing Home")
    # tag_qs()

    # hospi_ll(41.89498135,-87.62153624)
    hospi_ll(41.79027035,-87.60458343)

    # print("import sys; sys.exit()"); import code; code.interact(local=locals())


def main():
    test()

if __name__ == '__main__':
    main()
