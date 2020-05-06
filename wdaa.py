# wdaa.py
# WikiData Address Adder
# adds things with addresses, tries to avoid dupes based on lat/lng

import re
import urllib.parse

from pprint import pprint
from time import sleep

import geocoder

import gspread

from googsheet import v_to_ld

from wd import q, hospi_ll

try:
    from api_keys import sheets
except ModuleNotFoundError:
    # you can't ahve my secrets, but here is a start
    from googsheet import sheets

def addr_fixer(addr):

    # print(addr)
    addr_re = re.compile(r"(?P<name>[^\d]*)(?P<address>.*)", re.DOTALL)
    d = addr_re.match(addr).groupdict()
    # print(d)

    return d['address']


def addr_to_latlng(addr):

    # https://geocoder.readthedocs.io/providers/OpenStreetMap.html#osm-addresses
    print(addr)

    g = geocoder.osm(addr)
    sleep(1)

    j = g.json
    latlng = j['lat'], j['lng']

    return latlng

def all_addrs_to_ll( rows ):

    for row in rows:

        if row['Address'] is None or len(row['Address']) == 0:
            continue

        if row['lat']:
            continue

        # pprint(row)
        if row['fixed address']:
            addr = row['fixed address']
        else:
            addr = addr_fixer( row['Address'] )

        latlng = addr_to_latlng( addr )
        print(latlng)


def c19it():

    # gc = gspread.service_account()
    gc = gspread.oauth()

    sh = gc.open("Copy of COVID-19 INVENTORY TRACKER - CHICAGO")

    worksheet = sh.worksheet("Requesters")

    # ['Medical Center Name', 'Email Address', '', 'Region', 'Primary Contact', 'Address', 'fixed address', 'lat', 'lng', 'homepage url', 'location url', 'wikipedia url', 'Phone', 'Product Needs', 'Immediate Need - ready for order', 'How to get it to them']

    # keys = worksheet.get('A2:R2')[0]
    # cell.row, cell.col
    values = worksheet.get_all_values()

    # lists of dicts
    rows = v_to_ld(values, 1)

    for row in rows:
        if row['lng']:
            continue

        if row['Address'] is None or len(row['Address']) == 0:
            continue

        if row['fixed address']:
            addr = row['fixed address']
        else:
            addr = addr_fixer( row['Address'] )

        latlng = addr_to_latlng( addr )

        worksheet.update('H{row}:I{row}'.format(**row), [latlng])


def ilppe():

    gc = gspread.oauth()
    sh = gc.open("Copy of COVID-19 INVENTORY TRACKER - CHICAGO")
    worksheet = sh.worksheet("Requesters")
    values = worksheet.get_all_values()
    rows = v_to_ld(values, 1)

    what_am_i(rows)

    # return rows

def db_hospis():

    # get raw data
    with open("db_hospis.txt") as f:
        lines = []
        for line in f:
            line = line.strip()
            if line:
                lines.append(line)

    for line in lines:
        print(line)
        res = q(line)
        print("------------\n")



def db():

    # get raw data
    with open("db.txt") as f:
        lines = []
        for line in f:
            line = line.strip()
            if line:
                lines.append(line)

    # dig out hositals
    hospis=set()
    for line in lines:
        if "hosp" in line.lower():
            hospis.update([line])

        # words = line.split()
        # print(words)
        # for word in words:
        #    if "hosp" in word.lower():
        #        hospis.update(line)

    # pprint(hospis)

    for hospi in hospis:
        print(hospi)


    return lines


def chg():
    # "Chicago Hospitals_Geocoded"

    gc = gspread.oauth()
    sh = gc.open("Chicago Hospitals_Geocoded")
    worksheet = sh.worksheet("Sheet1")
    values = worksheet.get_all_values()
    rows = v_to_ld(values, 0)

    import code; code.interact(local=locals())

    return rows


def demo_addr():
    # addr = '1620 W. Harrison St. Chicago, IL 60612'
    # no find: "2070 N, IL-50, Suite 500, Bourbonnais, IL 60914"
    addr = "2070 N, IL-50, Bourbonnais, IL 60914"
    ll = addr_to_latlng(addr)
    print(ll)


def what_am_i(rows):

    def one(row):

        # Item from spreadsheet
        # pprint(row)

        query = urllib.parse.quote(
            '{Medical Center Name} "{Region}"'.format(**row))
        goog = "https://google.com/#q={}".format(query)

        query = urllib.parse.quote(
            "{Medical Center Name}".format(**row))
        wp = "https://en.wikipedia.org/wiki/Special:Search?search={}".format(query)

        print("{row} {Medical Center Name}\n".format(
            goog=goog, wp=wp, **row))

        """
        print("[{Region}] {Medical Center Name}\n{goog}\n{wp}\n".format(
            goog=goog, wp=wp, **row))
        """

        # Look for it in WikiData

        isa = "Q16917" if row['isa'] == 'hospital' else ''
        res = hospi_ll(row['lat'], row['lng'], .4, isa )

        for wd in res['results']['bindings']:
            print( "{} {} {} {}".format(
                wd['distance']['value'],
                wd['placeLabel']['value'],
                wd['place']['value'], wd['place']['value'].split('/')[-1]
                ))
            if row['Medical Center Name'] == wd['placeLabel']['value']:
                print("hit!")
                import code; code.interact(local=locals())
        print("----------\n")

    print()
    for row in rows[104:]:
        # pprint(row)
        if "Hospital" not in row['Medical Center Name'] and \
            row['Region'] == "Chicago" and \
            not row['wikidata'] and \
            row['isa'] != 'hospital':
                one(row)


def test():

    # c19it()

    # demo_addr()
    # all_addrs_to_ll( rows )

    # rows = ilppe()
    # rows = chg()
    db_hospis()


def main():
    test()

if __name__ == '__main__':
    main()
