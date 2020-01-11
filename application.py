import sqlite3
import requests
import re
import json
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, redirect, session, url_for,abort
s = requests.session()
conn = sqlite3.connect("crawler.db",check_same_thread=False)
cur = conn.cursor()
app = Flask(__name__)
# x=[]

def locsuggest(loc):
    par_1 = {'input': loc, 'types':''}
    suggest = s.get('https://www.swiggy.com/dapi/misc/places-autocomplete', params = par_1)
    x = json.loads(suggest.text)
    return x


def getlatlong(option,x) :
    option=int(option)
    place_id = x['data'][option]['place_id']
    par_2 = {'place_id': place_id}
    lat_lng = s.get('https://www.swiggy.com/dapi/misc/reverse-geocode', params = par_2)
    y = json.loads(lat_lng.text)
    return y


def getslugs(y):
    par_3 = y['data'][0]['geometry']['location']
    res = s.get('https://www.swiggy.com/dapi/restaurants/list/v5', params = par_3)
    z = json.loads(res.text)
    ttl_open = int(z['data']['cards'][2]['data']['data']['totalOpenRestaurants'])
    slugs = list()
    count = 0
    for i in range(0,15):
        slugs.append(z['data']['cards'][2]['data']['data']['cards'][i]['data']['slugs']['restaurant'])
        count += 1
    for i in range(15,ttl_open,16):
        par_3['offset'] = i
        par_3['pageType'] = 'SEE_ALL'
        par_3['sortBy'] = 'RELEVANCE'
        res_1 = s.get('https://www.swiggy.com/dapi/restaurants/list/v5', params = par_3)
        a = json.loads(res_1.text)
        for j in range(0,16):
            count += 1
            if count > ttl_open:
                break
            slugs.append(a['data']['cards'][j]['data']['data']['slugs']['restaurant'])
    return slugs,ttl_open


def get_items(slug,item):
    price=list()
    name=list()
    resname = list()

    # item = string(item)
    for i in slug :
        res_url = s.get('https://www.swiggy.com/bangalore/'+i)
        soup = BeautifulSoup(res_url.text, 'html.parser')
        b = soup.find_all(class_="_2wg_t")
        for j in b:
            if j.find(class_="jTy8b", string = re.compile(item, re.I)):
                n=j.find(class_="jTy8b", string = re.compile(item, re.I))
                p=j.find(class_="bQEAj")
                r=soup.find(class_="_3aqeL")
                name.append(n.get_text())
                price.append(p.get_text())
                resname.append(r.get_text())

    print(resname,name,price)
    return resname,name,price


@app.route("/", methods = ["GET","POST"])
@app.route("/index", methods = ["GET","POST"])
def index():
    #x=#[]
    if request.method == "GET" :
        return render_template("index.html",p=1)
    else :
        if request.form.get("loc") is not None:
            loc = request.form.get("loc")
        # print(loc)
            if loc:
                try:
                    x = locsuggest(loc)
                    #print(x)
                    return render_template("index.html",x=x, p=2)
                except:
                    return render_template("error.html",error = "enter at least 3 characters")

        option = request.form.get("options")
        # global x
        print(option)
        if option:
            try:
                #print(loc)
                global slug
                global ttlopen
                # global x
                # x = locsuggest(loc)
                # print("hii")
                # print(option,x)
                # latlong = getlatlong(option,x)
                place_id=option
                par_2 = {'place_id': place_id}
                lat_lng = s.get('https://www.swiggy.com/dapi/misc/reverse-geocode', params = par_2)
                print('hii')
                latlong = json.loads(lat_lng.text)
                print(latlong)
                slug,ttlopen=getslugs(latlong)
                print('hi3')
                return render_template("index.html",p=3)
            except:
                return render_template("error.html",error = "Please select an option")

        global item
        dish=request.form.get("dish")
        if dish:
            item = dish
            return render_template("index.html",ttlopen=ttlopen,p=4,x=x)
        tanzy = request.form.get("con")
        if tanzy :
            resname,name,price=get_items(slug,item)

            # resname = list(map(lambda x: x.string,resname))
            # name = list(map(lambda x: x.string,name))
            # price = list(map(lambda x: int(x.string),price))
            # print(resname,name,price)
            for i,j,k in zip(resname,name,price):
                cur.execute("Insert into swiggy(res_name,item_name,price) values (?,?,?)",(i,j,k))
            # conn.commit()
            cur.execute("select * from swiggy order by price")
            conn.commit()
            result = cur.fetchall()
            return render_template("list.html",result = result)












if __name__=='__main__':
    app.run(debug=True)
