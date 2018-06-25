import csv
from numpy import vstack,array
import os
from scipy.cluster.vq import kmeans,vq
from flask import Flask, render_template, request
import collections
import ibm_db_dbi
import io

app = Flask(__name__)

cnxn = ibm_db_dbi.connect("####", "", "")
if cnxn:
    print('database connected')

@app.route('/')
def index():
    return render_template('index.html')



@app.route('/upload', methods=['POST', 'GET'])
def graph():
    if request.method == 'POST':
        x=request.form['col1']
        y=request.form['col2']
        k=int(request.form['noclu'])
        print(x)
        print(y)
        print(k)

        sample = []
        f = csv.reader(open('minnow.csv', "r"), delimiter=",")
        headers = next(f)
        x = headers.index(x)
        y = headers.index(y)
        count = 0
        next(f, None)
        for row in f:
            value = []
            if row[x] != '' and row[y] != '':
                value.append(float(row[x]))
                value.append(float(row[y]))
                sample.append(value)
                count = count + 1

        data = vstack(sample)
        result=[]
        centroids, _ = kmeans(sample, k)
        print(_)
        print(centroids)
        idx, _ = vq(data, centroids)
        label = collections.Counter(idx)
        print(label)


        def centroiddist(centroids):
            i = 0
            cal_cen = []
            for items in centroids:
                i += 1
                x = items[0]
                y = items[1]
                count = 0
                for item in centroids:
                    if count < i:
                        count += 1
                        continue

                    a = item[0]
                    b = item[1]
                    cal_cen.append((((x - a) * 2) + ((y - b) * 2)) * 0.5)


            return cal_cen



    centdist1=centroiddist(centroids)
    print(centdist1)
    return render_template('index.html', cent=centroids, lab=label, cdist=centdist1)

@app.route('/farerange', methods=['POST', 'GET'])
def insert_table():

   cursor = cnxn.cursor()

   if request.method == 'POST':
       x = request.form['fare1']
       y = request.form['fare2']

       cursor.execute("select count(*) from minnow where fare between ? and ?", (x,y,))
       row = cursor.fetchall()
       print(row)

   return render_template('index.html',ffares=row)

if __name__ == '__main__':
    app.run(debug = True)

port = int(os.getenv('PORT', 5000))

