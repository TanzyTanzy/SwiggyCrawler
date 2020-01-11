import sqlite3
import requests
import re
import json
from bs4 import BeautifulSoup
s=requests.session()
slug=list()
inp=input('Enter your location (at least three letters) ')
r=s.get('https://www.swiggy.com/dapi/misc/places-autocomplete?input='+inp+'&types=')
json_data = json.loads(r.text)
for i in range (0,5):
     print(str(i+1)+" "+json_data['data'][i]['description'])
loc_id=int(input('Enter from above places: '))
place_id=json_data['data'][loc_id-1]['place_id']
restaur=s.get("https://www.swiggy.com/dapi/misc/reverse-geocode?place_id="+place_id)
loc=json.loads(restaur.text)
# print(json.dumps(loc,indent=4))
lat=str(loc['data'][0]['geometry']['location']['lat'])
# print(lat)
long=str(loc['data'][0]['geometry']['location']['lng'])
res_list=s.get("https://www.swiggy.com/dapi/restaurants/list/v5?lat="+lat+"1&lng="+long)
rest=json.loads(res_list.text)
count=0
total_open=int(rest['data']['cards'][2]['data']['data']['totalOpenRestaurants'])
for i in range (0,15):
    slug.append(rest['data']['cards'][2]['data']['data']['cards'][i]['data']['slugs']['restaurant'])
    count+=1
for i in range(15,total_open,16):
    rest_list=s.get("https://www.swiggy.com/dapi/restaurants/list/v5?lat="+lat+"1&lng="+long+"&offset="+str(i)+"&sortBy=RELEVANCE&pageType=SEE_ALL")
    all_res=json.loads(rest_list.text)
    # fhand=open('file1.json','w')
    # fhand.write(json.dumps(all_res,indent=4))
    for j in range(0,16):
        count+=1
        if count>total_open:
            break
        slug.append(all_res['data']['cards'][j]['data']['data']['slugs']['restaurant'])
dish=input("Enter the dish ")
# print(slug)
for i in range (0,total_open):
    res_menu=s.get("https://swiggy.com/bangalore/"+slug[i])
    each_menu=BeautifulSoup(res_menu.text,'html.parser')
    item=each_menu.find_all(class_="_2wg_t")
    for j in item:
        name=j.find(class_='jTy8b',string=re.compile(dish))
        # print(name.contents)
        if name!=None:
            # price=i.find(class_='bQEAj')
            price=j.find(lambda tag: tag.name == 'span' and tag.get('class') == ['bQEAj'])
            # print(price.contents)
            print(slug[i],'|',name.get_text(),'|',price.get_text())
            # print(price[y].contents)
