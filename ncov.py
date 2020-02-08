"""
@author Kyle McPherson
Data sources used:
+ http://ncov.dxy.cn/ncovh5/view/pneumonia - Real time Live media update - best source for China official numbers.
  Data hardcoded in HTML, can be accessed from console.log(window.getAreaStat)
  Updated everyday at 5PM GMT+1 (midnight Beijing)
"""
#!flask/bin/python
#!bin/bash/python
from flask import Flask
from flask_cors import CORS
from googletransx import Translator

app = Flask(__name__)
CORS(app)

import json
from bs4 import BeautifulSoup as BS
from urllib import request

def getSource():
    dxySource = request.urlopen("http://ncov.dxy.cn/ncovh5/view/pneumonia")
    soup = BS(dxySource, "html.parser")
    soup.prettify()
    return soup

@app.route('/api/location-data/', methods=['GET'])
def getLocationData():
    soup = getSource()
    data = []
    dxyCountries = json.loads(soup.select("#getListByCountryTypeService2")[0].text[44:][:-11])
    dxyProvinces = json.loads(soup.select("#getAreaStat")[0].text[27:][:-11])

    for k, v in enumerate(dxyCountries):
        translate = Translator()
        countryName = translate.translate(v['provinceName']).text
        data.append({"location": countryName, "infected": v['confirmedCount'], "cured": v['curedCount'],
             "dead": v['deadCount'], "type": "Country"})

    for k, v in enumerate(dxyProvinces):
        translator = Translator()
        name = translator.translate(v['provinceName']).text
        data.append(
            {"location": name, "infected": v['confirmedCount'], "cured": v['curedCount'],
             "dead": v['deadCount'], "type": "Province"})

    return json.dumps(data)

@app.route('/api/overall-numbers/', methods=['GET'])
def getOverallNumbers():
    soup = getSource()
    data = []
    numbers = json.loads(soup.select("#getStatisticsService")[0].text[36:][:-11])

    for k, v in enumerate(numbers):
        data.append({"totalCases": v['confirmedCount'], "suspectedCases": v['suspectedCount'], "curedCases": v['curedCount'],
                     "severeCases": v['seriousCount'], "totalDead": v['deadCount'], "totalCasesDailyIncr": v['confirmedIncr'],
                     "suspectedCasesDailyIncr": v['suspectedIncr'], "curedCasesDailyIncr": v['curedIncr'],
                     "severeCasesDailyIncr": v['seriousIncr'], "totalDeadDailyIncr": v['deadIncr']})
        
    return json.dumps(data)

@app.route('/')
def main():
    endpoints = f"<h1><u>API Endpoints</u></h1>Location Data - <span style='color:red'>/api/location-data/</span>"

    howTo = f"<br><br><h1><u>How To Use</u></h1>Add the endpoint to the end of the URL - <span style='color:red'>https://kalzeo.pythonanywhere.com/[ENDPOINT]</span>"
    return endpoints + howTo

if __name__ == '__main__':
    app.run()
