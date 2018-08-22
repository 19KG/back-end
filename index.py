# coding:utf-8

from flask import Flask, render_template, request, redirect, url_for, session
from flask_cors import CORS
import codecs
import random
import json
import os
import urllib.request
import pickle
import explanation


app = Flask(__name__)
CORS(app)
uid_list = []
uid2rec = dict()
uid_mid_rec = dict()
mid2dou = ''
exp = explanation.explan()
with codecs.open("ripple_result.txt", "r", "utf-8") as f:
    count = 0
    for line in f.readlines()[1000:1020]:
        array = line.strip().split("\t")
        if os.path.exists("uid_mid_rec.pkl"):
            with open("uid_mid_rec.pkl", "rb") as f:
                uid_mid_rec = pickle.load(f)
        else:
            result_exp = exp.get_explanation(line.strip())
            uid_mid_rec[array[0]] = result_exp
        uid2rec[array[0]] = array[1]
        uid_list.append(array[0])
        count += 1
        print(count)
    if not os.path.exists("uid_mid_rec.pkl"):
        with open("uid_mid_rec.pkl", "wb") as wf:
            pickle.dump(uid_mid_rec, wf)


@app.route('/')
def index():
    r = dict()
    r['status'] = 'error'
    r['massage'] = '没有该路径'
    return json.dumps(r)


@app.route('/uid_rec')
def uid_rec():
    global uid_list
    rec_five = []
    while True:
        m = random.choice(uid_list)
        rec_five.append(m)
        if len(rec_five) == 5:
            break
    data = dict()
    data['uid_rec'] = rec_five
    return json.dumps(data)


@app.route('/movies_rec', methods=['POST', 'GET'])
def movies_rec():
    global uid2rec
    global uid_mid_rec
    global mid2dou
    global uid_list
    if os.path.exists("movie.pkl"):
        with open("movie.pkl", "rb") as f:
            mid2dou = pickle.load(f)
    uid = ''
    if request.method == 'GET':
        uid = request.values.get("uid")
    data = dict()
    # data_pkl = dict()
    data['uid'] = uid
    data['movies'] = []
    if uid in uid2rec:
        result = uid2rec[uid]
        mids = result.split(",")[10:15]
        md = ''
        for m_index, m in enumerate(mids):
            movie_dict = dict()
            if not mid2dou or m not in mid2dou:
                md = pic_url(m)
                if md == 0:
                    r = dict()
                    r['status'] = 'error'
                    r['massage'] = '无法从豆瓣获得电影信息'
                    return json.dumps(r)
                mid2dou[m] = md
                with open("movie.pkl", "wb") as f:
                    pickle.dump(mid2dou, f)
            else:
                print("mid_info from session")
                md = mid2dou[m]
            movie_dict['mid'] = m
            movie_dict['picurl'] = md['picurl']
            movie_dict['title'] = md['title']
            movie_dict['year'] = md['year']
            movie_dict['rating'] = md['rating']
            movie_dict['summary'] = md['summary']
            movie_dict['countries'] = md['countries']
            movie_dict['genre'] = md['genre']
            movie_dict['subtype'] = md['subtype']
            movie_dict['directors'] = md['directors']
            movie_dict['starring'] = md['starring']
            try:
                movie_dict['explanation'] = uid_mid_rec[uid][uid+'_'+m][0]
                rel = []
                # print(uid_mid_rec[uid][uid+'_'+m][1][0][1])
                for i, p in enumerate(uid_mid_rec[uid][uid+'_'+m][1][0]):
                    if (i+1) % 2 and (i+2) < len(uid_mid_rec[uid][uid+'_'+m][1][0]):
                        pair = dict()
                        pair['source'] = uid_mid_rec[uid][uid+'_'+m][1][0][i]
                        pair['target'] = uid_mid_rec[uid][uid+'_'+m][1][0][i+2]
                        rel.append(pair)
                movie_dict['relation'] = rel
                rel = []
                for p in uid_mid_rec[uid][uid+'_'+m][1][1]:
                    e_dict = dict()
                    e_dict['name'] = p
                    rel.append(e_dict)
                movie_dict['entity_data'] = rel
            except Exception as e:
                print("获取解释错误")
            data['movies'].append(movie_dict)
            data['status'] = 'success'
    else:
        r = dict()
        r['status'] = 'error'
        r['massage'] = '用户ID不在数据库中，请重新选择用户ID'
        return json.dumps(r)
    return json.dumps(data)


def pic_url(m):
    mid = m
    html = r'https://api.douban.com/v2/movie/subject/'
    # mid = '6984039'
    url = html + mid
    movie_dict = dict()
    try:
        # url = 'https://movie.douban.com/subject/10569151/'
        hjson = json.loads(urllib.request.urlopen(url).read())
        title = hjson['title']
        year = hjson['year']
        rating = hjson['rating']['average']
        picurl = hjson['images']['large']
        summary = hjson['summary'][:-3]
        mid = hjson['id']
        countries = hjson['countries'][0]
        genre = hjson['genres'][0]
        subtype = hjson['subtype']
        directors = get_directors(hjson, 'directors')
        starring = get_casts(hjson)
        movie_dict['picurl'] = picurl
        movie_dict['title'] = title
        movie_dict['year'] = year
        movie_dict['rating'] = rating
        movie_dict['summary'] = summary
        movie_dict['mid'] = mid
        movie_dict['countries'] = countries
        movie_dict['genre'] = genre
        movie_dict['subtype'] = subtype
        movie_dict['directors'] = directors
        movie_dict['starring'] = starring
        return movie_dict
    except Exception as e:
        print('404')
        return 0


def get_directors(json_object, field):
    people_body = json_object[field]
    num = len(json_object[field])
    people = ""
    for i in range(num):
        pname = people_body[i]['name']
        people = people + pname +','
    people = people[:-1]
    # print(directors)
    return people


def get_casts(json_object):
    people_body = json_object['casts']
    num = len(json_object['casts'])
    people = ""
    for i in range(num):
        pname = people_body[i]['name']
        people = people + pname +','
    people = people[:-1]
    # print(directors)
    return people


if __name__ == '__main__':
    app.run(debug=True)
    # app.run()
    # test()
    # uid_rec()
    # pic_url('19416944')
