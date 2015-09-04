from flask import Flask, render_template, request, redirect

import requests
import datetime
import pandas as pd

from bokeh.plotting import figure
from bokeh.models import Range1d
from bokeh.embed import components
from jinja2 import Template


def plotDF(dataDF,StockName,ShowFeatures): 
  """ plot the selected features of the selected stock """
  dataDF['Date'] = pd.to_datetime(dataDF['Date'])
  # select the tools we want
  TOOLS="pan,wheel_zoom,box_zoom,reset,save"
  # set colors
  colors=["blue","red"]
  # build our figures
  p = figure(tools=TOOLS, plot_width=650, plot_height=650,x_axis_type="datetime")
  for i in range(len(ShowFeatures)):
    p.line(dataDF['Date'], dataDF[ShowFeatures[i]], color=colors[i],\
           line_width=1,alpha=0.5,legend=StockName+': '+ShowFeatures[i])
  p.title = 'Stock Evolution: ' + StockName
  p.legend.orientation = "top_right"
  p.grid.grid_line_alpha=0.7
  p.xaxis.axis_label = 'Date'
  p.yaxis.axis_label = 'Price'
  p.ygrid.band_fill_color="olive"
  p.ygrid.band_fill_alpha = 0.1

  # plots can be a single PlotObject, a list/tuple, or even a dictionary
  plots = {'Red': p}
  
  script, div = components(plots)
  message=''
  if len(ShowFeatures)==0:
    message='Nothing to show here, because you did not choose any feature.'
  template = Template('''<!DOCTYPE html>
  <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Stock Evolution</title>
        <style> div{float: left;} </style>
        <link rel="stylesheet" href="http://cdn.pydata.org/bokeh/release/bokeh-0.9.3.min.css" type="text/css" />
        <script type="text/javascript" src="http://cdn.pydata.org/bokeh/release/bokeh-0.9.3.min.js"></script>
        {{ script }}
    <h1>Stock Evolution for {{ stock_name }}</h1>
    <h2>{{ message}}</h2>
  <form id='index' method='post' action='/' > <!-- action is the URL you want to move to next-->
   <p>
   <input type='submit' value='Back' /> <!-- value is the text that will appear on the button. -->
   </p>
</form>

    </head>
    <body>
    {% for key in div.keys() %}
        {{ div[key] }}
    {% endfor %}
    </body>
  </html>
  ''')
  html_file = 'templates/bokeh_embed.html'
  with open(html_file, 'w') as textfile:
    textfile.write(template.render(script=script, div=div, stock_name=StockName,message=message))





app = Flask(__name__)

@app.route('/',methods=['GET','POST'])
def main():
  return redirect('/index')

@app.route('/index',methods=['GET','POST'])
def index():
  today=datetime.date.today()
  first_day_of_current_month = today.replace(day=1)
  last_day_of_previous_month = first_day_of_current_month - datetime.timedelta(days=1)
  StartDate = last_day_of_previous_month.strftime("%Y-%m") + today.strftime("-%d")
  if request.method == 'GET':
    return render_template('index.html',start_date=StartDate)
  else:
    StockName = request.form['stock_name'].upper()
    ShowFeatures=[] # which features to show
    if request.form.get('close_price',False):
       ShowFeatures.append('Close')
    if request.form.get('adj_close_price',False):
       ShowFeatures.append('Adj. Close')
    ReURL='https://www.quandl.com/api/v3/datasets/WIKI/'+StockName+'.json?auth_token=XMD-ta2mEyx3bj_AGW3n&start_date='+StartDate+'&end_date='+today.strftime("%Y-%m-%d")
    r = requests.get(ReURL).json()
    if 'dataset' in r:
      columnNames=r['dataset']['column_names']
      DFValues=r['dataset']['data']
      dataDF = pd.DataFrame(data=DFValues,columns=columnNames)
      plotDF(dataDF,StockName,ShowFeatures)
      return render_template('bokeh_embed.html') 
    else:
      message = "Quandl can't find the stock ticker. Please check the spelling and try again."# or: r['quandl_error']['message'] 
      return render_template('error.html', end_message=message) 


if __name__ == '__main__':
  app.run()
