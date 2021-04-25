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
    elif sheet == "Interests":
        return 1368843475

def get_sheet(spreadsheet, sheet):
    result = spreadsheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=sheet + "!A2:I").execute()
    values = result.get('values')
    print(values)
    if not values:
        if (sheet == "Groups"):
            return None, None, None, None, None, None, None
        elif (sheet == "Leaderboard"):
            return None, None, None
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
        ids, names, scores, goals1, goals2, lastCheckIn, lastActive = get_groups(values)
        return ids, names, scores, goals1, goals2, lastCheckIn, lastActive
    elif (sheet == "Leaderboard"):
        ids, names, scores = get_leaderboard(values)
        return ids, names, scores
    elif (sheet == "Interests"):
        interests, categories = get_interests(values)
        return interests, categories
    elif (sheet == "Blacklist"):
        ids, blacklist = get_blacklist(values)
        return ids, blacklist

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
    names = []
    goals1 = []
    goals2 = []
    lastCheckIn = []
    lastActive = []
    for row in values:
        ids.append(row[0])
        names.append(row[1])
        scores.append(row[2])
        goals1.append(row[3])
        goals2.append(row[4])
        lastCheckIn.append(row[5])
        lastActive.append(row[6])
    return ids, names, scores, goals1, goals2, lastCheckIn, lastActive

def get_leaderboard(values):
    ids = []    
    names = []
    scores = []
    for row in values:
        ids.append(row[0])
        names.append(row[1])
        scores.append(row[2])
    return ids, names, scores

def get_interests(values):
    interests = []
    categories = []
    for row in values:
        interests.append(row[0])
        categories.append(row[1])
    return interests, categories

def get_blacklist(values):
    ids = []
    blacklist = []
    for row in values:
        ids.append(row[0])
        blacklist.append(row[1])
    return ids, blacklist

def write_sheet(spreadsheet, sheet, values:list):
    values = [values]
    body = {
        'values': values
    }
    result = spreadsheet.values().append(
    spreadsheetId=SPREADSHEET_ID, range=sheet,
    valueInputOption="USER_ENTERED", body=body).execute()
    print('{0} cells appended.'.format(result \
                                       .get('updates') \
                                       .get('updatedCells')))

def deleteEntry(spread, sheet, id): # Deletes the row of the associated ID.
    # Gets the values held in the spreadsheet
    index = findValue(spread, sheet, id)
    if(index == None):
        print("[quickstart deleteEntry] index returned none, aborting; database list possibly empty")
        return
    print("[quickstart deleteEntry] found and deleting index {}".format(index))
    #index = index + 2
    sheet_id = get_id(sheet)
    # delete_body = [
    #     {
    #         "requests" : [{
    #             "deleteDimension": {
    #                 "range": {
    #                     "sheetId": sheet_id,
    #                     "dimension": "ROWS",
    #                     "startIndex": index,
    #                     "endIndex": index+1
    #                 }
    #             }
    #         }
    #         ]
    #     }
    # ]
    clear_body = {
        "ranges" : [
            sheet + "!A" + str(index) + ":" + str(index)
        ]
    }
    result = spread.values().batchClear(spreadsheetId = SPREADSHEET_ID, body = clear_body).execute()
    
    sortSheet(spread, sheet)

def editValue(spread, sheet, id, colNum, value, append = False): # Target is to be defined as the number of the column. I.E. Column B = Target 2
    index = findValue(spread, sheet, id) # Get the location that we will be updating our value at, in case it changed. Add 2 for sheet index.
    # Here we obtain the row that we are hoping to change
    result = spread.values().get(spreadsheetId = SPREADSHEET_ID, range = sheet).execute()
    temp = result.get("values")[index-1]
    # Here we check if we want to append our value into the cell specified. This is used for adding goals.
    if append:
        temp[colNum] = temp[colNum] + ";" + str(value)
    else:
        temp[colNum] = str(value)
    index = findValue(spread, sheet, id) # Get the location that we will be updating our value at, in case it changed. Add 2 for sheet index.
    # Here we define a range that encompasses the entirety of the row in question.
    range = sheet + "!A" + str(index) + ":I" + str(index)
    # Here we define the request body for the function specifying the range and what we want to add in.
    value_Range_Body = {
        "range" : sheet + "!A" + str(index) + ":I" + str(index),
        "values" : [
            temp
        ]
    }
    # Our current approach is to update the entire row but only change one cell at a time.
    result = spread.values().update(spreadsheetId = SPREADSHEET_ID, 
                            range = range, valueInputOption = "USER_ENTERED", body = value_Range_Body).execute()

def getValue(spread, sheet, id):
    index = findValue(spread, sheet, id)
    result = spread.values().get(spreadsheetId = SPREADSHEET_ID, range = sheet + "!A" + str(index) + ":" + str(index)).execute()
    return result.get("values")[0] # Get the value at 0 because this function returns a list of the list we get from Google Sheets

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
    spread = spread()
    # sortSheet(spread, "Leaderboard", 2)
    # userVals = getValue(spread, "Leaderboard", "189543454563368960")
    # print("User " + userVals[0] + "'s name is " + userVals[1] + " and their score is " + userVals[2])
    # index = findValue(spread, "Leaderboard", "189543454563368960")
    # ids = []
    # names = []
    # scores = []
    # ids, names, scores = get_sheet(spread, "Leaderboard")
    # editValue(spread, "Leaderboard", "189543454563368960", 2, int(scores[index]) + 1, False)
