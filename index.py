# coding:utf-8

from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import codecs
import os
import random
import json
import urllib.request
from flask import make_response


app = Flask(__name__)
app.config['SECRET_KEY'] = '\xd5\xb4U\xf7RX\xd0\x10\xbfw\xbb\xbf0\xefD\xb9@\xe7\x90\xec?\xaa:\x8f'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/uid_rec')
def uid_rec():
    rec_five = []
    uid_list = []
    session.permanent = True
    # try:
    #     session.pop('uid_list')
    #     uid_list = session.get('uid_list')
    #     print("uid_list from session")
    # except:
    with codecs.open("UserMovie_test2.txt", "r", "utf-8") as f:
        for line in f.readlines():
            array = line.strip().split()
            uid_list.append(array[0])
    uid_list = list(set(uid_list))
    # session['uid_list'] = uid_list
    while True:
        m = random.choice(uid_list)
        rec_five.append(m)
        if len(rec_five) == 5:
            break
    data = dict()
    data['uid_rec'] = rec_five
    # return render_template('index.html', rec_five=rec_five)
    return json.dumps(data)


@app.route('/movie')
def movie():
    return render_template('movie.html')


@app.route('/movies_rec', methods=['POST', 'GET'])
def movies_rec():
    session.permanent = True
    uid = ''
    if request.method == 'GET':
        uid = request.values.get("uid")
    # session['mid_info'] = data
    try:
        data = session.get(uid)
        print("mid_info from session")
        return data
    except Exception as e:
        print("not from session")
        data = ''
        with codecs.open("user_movie_rec.txt", "r", "utf-8") as f:
            for line in f.readlines():
                array = line.strip().split("\t")
                if array[0] == uid:
                    result = array[1]
                    mids = result.split(",")[:1]
                    for m in mids:
                        p_url = pic_url(m)
                        if p_url:
                            data = dict()
                            movie_dict = dict()
                            data['uid'] = uid
                            md = pic_url(m)
                            if 'movies' not in data:
                                data['movies'] = []
                                movie_dict['mid'] = m
                                movie_dict['picurl'] = md['picurl']
                                movie_dict['title'] = md['title']
                                movie_dict['year'] = md['year']
                                movie_dict['rating'] = md['rating']
                                movie_dict['summary'] = md['summary']
                                movie_dict['countries'] = md['countries']
                                movie_dict['genre'] = md['genre']
                                movie_dict['subtype'] = md['subtype']
                                data['movies'].append(movie_dict)
                            else:
                                movie_dict['mid'] = m
                                movie_dict['picurl'] = md['picurl']
                                movie_dict['title'] = md['title']
                                movie_dict['year'] = md['year']
                                movie_dict['rating'] = md['rating']
                                movie_dict['summary'] = md['summary']
                                movie_dict['countries'] = md['countries']
                                movie_dict['genre'] = md['genre']
                                movie_dict['subtype'] = md['subtype']
                                data['movies'].append(movie_dict)
        # return render_template('index.htm l', result=result)
        data = json.dumps(data)
        session[uid] = data
        return data


# @app.route('/get_pic', methods=['POST', 'GET'])
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
        # directors = get_directors(njson, 'directors')
        # starring = get_casts(njson)
        movie_dict['picurl'] = picurl
        movie_dict['title'] = title
        movie_dict['year'] = year
        movie_dict['rating'] = rating
        movie_dict['summary'] = summary
        movie_dict['mid'] = mid
        movie_dict['countries'] = countries
        movie_dict['genre'] = genre
        movie_dict['subtype'] = subtype
        return movie_dict
    except Exception as e:
        print('404')
        return False


if __name__ == '__main__':
    app.run(debug=True)
    # app.run()
    # test()
    # uid_rec()
