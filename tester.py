import json,httplib
from terminaltables import AsciiTable

import ConfigParser
Config = ConfigParser.ConfigParser()
Config.read("config.ini")
applicationId = Config.get("appinfo","APPLICATION_ID")
apiKey = Config.get("appinfo","API_KEY")

'''
class Currrva(object):

  def __init__(self):
    # Define app information 
    self.applicationId = Config.get("appinfo","APPLICATION_ID")
    self.apiKey = Config.get("appinfo","API_KEY")
'''

connection = httplib.HTTPSConnection('api.parse.com', 443)
connection.connect()
connection.request('GET', '/1/classes/Match', '', {
         "X-Parse-Application-Id": applicationId,
                "X-Parse-REST-API-Key": apiKey 
                     })
parse = json.loads(connection.getresponse().read())
singleMatch = parse["results"]

def setupUsers():
  usersList= []
  try:
    for i in singleMatch:
      player1 = i["player1"]["objectId"]
      player2 = i["player2"]["objectId"]
      # Append all players to the list. If player exists in the list do not add
      if [player1] not in usersList:
        usersList.append([player1])

      if [player2] not in usersList:
        usersList.append([player2])
  except KeyError:
    pass
   # Setup the list to contain records with initialized 6 zeroes
  for i in usersList:
    i.extend([0,0,0,0,0,0])
  return usersList 

def calculateResults(usersList):
  ''' 
  Add results in a list for each player. List follows (p, w, l, d, f, c) format where:
  p = Number of games played
  w = Number of wins
  l = number of losses
  d = number of draws
  f = number of goals scored
  c = number of goals conceded
  '''
  for i in singleMatch:
    player1 = i["player1"]["objectId"]
    player2 = i["player2"]["objectId"]
    gameStatus = i["status"]
    for k  in range(0, len(usersList)):
      # Player 1 Results
      if player1 == usersList[k][0] and gameStatus == "accept":
        usersList[k][1] += 1 # Calculate number of games
        usersList[k][5] += i["score1"] # Calculate goals scored
        usersList[k][6] += i["score2"] # Calculate goals conceded
        if i["score1"] > i["score2"]:
          usersList[k][2] += 1 # Calculate wins 
        elif i["score1"] < i["score2"]:
          usersList[k][3] += 1 # Calculate losses
        else:
          usersList[k][4] += 1 # Calculate draws 
      # Player 2 Results
      if i["player2"]["objectId"] == usersList[k][0] and gameStatus == "accept":
        usersList[k][1] += 1 # Calculate number of games
        usersList[k][5] += i["score2"] # Calculate goals scored
        usersList[k][6] += i["score1"] # Calculate goals conceded
        if i["score2"] > i["score1"]:
          usersList[k][2] += 1 # Calculate wins 
        elif i["score2"] < i["score1"]:
          usersList[k][3] += 1 # Calculate losses
        else:
          usersList[k][4] += 1 # Calculate draws 
  return usersList 

def calculateHeadToHead():
  pass

def prettify(table_data):
  tableHeaderList = [["User ID", "Played", "Wins", "Losses", "Draws", "Goals For", "Goals Conceded"]]
  # Convert to int to strings to setup for terminaltable library requirements 
  for i in range(0, len(table_data)):
    table_data[i] = map(str, table_data[i]) 
  final_table = tableHeaderList + table_data
  pretty_table = AsciiTable(final_table)
  print "\nCURRRVA FULL RECORDS FOR ALL USERS"
  print pretty_table.table
   
def main():
  usersList = setupUsers()
  fullRecordList = calculateResults(usersList)
  prettify(fullRecordList)

if __name__ == "__main__":
  main()
