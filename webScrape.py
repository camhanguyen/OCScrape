# 04.02.2020 HN How updated are schools with online learning option on their site?
# First scrape all links to school codes based on cdscode on cde.ca.gov
# Then go to site and scrape school website
# Then go to school website and see if there site mentions "online learning" option on the Home page

# Import libraries
import os
os.chdir("your directory path")
import pandas as pd # data wrangling
import bs4 # web scraping
from bs4 import BeautifulSoup as BS
import requests # web scraping
import time  
import datetime

# Part 1. Create a dataframe of all link to school website. The state directory provides access to the individual school profiles. On the profile page there is the link to the school url.
# https://www.cde.ca.gov/schooldirectory/
# The data file of school profiles is exported from the CA state's school directory website
# with the following columns: Record, CDSCode, County, District, Locations

cdeData = pd.read_csv("cdscode.csv", dtype={"CDSCode": str})
cdeData.head()

# Create a column with the url links for the individual school record in the state's directory
urlBase = "https://www.cde.ca.gov/SchoolDirectory/details?cdscode="
cdeData["cdeLink"]=urlBase+cdeData["CDSCode"].astype(str)

# First join all string into an array
urlDf = cdeData["cdeLink"].str.cat(sep=',')
urlDf = urlDf.split(',')

# Loop through the URL lists for the state directory, and save the school website URL
urlList = []
IDMap= {}

badStrs=["www.cde.ca.gov", "google.com"] # remove the unwanted urls from the individual school record sites (common patterns are a googlemap link and the state directory links)

with open('htmlList.txt', 'w') as myfile, open('schoolList.txt', 'w') as schoolfile: # save links to local files
    for b in urlDf:
        time.sleep(.5)
        print("Requesting: "+b)
        try:
            html = requests.get(b).text
        except Exception as e: # if request out of time, move on
            print(e)
            continue
        myfile.write(b+'\n') # save to local file
        
        soup = BS(html, "html.parser")
        section = soup.find_all(class_="table table-bordered small")
        tempList = []

        for elem in section:
            link1 = elem.find_all("a")
            for link in link1:
                schoolLink = link.get("href", None)
                if schoolLink and (schoolLink.find("https://")>=0 or schoolLink.find("http://")>=0): # retrieve all links starting out with https or http, remove the ones containing badStrs
                    skip=False
                    for bad in badStrs:
                        if(schoolLink.find(bad)>=0):
                            skip=True
                            break
                    if(skip):
                        continue
                    tempList.append(schoolLink)
                    urlList.append(schoolLink)
                    print(schoolLink)
                    schoolfile.write(schoolLink+'\n') # save school url links to local files
    
        IDMap[b]=tempList # map school links to directory link, so that we can later link the school link back to the original cdeData frame
        
# Part 2. Create a list: if school websites contain the keywords for online learning, mark as True
# Define function to flag whether keywords exist or not
def findKeywords(url):
    fileName=datetime.date.today().isoformat()+"_"+"OC_"+url.replace('/', "_")+'.txt' #write individual html file to local disk, for faster retrieval
    with open(fileName, 'w') as f:
        kw = ["online", "internet", "virtual", "en línea", "on-line", "conectado", "distance learning", "e-learning", "distal", "home learning"]

        try:
            schoolurlText = requests.get(url).text.lower()
        except Exception as e: # if request out of time, move on
            print(e)
            return False
        f.write(schoolurlText)
        f.flush()
        for w in kw:
            if schoolurlText.find(w)>=0:
                return True
        return False

# Create inverse IDMap
invIDMap = {}
def addDict(d, key, val):
    if(key in d):
        d[key].append(val)
    else:
        d[key]=[val]
        
for key in IDMap.keys():
    urls=IDMap[key]
    for url in urls:
        addDict(invIDMap, url, key)
        
# Run keyword function       
haveKw = {}
for url in urlList:
    haveKw[url]=findKeywords(url)

# Part 3. Match with original dataframe (with school record, location, etc.)
# First change the keyword dataframe (whether school sites have keyword or not) to a dataframe
haveKwDf = pd.DataFrame.from_dict(haveKw, orient='index')

# Map school link with link from state's directory links
haveKwDf['cdeLink'] = haveKwDf['schoolLink'].map(invIDMap)

# Match with original ataframe, based on the state's directory links
kwSchoollinkMerge = pd.merge(haveKwDf, cdeData, on = "cdeLink", how="inner")

kwSchoollinkMergeMapDf = pd.DataFrame(kwSchoollinkMergeMap)
kwSchoollinkMergeMapDf.to_csv("mergedDf2.csv") # Write to file with merged df

# For the illustrative map, I selected only schools in Orange County
OCMerge = kwSchoollinkMergeMapDf.loc[(kwSchoollinkMergeMapDf["County"]=="Orange")]
OCMerge.to_csv("OCMerge.csv")
