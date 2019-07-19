import csv
import re

import time
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
import requests
from selenium.webdriver.chrome.options import Options




def openDriver():
    options = Options()
    options.headless = True
    driver = webdriver.Chrome("/Users/saurabhbansal/PycharmProjects/webscrapper/venv/bin/chromedriver",options=options)
    driver.get( "https://qpublic.schneidercorp.com/Application.aspx?AppID=1051&LayerID=23951&PageTypeID=2&PageID=9967")


    return driver

def scrapeWebpage(url=None):
    """

    :param url:
    :return:
    """

    headers = requests.utils.default_headers()

    headers.update(
        {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    )

    response = requests.get(url,headers=headers)
    soup = BeautifulSoup(response.content,'html.parser')
    #print(soup.prettify())


    data = soup.find_all("table")
    findkeyvalue(data)
    heading = soup.find_all("h1")
    data = soup.find_all("tbody")
    getAppraisedValues(heading,data)
    salesInformation(heading,data)
    driver.close()


def findkeyvalue(data):
    keyvalue = []
    valuepair = []
    #keyvaluepair = []

    for tag in data:
        title = tag.find_all('strong')
        val = tag.find_all("span")

        for key in title:
            if (len( key )) > 0:
                keyvalue.append(key.text)

        for value in val:
            if(len(value))>0:
                valuepair.append(value.text)

    result = zip(keyvalue,valuepair)

    keyvaluepair = ((dict(result)))
    print(keyvaluepair)

    return keyvaluepair


def getAppraisedValues(heading, data):

    vector = []
    year = []
    appraisedLand = []
    appraisedValue =[]
    totalAppraisedvalue =[]
    appraisedValueData = {}


    for h1 in heading:
        if h1.text == 'Appraised Values':
            for d in data:
                value = d.find_all('tr')

                for val in value:
                    vector.append(val.text.split())




    for i in range(0,13):
        val = (str(vector[i]).replace("[","").replace("]","").replace("'",""))
        dollarvalue = re.search("[$][\d(\\d),$]+",val)
        valueNum=(dollarvalue.group(0).split("$"))
        yearValue = re.search("[0-9]{4}",val)



        year.append(yearValue.group(0))
        appraisedLand.append("{0}".format("$") + valueNum[1].replace(",",""))
        appraisedValue.append("{0}".format("$") + valueNum[2].replace(",",""))
        totalAppraisedvalue.append("{0}".format("$") + valueNum[3].replace(",",""))


    appraisedValueData["Year"] = year
    appraisedValueData["AppraisedLand"] = appraisedLand
    appraisedValueData["AppraisedBuildingValue"] = appraisedValue
    appraisedValueData["TotalAppraisedValue"] = totalAppraisedvalue

    print(appraisedValueData)


    return appraisedValueData


def salesInformation(heading, data):
    """

    :param heading:
    :param data:
    :return:
    """
    vector = []
    salesprice = []
    salesDate = []
    manustring = []


    for h1 in heading:
        if h1.text == 'Appraised Values':
            for d in data:
                value = d.find_all('tr')

                for val in value:
                    vector.append(val.text.split())

    for i in range(int(len(vector)-6),len(vector)):
        finalString=(str(vector[i]).replace( "[", "" ).replace( "]", "" ).replace( "'", ""))
        saleprice = re.search( "[$][\d(\\d),]+", finalString)
        if saleprice is None:
            continue
        else:
            salesprice.append(saleprice.group(0))
            saledate = re.search( "(1[0-2]|0?[1-9])/(3[01]|[12][0-9]|0?[1-9])/(?:[0-9]{2})?[0-9]{2}", finalString )
            salesDate.append(saledate.group(0))
            finalString=finalString.replace("VALIDATED","").replace("SALE","").replace("Click","").replace("Here","")
            manustring.append(finalString.replace(saledate.group(0),"").replace(saleprice.group(0),""))


    endindex = len(manustring[0].split(","))
    name = ""

    for i in range(1,endindex):
        name += (manustring[0].split(",").pop(i))

    print(name)

    grantee = name.strip()[0:int(len(name)/2)+4]
    print((grantee))







    #finalString = str((vector[int(len(vector))-5]))
    #print(len(finalString))
    #saledate = re.search("(1[0-2]|0?[1-9])/(3[01]|[12][0-9]|0?[1-9])/(?:[0-9]{2})?[0-9]{2}",finalString)
    #saledate=saledate.group(0)
    #saleprice = re.search("[$][\d(\\d),]+",finalString)
    #saleprice=saleprice.group(0)
    #listofignoredwords=["VALID SALE","NOT VALIDATED","MINIMUM CONSIDERATION","FINANCIAL INSTITUTION - R.E.O. SALE"]

    #stringmanipulation =(finalString.replace(saledate,"").replace(saleprice,"").replace("Click Here",""))
    #print((stringmanipulation.replace("FINANCIAL INSTITUTION - R.E.O. SALE","").replace("VALID SALE","")
     #      .replace("NOT VALIDATED","").replace("MINIMUM CONSIDERATION","")))






def closepopup():

    time.sleep(10)

    terms = driver.find_element_by_class_name( "modal-footer" )
    driver.find_element_by_class_name( "tab-item-bar" )
    link = terms.find_element_by_xpath( "//a[@class='btn btn-default button-1']" )
    link.click()






searchbyparcelNum = []
searchbylocationAdd = []

filename = "trial.csv"

with open(filename, "r" ) as readfile:
    reader = csv.reader(readfile)
    next(reader)

    for lines in reader:

        result = str(lines).replace("[","").replace("]","").replace("'", "")


        if result.isdigit():

            driver = openDriver()
            closepopup()

            searchbyparcelNum.append(result)
            searchboxParcelNumber = driver.find_element_by_id("ctlBodyPane_ctl02_ctl01_txtParcelID")
            searchboxParcelNumber.send_keys(result)
            searchboxParcelNumber.send_keys(Keys.ENTER)
            driver.close()

        else:
            driver = openDriver()
            closepopup()
            searchbylocationAdd.append(result)
            searchboxLocation = driver.find_element_by_id( "ctlBodyPane_ctl01_ctl01_txtAddress" )
            searchboxLocation.send_keys( result )
            searchboxLocation.send_keys( Keys.ENTER )
            print(driver.current_url)
            scrapeWebpage(driver.current_url)













