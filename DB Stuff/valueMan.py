from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SPREADSHEET_ID = "1lWf3GVoGt9j5ibvoUFqYJbPz6xCbjAX2BnMnVkkDp6Q"
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Here we define a method that allows us to easily place values into our spreadsheet
def addValue(spread, sheet, id, value):
    # Gets the values held in the spreadsheet
    result = spread.values().append(spreadsheetId = SPREADSHEET_ID, 
                            range = sheet).execute()
    sortSheet(spread, sheet)

def sortSheet(spread, sheet, sortCol = 0, order = "ASCENDING"):
    if sheet == "Users":
        sheet = 2081950163
    elif sheet == "Groups":
        sheet = 2101048164
    elif sheet == "Leaderboard":
        sheet = 322611983
    if "ASCENDING" != order and "DESCENDING" != order:
        print("Error: " + order + " is not a valid order. Please type ASCENDING or DESCENDING")
    else:
        sort_body = {
            "requests": [
                {
                    "sortRange" : {
                        "range" : {
                            "sheetId" : sheet,
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

def editValue(spread, sheet, index, colNum, value, append = False): # Target is to be defined as the number of the column. I.E. Column B = Target 2
    # Here we obtain the row that we are hoping to change
    temp = getValue(spread, sheet, index)
    # Here we check if we want to append our value into the cell specified. This is used for adding goals.
    if append:
        temp[colNum] = temp[colNum] + str(value)
    else:
        temp[colNum] = str(value)
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
                            range = range, valueInputOption = "RAW", body = value_Range_Body).execute()


def deleteEntry(spread, sheet, id): # Deletes the row of the associated ID.
    # Gets the values held in the spreadsheet
    index = findValue(spread, sheet, id)
    delete_body = {
        "requests" : {
            "deleteDimension": {
                "range": {
                    "sheetId": 2101048164,
                    "dimension": "ROWS",
                    "startIndex": index - 1,
                    "endIndex": index
                }
            }
        }
    }
    result = spread.batchUpdate(spreadsheetId = SPREADSHEET_ID, body = delete_body).execute()
    
    sortSheet(spread, sheet)

def getValue(spread, sheet, index): # Receives value held in spreadsheet by index
    # Gets the values held in the spreadsheet
    result = spread.values().get(spreadsheetId = SPREADSHEET_ID, 
                            range = sheet).execute()
    # While the Google Sheets API starts its indices at 1, Python does not.
    # We will use the numbers as shown on the Google Sheets, but logically the code will automatically keep track of this potential oversight.
    index = index - 1; 
    # The Google Sheets API holds our results in a dictionary. Here we get the value associated to our key: "values"
    # We return the value held in this list at the specified index.
    return result.get("values")[index] # Returns the value held in the list that is held in the result dictionary under "values"
    

def findValue(spread, sheet, id): # Finds where an ID is held in the spreadsheet
    # Gets the values held in the spreadsheet from column A from row 2 onwards
    result = spread.values().get(spreadsheetId = SPREADSHEET_ID, 
                            range = sheet + "!A2:A").execute()
    i = 2; # Starts at 2 because sheets indices start at 1 and the first index is the name for our categories.
    for entry in result.get("values"):
        if id == int(entry[0]):
            return i
        i = i + 1

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

    """spreadsheet = {
        'properties': {
            'title': "Test"
        }
    }   
    spreadsheet = service.spreadsheets().create(body=spreadsheet,
                                        fields='spreadsheetId').execute()
    print('Spreadsheet ID: {0}'.format(spreadsheet.get('spreadsheetId')))"""

    #Call the Sheets API
    sheet = service.spreadsheets()
    return sheet

if __name__ == "__main__":
    spreadsheet = spread()
    deleteEntry(spreadsheet, "Groups", 111)