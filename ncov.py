"""
@author Kyle McPherson

Data sources used:
+ https://3g.dxy.cn/newh5/view/pneumonia - Real time Live media update - best source for China official numbers.
  Data hardcoded in HTML, can be accessed from console.log(window.getAreaStat)
  Updated everyday at 5PM GMT+1 (midnight Beijing)
"""
#!flask/bin/python
#!bin/bash/python
from flask import Flask
from flask_cors import CORS
from googletrans import Translator
t = Translator()

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

def translateChinese(data, province=False):
    for k, v in enumerate(data):
        v['provinceName'] = t.translate(v['provinceName']).text
        v['provinceShortName'] = t.translate(v['provinceShortName']).text

        if(province):
            for q, w in enumerate(v['cities']):
                w['cityName'] = t.translate(w['cityName']).text
    return data

@app.route('/data/chinese-provinces/', methods=['GET'])
def getDxyProvinces():
    soup = getSource()
    dxyJSON = json.loads(soup.select("#getAreaStat")[0].text[27:][:-11])
    dxy = translateChinese(dxyJSON, True)
    return json.dumps(dxy)


@app.route('/data/other-countries/', methods=['GET'])
def getDxyCountries():
    soup = getSource()
    dxyJSON = json.loads(soup.select("#getListByCountryTypeService2")[0].text[44:][:-11])

    for k, v in enumerate(dxyJSON, False):
        v["provinceName"] = t.translate(v["provinceName"]).text

    return json.dumps(dxyJSON)

@app.route('/')
def main():
    endpoints = f"<h1><u>API Endpoints</u></h1>Chinese Province Information & Cities - <span style='color:red'>/data/chinese-provinces/</span>\
    <br>Countries Affected Outwith China - <span style='color:red'>/data/other-countries/</span>"
    return endpoints

if __name__ == '__main__':
    app.run()
