import pandas as pd
import numpy as np
import re

df = pd.read_csv('anime.csv')
print(df)

top_5 = df.head()
print(top_5)

title = df.loc[3]['Title']
print(title)

def extract_episodes(txt):
    data = ""
    check = False

    for ch in txt:
        if ch == ')':
            break
        if ch == '(':
            check = True
            continue   
        if check == True:
            data += ch
    return data

df['episodes'] = df['Title'].apply(extract_episodes)
print(df)
df['episodes'] = df['episodes'].str.replace("eps", "")
df['episodes'] = df['episodes'].astype(int)

def extract_time(txt):
    data = ""
    for i in range(len(txt)):
        if txt[i] == ')':
            for j in range(i+1, i+20):
                data += txt[j]
    return data
df['Total Time'] = df['Title'].apply(extract_time)
print(df)

def extract_months_only(title_string):
    MONTH_ONLY_PATTERN = r'([A-Z][a-z]{2,3})(?=\s?\d{4})'
    months_list = re.findall(MONTH_ONLY_PATTERN, title_string)
    return months_list

df['Months_only'] = df['Total Time'].apply(extract_months_only)
print(df)

top_anime = df[df['Score'] == df['Score'].max()]


top_5 = df.sort_values('Score', ascending=False).head(5)
print(top_5)

highest_epi = df[df['episodes'] == df['episodes'].max()]
print(highest_epi)

top_5 = df.sort_values('episodes', ascending=False).head(5)
print(top_5)

longest = df[df['episodes'] == df['episodes'].max()]
print(longest)



