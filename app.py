from flask import Flask, render_template, request, redirect

import requests
import datetime
import pandas as pd

# deal with the plot and embedding into bokeh_embed.html
from MyAux import *



app = Flask(__name__)

@app.route('/',methods=['GET','POST'])
def main():
  return redirect('/index')

@app.route('/index',methods=['GET','POST'])
def index():
  EndDate=datetime.date.today()
  StartDate = getStartDate(EndDate) # StartDate is a string: %Y-%m-%d
  if request.method == 'GET':
    return render_template('index.html',start_date=StartDate)
  else:
    StockName = request.form['stock_name'].upper()
    ShowFeatures=[] # which features to show
    if request.form.get('close_price',False):
       ShowFeatures.append('Close')
    if request.form.get('adj_close_price',False):
       ShowFeatures.append('Adj. Close')
    ReURL='https://www.quandl.com/api/v3/datasets/WIKI/'+StockName+'.json?auth_token=XMD-ta2mEyx3bj_AGW3n&start_date='+StartDate+'&end_date='+EndDate.strftime("%Y-%m-%d")
    r = requests.get(ReURL).json()
    if 'dataset' in r:
      dataDF = pd.DataFrame(data=r['dataset']['data'],\
                         columns=r['dataset']['column_names'])
      plotDF(dataDF,StockName,ShowFeatures)
      return render_template('bokeh_embed.html') 
    else:
      message = "Quandl can't find the stock ticker. Please check the spelling and try again."# or: r['quandl_error']['message'] 
      return render_template('error.html', end_message=message) 


if __name__ == '__main__':
  app.run()
