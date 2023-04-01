# Web Scraping Tutorial
from cgitb import html
import code
from turtle import title
import requests
from bs4 import BeautifulSoup
url = "https://www.codewithharry.com/"
# *********************     step 1 Get the HTML ********************************

r= requests.get(url)
htmlContent = r.content
# This used for view sourse code
#print(htmlContent)
# ************************ step 2 Parse the HTML ***********************************
soup = BeautifulSoup(htmlContent,'html.parser')
print(soup.prettify())


# step 3 HTML Tree traversal 
# title = soup.title
#$$$$$$$ for print title
#print(title)
# **** Commonly used type of objects
# 1. Tag
# 2. NavigableString
# 3. BeautifulSoup
# 4. Comment
# print(type(title))
# print(type(soup))
# print(type(title.string))
# print(title.string)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# **************************BeautifulSoup documentation************************** 
# print(soup.get_text())

# for link in soup.find_all('a'):
#     print(link.get('href'))
# print(soup.find(id="link3"))
#   print(soup.title.name)
