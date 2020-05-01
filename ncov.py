"""
@author Kyle McPherson
Data sources used:
+ http://ncov.dxy.cn/ncovh5/view/pneumonia - Real time Live media update - best source for China official numbers.
  Data hardcoded in HTML, can be accessed from console.log(window.getAreaStat)
  Updated everyday at 5PM GMT+1 (midnight Beijing)
"""

#!flask/bin/python
#!bin/bash/python
from time import gmtime, strftime
import json

from flask import Flask
from flask_cors import CORS
from bs4 import BeautifulSoup as BS
from urllib import request

updated = False

app = Flask(__name__)
CORS(app)

locationData = []
statistics = []

def isEmpty(arr):
    if(len(arr) == 0):
        return True
    return False

def compareSame(temp, compareTo):
    if(temp is compareTo):
        return True
    return False

def turnToJSON(obj):
    return json.dumps(obj)

def getSource():
    dxySource = request.urlopen("http://ncov.dxy.cn/ncovh5/view/pneumonia")
    soup = BS(dxySource, "html.parser")
    soup.prettify()
    return soup

def updateLocationData():
    soup = getSource()
    temp = []

    try:
        dxyWorldwide = json.loads(soup.select("#getListByCountryTypeService2true")[0].text[48:][:-11])
        for k, v in enumerate(dxyWorldwide):
            index = dxyWorldwide[k]
            temp.append(
                {
                    "place": index['countryFullName'],
                    "infected": index['currentConfirmedCount'],
                    "cured": index['curedCount'] ,
                    "dead": index['deadCount']
                })

        if not (compareSame(temp, locationData)):
            locationData.clear()
            for k,v in enumerate(temp):
                locationData.append(v)

    except (IndexError, AttributeError, KeyError):
        pass

def updateStatistics():
    soup = getSource()
    temp = []

    try:
        stats = json.loads(soup.select("#getStatisticsService")[0].text[36:][:-11])
        globalStats = stats['globalStatistics']
        try:
            temp.append(
                {"totalCases": globalStats['confirmedCount'],
                 "curedCases": globalStats['curedCount'],
                 "totalDead": globalStats['deadCount']
                 })

            if not(compareSame(temp, statistics)):
                statistics.clear()
                statistics.append(*temp)
            else:
                pass

        except KeyError:
            pass

    except (IndexError, AttributeError):
        pass

#-----------------------------------------------------------------------------------------------------------
@app.route('/api/locations/', methods=['GET'])
def getLocationData():
    if(isEmpty(locationData)):
        updateLocationData()
    return turnToJSON(locationData)

@app.route('/api/stats/', methods=['GET'])
def getOverallNumbers():
    if(isEmpty(statistics)):
        updateStatistics()

    return turnToJSON(statistics)


@app.route('/')
def main():
    endpoints = f"<h1><u>API Endpoints</u></h1>Location Data - <span style='color:red'>/api/locations/</span>" \
                f"<br>Overall Statistics - <span style='color:red'>/api/stats/</span>"

    howTo = f"<br><br><h1><u>How To Use</u></h1>Add the endpoint to the end of the URL - <span style='color:red'>https://kalzeo.pythonanywhere.com/[ENDPOINT]</span>"
    return endpoints + howTo

if __name__ == '__main__':
    app.run(threaded=True)
