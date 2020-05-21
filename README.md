# wdaa
WikiData Address Adder

Mine various databases to locate health care facilities.
Use Open Street Map AIP to geocode 
use WikiData.org SPARQL queries to identify duplicates based on location, two entities within 100 meters are likely the same facility.
Use google spreadsheets as the UI to review ananysis.


Install:

1. python3 -m venv venv
1. . venv/bin/activate
1. pip install -r requirements.txt

To access private data sources:

1. https://developers.google.com/sheets/api/quickstart/python#step_1_turn_on_the
1. click the blue button
1. download credentials.json 
1. mv ~/Downloads/credentials.json .
