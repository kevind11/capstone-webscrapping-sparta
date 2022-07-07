from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

url = 'https://www.coingecko.com/en/coins/ethereum/historical_data/?start_date=2020-01-01&end_date=2021-06-30'
url_get = requests.get(url, headers = { 'User-Agent': 'Popular browser\'s user-agent'})

soup = BeautifulSoup(url_get.content,"html.parser")
pages = soup.select('li.page-item:not(.next)')
total_pages = pages[-1].string

temp = [] #initiating a tuple

# loop all pages & get the data
for page in range(1, (int(total_pages) + 1)):
    url = 'https://www.coingecko.com/en/coins/ethereum/historical_data/?start_date=2020-01-01&end_date=2021-06-30&page=' + str(page)
    url_get = requests.get(url, headers = { 'User-Agent': 'Popular browser\'s user-agent'})
    soup = BeautifulSoup(url_get.content,"html.parser")
    #scrapping process
    table = soup.find('div', {"class":"coingecko-table"})
    rows = table.find('tbody').find_all('tr')
    row_length = len(rows)
    for i in range(0, row_length):
        date = str(rows[i].find('th').string)
        volume = rows[i].find_all('td')[1].string
        temp.append({"Date":date,"Volume":volume})


#change into dataframe
df = pd.DataFrame(temp)

#insert data wrangling here

# Remove \n, $, , from Volume and change to float dtype
df['Volume'] = df['Volume'].str.strip().\
str.replace('$', '', regex=False).\
str.replace(',', '', regex=False).\
astype('float')

# Change volume to smaller digit (million)
df['Volume'] = (df['Volume'] / 1e6).round(2)

# Change Date to datetime
df['Date'] = df['Date'].astype('datetime64[ns]')

# Set index to Date
df = df.set_index('Date')

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{df["Volume"].mean().round(2)}' #be careful with the " and ' 

	# generate plot
	ax = df.plot(figsize = (20,9)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)