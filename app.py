from flask import Flask, render_template 
import pandas as pd
import requests
from bs4 import BeautifulSoup 
from io import BytesIO
import base64
import matplotlib.pyplot as plt

app = Flask(__name__)

def scrap(url):
    #This is fuction for scrapping
    url_get = requests.get(url)
    soup = BeautifulSoup(url_get.content,"html.parser")
    
    #Find the key to get the information
    table = soup.find("div", { "class" : "lister-list" })
    row = table.find_all("div", { "class" : "lister-item mode-advanced" })

    tmp = [] #initiating a tuple

    for i in range(0, len(row)):
        title = row[i].find("h3", { "class" : "lister-item-header" }).find('a').text.strip()
        rating = row[i].find("div", { "inline-block ratings-imdb-rating" }).find('strong').text.strip()
        if (row[i].find("span", { "metascore favorable" }) is None):
            metascore = '0'
        else:
            metascore = row[i].find("span", { "metascore favorable" }).text.strip()
        votes = row[i].find("span", {"name" : "nv" }).text.strip()


        tmp.append((title, rating, metascore, votes)) #append the needed information 

    df = pd.DataFrame(tmp, columns = ('judul' , 'imdb_rating' , 'metascore', 'votes'))
    df['votes'] = df['votes'].str.replace(",", "")
    df['imdb_rating'] = df['imdb_rating'].astype('float')
    df['metascore'] = df['metascore'].astype('float')
    df['votes'] = df['votes'].astype('int')
   #data wranggling -  try to change the data type to right data type

   #end of data wranggling

    return df

@app.route("/")
def index():
    df = scrap("https://www.imdb.com/search/title/?release_date=2019-01-01,2019-12-31") #insert url here

    #This part for rendering matplotlib
    fig = plt.figure(figsize=(5,2),dpi=300)
    df.plot()
    
    #Do not change this part
    plt.savefig('plot1',bbox_inches="tight") 
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    result = str(figdata_png)[2:-1]
    #This part for rendering matplotlib

    #this is for rendering the table
    df = df.to_html(classes=["table table-bordered table-striped table-dark table-condensed"])

    return render_template("index.html", table=df, result=result)


if __name__ == "__main__": 
    app.run()
