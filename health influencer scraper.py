#!/usr/bin/env python
# coding: utf-8

#author: Michelle Chaewon Bak
#website: https://influence.co/category/health

import os
import csv
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

# In[86]:


with open('health_flz_list.csv', 'w', encoding='utf8', newline='') as f:
    fieldnames = ['Name', 'Subtitle', 'Inst_link', 'Topic_tag', 'Location']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    #there are 200 pages (10,000 influencers) in total
    for x in range(1, 201):
        result = requests.get("https://influence.co/category/health/" + str(x))
        src = result.content
        soup = BeautifulSoup(src, 'lxml')

        #tables of influencer info
        tables = soup.find_all("div", attrs={'class': 'middle'})
        for table in tables:
            #influencer name
            try:
                name = table.find("h4", attrs={'class': 'no-wrap-ellipsis'}).a.text
            except:
                name = ""
            
            #subtitle under influencer name
            try:
                subtitle = table.find("p", attrs={'class': 'influencer-headline no-wrap-ellipsis'}).text 
            except:
                subtitle = ""
            
            #INSTAGRAM USERNAME
            #instagram username will be collected from instagram link; I think this method is more accurate as we
            #extract username directly from instagram link
                
            #instagram link
            #I know this approach might seem somewhat inefficient, this worked for me.
            #if you know more efficient way to extract insta_link, please use that method!
            #I'm gonna filter this list to include only instagram link later on
            try:
                link_list = []
                link_bodies = table.find_all("a")
                for url in link_bodies:
                    link_list.append(url['href'])  
                link = link_list
            except:
                link = ""
                
            #topic_tag
            try:
                tag_list = []
                tags = table.find_all("span", attrs={'class': 'category-name'})
                for tag in tags:
                    tag_list.append(tag.a.text)
                    topic_tag = tag_list
            except:
                tag = ""
                
            #location info
            try:
                location = table.find("p", attrs={'style': 'margin-bottom: 10px;'}).text
            except:
                location = ""
                
            writer.writerow({'Name': name, 'Subtitle': subtitle, 'Inst_link': link, 
                            'Topic_tag': topic_tag, 'Location': location})


# In[219]:


df = pd.read_csv('health_flz_list.csv')
df = df.astype(str)

#remove newlines
df = df.replace('\n','', regex=True)
#replace empty cell with NaN
df = df.replace(r'^\s*$', np.NaN, regex=True)
df = df.replace('nan', np.NaN, regex=True)


# In[220]:


#remove quotes from these columns
try:
    df['Topic_tag'] = df['Topic_tag'].str.rstrip('"')
    df['Topic_tag'] = df['Topic_tag'].str.lstrip('"')

    df['Location'] = df['Location'].str.rstrip('"')
    df['Location'] = df['Location'].str.lstrip('"')
    
    #remove spaces
    df['Topic_tag'] = df['Topic_tag'].str.strip()
    df['Location'] = df['Location'].str.strip()
except Exception as e:
    print(str(e))


# In[221]:


#filter Inst_link column only to include instagram website
for i, row in df.iterrows():
    for ele in str(row.Inst_link).split("', '"):
        if ele.startswith('https://www.instagram'):
#             print(ele)
            row['Inst_link'] = ele


# In[222]:


#if the cell includes a link that starts with "https://www.instagram", the cell should include only the link to instagram account. 
#f not, it will include more than one link. Just in case, let's check if all the cells that includes "," does not contain 
#https://www.instagram", and also check if all the cells that has no "," includes "https://www.instagram"

##SANITY CHECK
#check if there's any cell that contains "https://www.instagram" but has "," - if anything appears, error
check1 = df[(df['Inst_link'].str.contains('https://www.instagram')) & (df['Inst_link'].str.contains(','))]

#check if there's any cell that does not contain "https://www.instagram" but has not "," - if anything appears, error
check2 = df[(df['Inst_link'].str.contains('https://www.instagram') == False) & (df['Inst_link'].str.contains(',') == False)]

#replace Inst_link value that does not have "https://www.instagram" but have ","
for i, row in df.iterrows():
    if "," in str(row['Inst_link']) and "https://www.instagram" not in str(row['Inst_link']):
        row['Inst_link'] = np.NaN


# In[223]:


#extract username from instagram link column
df['Username'] = df.Inst_link.str.split('/').str[-1]


# In[224]:


df = df.replace('nan', np.NaN, regex=True)


# In[225]:


#drop duplicates and reset index
#dropped duplicate based on Instagram username instead of influencer name, considering one person might have multiple accounts
df = df.drop_duplicates(['Inst_link']).reset_index(drop=True)


# In[226]:


#SANITY CHECK
# check duplicate in instagram link
link_dup_bool = df['Inst_link'].duplicated().any()
#check to see instagram_id is in instagram_link
Username_value = set(df['Username'].unique())
df['sanity_temp'] = df['Inst_link'].map(lambda x : True if x in Username_value  else False)
df['sanity_temp'].nunique


# In[227]:


del df['sanity_temp']


# In[228]:


#drop if any cell in Inst_link is empty
df = df[df['Inst_link'].notna()]


# In[230]:


df.to_csv('Health_Influencer_v2.csv', index=False)


# In[231]:


df = pd.read_csv('Health_Influencer_v2.csv')

df


# In[203]:


df[~df['Inst_link'].str.contains('https://www.instagram')]

