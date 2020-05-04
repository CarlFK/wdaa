# wdaa.py
# WikiData Address Adder
# adds things with addresses, tries to avoid dupes based on lat/lng

import re
import urllib.parse

from pprint import pprint
from time import sleep

import geocoder

import gspread

from googsheet import goog_sheet, v_to_ld

from wd import hospi_ll

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

    sheet = sheets['ilppe']
    ssid = sheet['ssid']
    cells = sheet['cells']
    rows = goog_sheet(ssid, cells)
    # print(rows[0].keys())

    row = rows[0]
    # pprint(row)

    return rows


def demo_addr():
    # addr = '1620 W. Harrison St. Chicago, IL 60612'
    # no find: "2070 N, IL-50, Suite 500, Bourbonnais, IL 60914"
    addr = "2070 N, IL-50, Bourbonnais, IL 60914"
    ll = addr_to_latlng(addr)
    print(ll)


def what_am_i(rows):

    def one(row):

        pprint(row)

        query = urllib.parse.quote(
            '{Medical Center Name} "{Region}"'.format(**row))
        goog = "https://google.com/#q={}".format(query)

        query = urllib.parse.quote(
            "{Medical Center Name}".format(**row))
        wp = "https://en.wikipedia.org/wiki/Special:Search?search={}".format(query)

        res = hospi_ll(row['lat'], row['lng'])

        print("[{Region}] {Medical Center Name}\n{goog}\n{wp}\n".format(
            goog=goog, wp=wp, **row))

        for wd in res['results']['bindings']:
            if row['Medical Center Name'] == wd['placeLabel']['value']:
                print("hit: " + wd['place']['value'])


    print()
    for row in rows:
        if "Hospital" in row['Medical Center Name']:
            continue
        if "Chicago" != row['Region']:
            continue
        # one(row)
        if "Chicago" in row['Address']:
            continue
        # one(row)

    print()
    for row in rows:
        if "Hospital" in row['Medical Center Name']:
            continue
        if "Chicago" != row['Region']:
            continue
        # one(row)

    print()
    for row in rows:
        if "Hospital" not in row['Medical Center Name']:
            continue
        if "Chicago" != row['Region']:
            continue
        if row['wikidata']:
            continue
        one(row)
        break


def ray():

    sheet = sheets['ray-copy']
    ssid = sheet['ssid']
    cells = sheet['cells']
    rows = goog_sheet(ssid, cells)
    for row in rows:
        print(row['Medical Center Name'])


def test():

    # c19it()

    # demo_addr()
    rows = ilppe()
    what_am_i(rows)
    # all_addrs_to_ll( rows )
    # ray()



def main():
    test()

if __name__ == '__main__':
    main()
