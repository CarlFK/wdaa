# googsheet.py - some google sheet things


import pickle
import os.path

from httplib2 import Http
from pprint import pprint

# for goog spreassheet api
# https://developers.google.com/resources/api-libraries/documentation/sheets/v4/python/latest/

import oauth2client # import file, client, tools
from oauth2client.file import Storage

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

sheets = {
    'sample': {
        'ssid':  '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms',
        'cells': 'Class Data!A2:E'
            },
    'idph': {
        # 'ssid':  '1uJ5r1qlXl5YLXvMHREDKtsfULy-P3xfU',
        'ssid':  '12inQ_P2xrEevzu5rbBANSRpekvZX3bASekP8AfNOWDI',
        'cells': 'A1:I208'
            }
        }

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def v_to_ld(values, offset=0):
    # values to List of Dicts
    # first row are key names, rest is data

    # get rid of extra headers:
    values = values[offset:]

    if not values:
        print('No data found.')
        import code; code.interact(local=locals())

    else:
        # make a list of dicts, first row are keys:
        keys=values[0]
        # and a "row#" key:
        if 'row' in keys:
            print("'row' already a key.")
            import code; code.interact(local=locals())
        else:
            keys.insert(0, 'row')

        # print("keys: {}".format(keys))
        rows=[]
        rowno = offset + 2
        for row in values[1:]:

            #pad empty cells
            row.extend( [None] * (len(keys) - len(row)) )

            # prepend the row number
            row.insert(0,rowno)
            rowno += 1

            rowd = dict(zip(keys, row))
            rows.append(rowd)

    return rows


def goog_sheet(spreadsheetId, range_name='A1:ZZ99999'):
    # read from goog spreadsheet

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheetId,
                                range=range_name).execute()
    values = result.get('values', [])

    rows = v_to_ld(values)

    return rows


def goog_sheet_old(spreadsheetId, range_name='A1:ZZ99999'):

    """
    range is any
https://developers.google.com/resources/api-libraries/documentation/sheets/v4/python/latest/sheets_v4.spreadsheets.values.html#get

    you can define a named range in the spreadsheet name, like "veyepar"
    (this is a good idea.)

    whatever the range is:
    top row of that range will be dictionary keys
    remaining rows will be data.
    """

    # Setup the Sheets API
    # SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'

    store = oauth2client.file.Storage('credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = oauth2client.client.flow_from_clientsecrets(
                'client_secret.json', SCOPES)
        creds = oauth2client.tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))

    result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheetId,
            range=range_name).execute()

    values = result.get('values', [])

    return values


def sample():

    sheet = sheets['sample']
    ssid = sheet['ssid']
    cells = sheet['cells']
    rows = goog_sheet(ssid, cells)
    for row in rows:
        print(row)

def idph():

    sheet = sheets['idph']
    ssid = sheet['ssid']
    cells = sheet['cells']
    rows = goog_sheet(ssid, cells)
    for row in rows:
        print(row['Hospital'])

def test():
    sample()
    idph()

def main():
    test()

if __name__ == '__main__':
    main()
