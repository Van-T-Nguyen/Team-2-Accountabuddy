from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

spreadsheet = None #Blank spreadsheet to be used later

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = "1lWf3GVoGt9j5ibvoUFqYJbPz6xCbjAX2BnMnVkkDp6Q"#'1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms' #this is the spreadsheet I made

def findValue(spread, sheet, id): # Finds where an ID is held in the spreadsheet
    # Gets the values held in the spreadsheet from column A from row 2 onwards
    result = spread.values().get(spreadsheetId = SPREADSHEET_ID, 
                            range = sheet + "!A2:A").execute()
    values = result.get('values')
    if not values:
        print('No data found.')
        return None
    i = 2; # Starts at 2 because sheets indices start at 1 and the first index is the name for our categories.
    for entry in values:
        if id == int(entry[0]):
            return i
        i = i + 1

def get_id(sheet):
    if sheet == "Queue":
        return 0
    elif sheet == "Message":
        return 1793963230
    elif sheet == "Users":
        return 2081950163
    elif sheet == "Groups":
        return 2101048164
    elif sheet == "Leaderboard":
        return 322611983

def get_sheet(spreadsheet, sheet):
    result = spreadsheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=sheet + "!A2:I").execute()
    values = result.get('values')
    print(values)
    if not values:
        if (sheet == "Groups"):
            return None, None, None, None, None, None
        else:
            return None, None
    elif (sheet == "Queue"):
        ids, goals = get_queue(values)
        return ids, goals
    elif (sheet == "Message"):
        ids, messages = get_message(values)
        return ids, messages
    elif (sheet == "Users"):
        ids, interests = get_users(values)
        return ids, interests
    elif (sheet == "Groups"):
        ids, scores, link1, goals1, link2, goals2 = get_groups(values)
        return ids, scores, link1, goals1, link2, goals2
    elif (sheet == "Leaderboard"):
        ids, scores = get_leaderboard(values)
        return ids, scores

def get_queue(values):
    ids = []    
    goals = []
    for row in values:
        ids.append(row[0])
        goals.append(row[1])
    return ids, goals

def get_message(values):
    ids = []
    message = []
    for row in values:
        ids.append(row[0])
        message.append(row[1])
    return ids, message

def get_users(values):
    ids = []    
    interests = []
    for row in values:
        ids.append(row[0])
        interests.append(row[1])
    return ids, interests

def get_groups(values):
    ids = []    
    scores = []
    link1 = []    
    goals1 = []
    link2 = []    
    goals2 = []
    for row in values:
        ids.append(row[0])
        scores.append(row[1])
        link1.append(row[2])
        goals1.append(row[3])
        link2.append(row[4])
        goals2.append(row[5])
    return ids, scores, link1, goals1, link2, goals2

def get_leaderboard(values):
    ids = []    
    scores = []
    for row in values:
        ids.append(row[0])
        scores.append(row[1])
    return ids, scores

def write_sheet(spreadsheet, sheet, values:list):
    values = [values]
    body = {
        'values': values
    }
    result = spreadsheet.values().append(
    spreadsheetId=SPREADSHEET_ID, range=sheet,
    valueInputOption="RAW", body=body).execute()
    print('{0} cells appended.'.format(result \
                                       .get('updates') \
                                       .get('updatedCells')))

def deleteEntry(spread, sheet, id): # Deletes the row of the associated ID.
    # Gets the values held in the spreadsheet
    index = findValue(spread, sheet, id)
    sheet_id = get_id(sheet)
    delete_body = {
        "requests" : {
            "deleteDimension": {
                "range": {
                    "sheetId": sheet_id,
                    "dimension": "ROWS",
                    "startIndex": index - 1,
                    "endIndex": index
                }
            }
        }
    }
    result = spread.batchUpdate(spreadsheetId = SPREADSHEET_ID, body = delete_body).execute()
    
    sortSheet(spread, sheet)


def sortSheet(spread, sheet, sortCol = 0, order = "ASCENDING"):
    sheet_id = get_id(sheet)
    if "ASCENDING" != order and "DESCENDING" != order:
        print("Error: " + order + " is not a valid order. Please type ASCENDING or DESCENDING")
    else:
        sort_body = {
            "requests": [
                {
                    "sortRange" : {
                        "range" : {
                            "sheetId" : sheet_id,
                            "startRowIndex" : 1
                        },
                        "sortSpecs" : [
                            {
                                "dimensionIndex": sortCol,
                                "sortOrder" : order
                            }
                        ]
                    }
                }
            ]
        }
        result = spread.batchUpdate(spreadsheetId = SPREADSHEET_ID,
                                body = sort_body).execute()
 

def spread():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
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

    #Call the Sheets API
    sheet = service.spreadsheets()
    return sheet

if __name__ == '__main__':
    spreadsheet = spread()
    #write_sheet(spreadsheet, "Users", ["162777143028350976", ["Blah", "Hahaha MORE entries"]])
    #deleteEntry(spreadsheet, "Users", 162777143028350976)
    get_sheet(spreadsheet, "Message")
    #print(findValue(spreadsheet, "Groups", 112))