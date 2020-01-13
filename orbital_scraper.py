#!/usr/bin/env python
# coding: utf-8

# In[61]:


import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
from datetime import datetime
from dateutil import parser

URL = "https://en.wikipedia.org/wiki/2019_in_spaceflight#Orbital_launches"

res = requests.get(URL).text
soup = BeautifulSoup(res,'lxml')
table_to_parse = soup.find('table', class_='wikitable')

def pre_process_table(table):
    """
    INPUT:
        1. table - a bs4 element that contains the desired table: ie <table> ... </table>
    OUTPUT:
        a tuple of: 
            1. rows - a list of table rows ie: list of <tr>...</tr> elements
            2. num_rows - number of rows in the table
            3. num_cols - number of columns in the table
    Options:
        include_td_head_count - whether to use only th or th and td to count number of columns (default: False)
    """
    rows = [x for x in table.find_all('tr')]
    
    num_rows = len(rows)
    
    # get an initial column count. Most often, this will be accurate
    num_cols = max([len(x.find_all(['th','td'])) for x in rows])

    # sometimes, the tables also contain multi-colspan headers. This accounts for that:
    header_rows_set = [x.find_all(['th', 'td']) for x in rows if len(x.find_all(['th', 'td']))>num_cols/2]

    num_cols_set = []

    for header_rows in header_rows_set:
        num_cols = 0
        for cell in header_rows:
            row_span, col_span = get_spans(cell)
            num_cols+=len([cell.getText()]*col_span)

        num_cols_set.append(num_cols)

    num_cols = max(num_cols_set)

    return (rows, num_rows, num_cols)


def get_spans(cell):
        """
        INPUT:
            1. cell - a <td>...</td> or <th>...</th> element that contains a table cell entry
        OUTPUT:
            1. a tuple with the cell's row and col spans
        """
        if cell.has_attr('rowspan'):
            rep_row = int(cell.attrs['rowspan'])
        else: # ~cell.has_attr('rowspan'):
            rep_row = 1
        if cell.has_attr('colspan'):
            rep_col = int(cell.attrs['colspan'])
        else: # ~cell.has_attr('colspan'):
            rep_col = 1 

        return (rep_row, rep_col)

def process_rows(rows, num_rows, num_cols):
    """
    INPUT:
        1. rows - a list of table rows ie <tr>...</tr> elements
    OUTPUT:
        1. data - a Pandas dataframe with the html data in it
    """
    data = pd.DataFrame(np.ones((num_rows, num_cols))*np.nan)
    for i, row in enumerate(rows):
        try:
            col_stat = data.iloc[i,:][data.iloc[i,:].isnull()].index[0]
        except IndexError:
            print(i, row)

        for j, cell in enumerate(row.find_all(['td', 'th'])):
            rep_row, rep_col = get_spans(cell)

            #print("cols {0} to {1} with rep_col={2}".format(col_stat, col_stat+rep_col, rep_col))
            #print("\trows {0} to {1} with rep_row={2}".format(i, i+rep_row, rep_row))

            #find first non-na col and fill that one
            while any(data.iloc[i,col_stat:col_stat+rep_col].notnull()):
                col_stat+=1

            data.iloc[i:i+rep_row,col_stat:col_stat+rep_col] = cell.getText()
            if col_stat<data.shape[1]-1:
                col_stat+=rep_col

    return data
#import re

def split_it(year):
    #whiteSpaceRegex = " ";
    words = re.split('\s+', year)
    #words
    words[1]=re.sub(r"\d", "", words[1])
    words[1]=re.sub('[^A-Za-z0-9]+', '', words[1])[:3]
    
    ans=words[0]+" "+words[1]+" "+"2019"
    return ans

def date_format(date):
    
    date = parser.parse(date)
    
    #date = datetime.strptime(date, '%d %m %Y')
    date.isoformat()
    #print(date)
    return date
rows, num_rows, num_cols = pre_process_table(table_to_parse)
df = process_rows(rows, num_rows, num_cols)
df = df.iloc[3:]
df.columns = ["date", "Rocket", "Flight", "Launch Site", "Launch Site 2", "LSP", "LSP 2"]
df["date"]= df["date"].apply(split_it)
#df["Date"]= df["Date"].apply(date_format)
#df["Date"] = re.sub(r"\d", "", df["Date"])
dfq = pd.DataFrame() 
dfq['date_all'] = pd.date_range('1/1/2019', periods = 365, freq ='D') 
print(dfq['date_all'])
# Remove all starting and ending white spaces
df["date"] = df["date"].str.rstrip()
df["date"] = df["date"].str.lstrip()
df["Flight"] = df["Flight"].str.rstrip()
df["LSP"] = df["LSP"].str.rstrip()
df["LSP 2"] = df["LSP 2"].str.rstrip()
df["Rocket"] = df["Rocket"].str.rstrip()
df["Launch Site"] = df["Launch Site"].str.rstrip()
df["Launch Site 2"] = df["Launch Site 2"].str.rstrip()
df["Flight"] = df["Flight"].str.lstrip()
df["LSP"] = df["LSP"].str.lstrip()
df["LSP 2"] = df["LSP 2"].str.lstrip()
df["Rocket"] = df["Rocket"].str.lstrip()
df["Launch Site"] = df["Launch Site"].str.lstrip()
df["Launch Site 2"] = df["Launch Site 2"].str.lstrip()


# Remove Dirty Rows which aren't useful
df = df[df['Flight'] != df['Rocket']]

# Mark the Launch Vehicles (Represented as 1) and Payloads (Represented as 0)
df['value'] = (df['Launch Site'].str.strip().str.lower()==df['Launch Site 2'].str.strip().str.lower()).astype(int)


# Count the Number of Launches for each date

#print(df.groupby("Date").count())

#print(df[(df['Date'].isin(df['Date'][df['LSP 2'].isin(['Operational','Successful', 'En Route'])])) & (df['Category'] == 1)].groupby('Date').sum())
df_new=df[(df['date'].isin(df['date'][df['LSP 2'].isin(['Operational','Successful', 'En Route'])])) & (df['value'] == 1)]
df_new["date"]= df_new["date"].apply(date_format)
#print(df_new['Date'])
df_1=df_new.groupby('date').sum()
#new=dfq.join(df_1)
#merge=pd.merge(dfq,df_1, how='inner', left_index=True, right_index=True)
#print(merge)
df_1.to_csv('output.csv')


# In[ ]:





# In[ ]:




