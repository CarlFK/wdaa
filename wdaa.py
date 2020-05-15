# wdaa.py
# WikiData Address Adder
# adds things with addresses, tries to avoid dupes based on lat/long

import re
import urllib.parse

from pprint import pprint
from time import sleep

import geocoder

import gspread

from googsheet import v_to_ld

from wd import label, hospi_ll

try:
    from api_keys import sheets
except ModuleNotFoundError:
    # you can't ahve my secrets, but here is a start
    from googsheet import sheets


def goog_search(query):

    goog_q = urllib.parse.quote(query)
    url = "https://google.com/#q={}".format(goog_q)
    return url


def addr_fixer(addr):

    # print(addr)
    addr_re = re.compile(r"(?P<name>[^\d]*)(?P<address>.*)", re.DOTALL)
    d = addr_re.match(addr).groupdict()
    # print(d)

    return d['address']


def addr_to_latlong(addr):

    # https://geocoder.readthedocs.io/providers/OpenStreetMap.html#osm-addresses
    # print(addr)

    g = geocoder.osm(addr)
    sleep(1)

    j = g.json
    latlong = j['lat'], j['lng']

    return latlong

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

        latlong = addr_to_latlong( addr )
        print(latlong)


def c19it():

    # gc = gspread.service_account()
    gc = gspread.oauth()

    sh = gc.open("Copy of COVID-19 INVENTORY TRACKER - CHICAGO")

    worksheet = sh.worksheet("Requesters")

    # ['Medical Center Name', 'Email Address', '', 'Region', 'Primary Contact', 'Address', 'fixed address', 'lat', 'long', 'homepage url', 'location url', 'wikipedia url', 'Phone', 'Product Needs', 'Immediate Need - ready for order', 'How to get it to them']

    # keys = worksheet.get('A2:R2')[0]
    # cell.row, cell.col
    values = worksheet.get_all_values()

    # lists of dicts
    keys,rows = v_to_ld(values, 1)

    for row in rows:
        if row['long']:
            continue

        if row['Address'] is None or len(row['Address']) == 0:
            continue

        if row['fixed address']:
            addr = row['fixed address']
        else:
            addr = addr_fixer( row['Address'] )

        latlong = addr_to_latlong( addr )

        worksheet.update('H{row}:I{row}'.format(**row), [latlong])


def ilppe_get():

    gc = gspread.oauth()
    sh = gc.open("Copy of COVID-19 INVENTORY TRACKER - CHICAGO")
    worksheet = sh.worksheet("Requesters")
    values = worksheet.get_all_values()
    keys,rows = v_to_ld(values, 1)

    return rows

def db_hospis():

    gc = gspread.oauth()
    sh = gc.open("d data")
    worksheet = sh.worksheet("cooked")
    values = worksheet.get_all_values()
    keys,rows = v_to_ld(values, 0)

    ilppes = ilppe_get()

    for row in rows:

        if not row['wikidata'] and \
                row['isa'] == 'hospital' and \
                row['name'] not in [
                    ilppe['Medical Center Name'] for ilppe in ilppes]:

            print(row['row'],row['name'])

            goog_q = urllib.parse.quote(row['name'])
            print("https://google.com/#q={}".format(goog_q))

            isa = "Q16917" if row['isa'] == 'hospital' else ''
            res = label(row['name'], isa)
            if len(res['results']['bindings']):
                cell=worksheet.cell(row['row'], keys.index('wikidata'))
                wd_id = res['results']['bindings'][0]['item']['value'].split('/')[-1]
                print('worksheet.update( {}, "{}")'.format(
                    cell.address,
                    wd_id))
            print("------------\n")

            import code; code.interact(local=locals())

            break



def chl():
    sn = "Chicago Hospital Location.csv"
    ws_name = "Sheet1"

    gc = gspread.oauth()
    sh = gc.open(sn)
    worksheet = sh.worksheet(ws_name)
    values = worksheet.get_all_values()
    keys,rows = v_to_ld(values, 0)

    rows = [row for row in rows if not row['lat']]

    # fill in lat,long
    for row in rows:
        print("-------\n{Hospital} - {Street Address}\n".format(**row))

        full_addr = "{Street Address}, {City} IL, {Zip Code}".format(**row)
        try:
            latlong = addr_to_latlong( full_addr )
            # lat,long is G,H
            worksheet.update('G{row}:H{row}'.format(**row), [latlong])

        except TypeError:
            # print( "{Hospital}\n{Street Address}".format(**row) )

            isas = ["Q16917", "Q4287745"]  # hospital,  medical organization
            res = label(row['Hospital'], isas)

            query = "{Hospital} {City}".format(**row)
            print( goog_search(query))
            import code; code.interact(local=locals())


        """
        isas = ["Q16917", "Q4287745"]  # hospital,  medical organization
        res = hospi_ll( row['Y'], row['X'], .2, isas=isas)

        for wd in res['results']['bindings']:
            if row['FACILITY'] == wd['placeLabel']['value']:
                print( "match: ", wd['place']['value'] )
                break
            else:
                print( wd['distance']['value'],
                    wd['placeLabel']['value'],
                    wd['place']['value'],
                    # wd['place']['value'].split('/')[-1]
                    )
        print("----------")
        # break
        """


    return rows


def chg():
    sn = "Chicago Hospitals_Geocoded"
    ws_name = "Sheet1"

    gc = gspread.oauth()
    sh = gc.open(sn)
    worksheet = sh.worksheet(ws_name)
    values = worksheet.get_all_values()
    keys,rows = v_to_ld(values, 0)

    for row in rows:
        print("{FACILITY} - {StAddr} {City}\n".format(**row))
        isas = ["Q16917", "Q4287745"]  # hospital,  medical organization
        res = hospi_ll( row['Y'], row['X'], .2, isas=isas)

        for wd in res['results']['bindings']:
            if row['FACILITY'] == wd['placeLabel']['value']:
                print( "match: ", wd['place']['value'] )
                break
            else:
                print( wd['distance']['value'],
                    wd['placeLabel']['value'],
                    wd['place']['value'],
                    # wd['place']['value'].split('/')[-1]
                    )
        print("----------")
        # break

    import code; code.interact(local=locals())

    return rows


def demo_addr():
    # addr = '1620 W. Harrison St. Chicago, IL 60612'
    # no find: "2070 N, IL-50, Suite 500, Bourbonnais, IL 60914"
    addr = "2070 N, IL-50, Bourbonnais, IL 60914"
    ll = addr_to_latlong(addr)
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

        print("[{Region}] {Medical Center Name}\n{goog}\n{wp}\n".format(
            goog=goog, wp=wp, **row))

        # Look for it in WikiData

        # isa = "Q4287745" if row['isa'] == 'hospital' else ''
        isa = "Q16917" if row['isa'] == 'hospital' else ''
        res = hospi_ll(row['lat'], row['long'], .5, isa )

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
    for row in rows:
        # pprint(row)
        # if "Hospital" in row['Medical Center Name'] and \
        #    row['Region'] == "Chicago" and \
        if not row['wikidata'] and \
            row['isa'] == 'hospital':
                one(row)
                break


def test():

    # c19it()

    # demo_addr()
    # all_addrs_to_ll( rows )

    # rows = ilppe_get()
    # what_am_i(rows)

    # db_hospis()

    # rows = chg()
    rows = chl()


def main():
    test()

if __name__ == '__main__':
    main()
