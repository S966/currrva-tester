import json,httplib
from terminaltables import AsciiTable


import ConfigParser
Config = ConfigParser.ConfigParser()
Config.read("config.ini")
applicationId = Config.get("appinfo","APPLICATION_ID")
apiKey = Config.get("appinfo","API_KEY")


def setupUsers(matches):
  global usersList
  usersList = []
  try:
    for i in matches:
      player1 = i["player1"]["objectId"]
      player2 = i["player2"]["objectId"]
      # Append all players to the list. If player exists in the list do not add
      if [player1] not in usersList:
        usersList.append([player1])

      if [player2] not in usersList:
        usersList.append([player2])
  except KeyError:
    print "Keyerror"

   # Setup the list to contain records with initialized 6 zeroes
  for i in usersList:
    i.extend([0,0,0,0,0,0])

  return usersList 


class Parse(object):
  @staticmethod
  def queryParse(collection):
    connection = httplib.HTTPSConnection('api.parse.com', 443)
    connection.connect()
    connection.request('GET', '/1/classes/' + collection, '', {
             "X-Parse-Application-Id": applicationId,
                    "X-Parse-REST-API-Key": apiKey 
                         })
    parse = json.loads(connection.getresponse().read())
    return parse
  
  @staticmethod
  def getMatch():
    return "Match"

  @staticmethod
  def getUser():
    return "User"

  @staticmethod
  def getAlert():
    return "Alert"

  @staticmethod
  def getFriendship():
    return "Friendship"

  
class calculateResults(object):

  def isAccepted(self,match):
    if match == "accept":
      return True

  def getPlayer(self, player, match):
    if player[0] == match["player1"]["objectId"]:
      return "player1"
    if player[0] == match["player2"]["objectId"]:
      return "player2"
    else:
      return False

  def didPlay(self, player, user):
    if player == "player1" or player == "player2":
      user[1] += 1



  def didWin(self, player, user, match):
    if player == "player1" and match["score1"] > match["score2"]:
      user[2] += 1
    if player == "player2" and match["score2"] > match["score1"]:
      user[2] += 1

  def didLose(self, player, user, match):
    if player == "player1" and match["score1"] < match["score2"]:
      user[3] += 1
    if player == "player2" and match["score2"] < match["score1"]:
      user[3] += 1

  def didDraw(self, user, match):
    if match["score1"] == match["score2"]:
      user[4] += 1

  def didScore(self, player, user, match):
    if player == "player1":
      user[5] += match["score1"] 
    if player == "player2":
      user[5] += match["score2"] 

  def didConcede(self, player, user, match):
    if player == "player1":
      user[6] += match["score2"] 
    if player == "player2":
      user[6] += match["score1"] 

class calculateHeadToHead(object):
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
  # Query Parse and get all matches
  matchCollection = Parse.getMatch()
  match = Parse.queryParse(matchCollection)
  allMatches = match["results"]

  # Setup a list for users
  usersList = setupUsers(allMatches)
  
  calculate = calculateResults()
  for user in usersList:
    for match in allMatches:
      player = calculate.getPlayer(user, match)
      if player != False:
        # print match["objectId"], " : ", user[0] , " is", player 
        try:
          if calculate.isAccepted(match["status"]):
            calculate.didPlay( player, user)
            calculate.didWin(player, user, match)
            calculate.didLose(player, user, match)
            calculate.didDraw(user, match)
            calculate.didScore(player, user, match)
            calculate.didConcede(player, user, match)
            
        except KeyError:
          pass
  prettify(usersList)

if __name__ == "__main__":
  main()
