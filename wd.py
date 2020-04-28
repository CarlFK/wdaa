# wd.py

# WikiData things

from pprint import pprint

from qwikidata.entity import WikidataItem, WikidataLexeme, WikidataProperty
from qwikidata.linked_data_interface import get_entity_dict_from_api

from qwikidata.sparql import (get_subclasses_of_item,
                              return_sparql_query_results)

# SELECT ?item WHERE { ?item rdfs:label "hospital"@en. }

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

    # print("import sys; sys.exit()"); import code; code.interact(local=locals())


def tag_qs():
    tags = """
Hospital
psychiatric hospital
rehabilitation hospital
Urgent care
Nursing homes
Doctor office
Dentist office
fire station
EMT
Food pantries
Post office
"""

    for tag in tags.split('\n'):
        if not tag:
            continue
        print(tag)
        q(tag)

def main():
    # q("Hospital")
    tag_qs()

if __name__ == '__main__':
    main()
