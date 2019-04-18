# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 13:36:12 2019

@author: takan
"""

from dotenv import load_dotenv
import os
import pandas as pd
import requests
from datetime import datetime

"""
To get the key for API:
"""
#print(os.environ.get("key")) 
load_dotenv()
#print(os.environ.get("key"))
key = os.environ.get("key")
"""
For doing the calculations of the stock
this function takes symbol parameter 
and the cleaned dataframe which we generate from function data_cleaning_processing
"""
def calculations(sign,file):
    print("Stock:",sign)
    print("Run at Date:", datetime.date(datetime.now())," and at time:" , datetime.time(datetime.now()))
    #path = str(os.getcwd())+ '\\'+str(sign)+'.csv'
    #file=pd.read_csv(path)
    print("DATA related to price queries:")
    todayclose = file['close'].loc[file['"timestamp']== max(file['"timestamp'])]
    high =  max(file['high'])
    low = min(file['low'])
    print('Latest Date of Available Trading Data:',max(file['"timestamp']))
    print('Latest Close Price from the available Trading Data:','$'+str(float(todayclose.values)))
    print('Highest Price from the available Trading Data:','$'+str(float(high)))
    print('Lowest Price from the available Trading Data:','$'+str(float(low)))
    #todayclose = file['4. close'].loc[file['date']== max(file['date'])]
    todaylow = file['low'].loc[file['"timestamp']== max(file['"timestamp'])]
    todayhigh = file['high'].loc[file['"timestamp']== max(file['"timestamp'])]
    #print(todayclose.values)
    print("Recommendation of the stock as below:")
    if float(todayclose.values) > float(file['high'].mean()): # and float(todayclose.values)< float(file['high'].mean()):
        decision = "Definately Buy"
        price=  float(file['high'].mean())
        recommendation(decision,price,sign)
    elif float(todayclose.values) > float(file['close'].mean()) and float(todayclose.values) <  float(file['high'].mean()):
        price = float(file['close'].mean())
        decision="Can Buy"
        recommendation(decision,price,sign)
    else:
        #price = 1.2* float(todaylow.values)
        price = float(file['close'].mean())
        decision = "Shouldnt buy"
        recommendation(decision,price,sign)
    remove_files(sign)
"""
Recommandations explained
"""
def recommendation(decision,threshold,symbol):
    if decision =="Definately Buy":
        print("You definately buy "+symbol+" cause its performance for today is higher than its average high prices, which was: $"+str("{0:.2f}".format(threshold)))
    elif decision =="Can Buy":
    
        print("You can buy "+symbol+" cause its performance for today is higher than its mean close price, which was: $"+str("{0:.2f}".format(threshold)))
        
    else:
        print("You shouldnt buy "+symbol+" cause its performance for today lower than expected closing price, which was: $"+ str("{0:.2f}".format(threshold)))
"""
Using API function to get the best match for a symbol given
"""       
def search_symbol_json(keyword,key=key):
    'function to search a symbol using a keyword'
    base_url = 'https://www.alphavantage.co/query?'
    url = base_url+'function=SYMBOL_SEARCH&keywords='+keyword+'&apikey='+key
    response = requests.get(url).json()
    #sym,name=[],[]
    sym,name,sec_type,region,curr=[],[],[],[],[]
    for element in response['bestMatches']:
        sym.append(element['1. symbol'])
        name.append(element['2. name'])
        sec_type.append(element['3. type'])
        region.append(element['4. region'])
        curr.append(element['8. currency'])
    search_matches = pd.DataFrame({'symbol':sym,'name':name,'type':sec_type,'region':region,'currency':curr})
    return print(search_matches )  
"""
def data_cleaning_processing takes the correct symbol and downloads
the file from url, cleans it and then makes it a dataframe which can be 
easily processed by calculations function
"""
def data_cleaning_processing(corr_sign):
    
    path = str(os.getcwd())+ '\\'+str(corr_sign)+'.csv'
    data=pd.read_csv(path,skiprows=1,sep="\,",engine='python')
     
    data['"timestamp']=data['"timestamp'].str.replace('\"','')
    data['volume"']=data['volume"'].str.replace('\"','')
    pd.to_datetime(data['"timestamp'])
    pd.to_numeric(data['volume"'])
    FinalTable=pd.DataFrame(data)
    
    calculations(corr_sign,FinalTable)
    return FinalTable
"""
Function to remove files
"""
def remove_files(symbol):
    files = os.listdir(os.getcwd())
    removefile = symbol+'.csv'
    for f in files:
        if removefile in f:
          x=  removefile
          os.remove(x)
          return print("The file is removed:",x)
"""
Main body which takes input from user or suggests best matches
currently the limit is 5 which can be changed
"""
i=0
x=0
while i <5:
  Question = input("Please type the symbol of the stock to be checked:") 
  sign=Question

  #Using TIME_SERIES_DAILY High Usage with compact Size

  request_url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&"+"symbol="+sign+"&apikey="+key+"&datatype=csv"
  response = requests.get(request_url)
  rawdata= pd.DataFrame(response.text.splitlines())
  error = "Invalid API call"
  check = error in str(rawdata.head(3))
  
  if check == True :
    x=x+1
    try:
        i=i+1
        
        
        #print("Retry Number",i,",Total retries 3")
        #Question = input("Please type the symbol of the stock to be checked:")
        
        if x > 3:
            raise ValueError
        else:
            
            print("Incorrect symbol please look at table below")
            search_symbol_json(sign)
            continue
        
        
    except ValueError:
        print('Error getting data from the api, no return was given.')
        break
  else:
    
    symbol = Question
    filename = './'+symbol+'.csv'
    file1 = rawdata.to_csv(filename,sep=',',index_label =False ,index=False)
    data_cleaning_processing(symbol)
    i=i+1
    


