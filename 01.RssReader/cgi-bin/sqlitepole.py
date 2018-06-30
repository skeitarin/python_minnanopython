#!/usr/bin/env python 
# coding: utf-8
import sqlite3
from string import Template
import os
from httphandler import Request, Response, get_htmltemplate
from simpletemplate import SimpleTemplate
import cgitb; cgitb.enable() 

def get_absolute_path(relative_path):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)
    return os.path.normpath(path)

def increment(cur, lang_name):
    cur.execute("SELECT value FROM language_pole WHERE name='{lang}'".format(lang=lang_name))
    item=None
    try:
        for item in cur.fetchall():
            cur.execute("UPDATE language_pole SET value={value} WHERE name='{name}'".format(name=lang_name, value=item[0]+1))
        if item is None:
            cur.execute("INSERT INTO language_pole(name, value) VALUES('{name}', {value})".format(name=lang_name, value=1))
        con.commit()
    except:
        con.rollback()

con=sqlite3.connect(get_absolute_path('../data/favorite_language.sqlite'))
cur=con.cursor()

try:
    cur.execute('CREATE TABLE language_pole (name text, value int);')
except:
    pass

content=""
req=Request()
if 'language' in req.form:
    lang = req.form['language'].value
    increment(cur, lang)

lang_dict = {}
cur.execute("SELECT name, value FROM language_pole;")
for res in cur.fetchall():
    lang_dict[res[0]]=res[1]
cur.close()

lang_list=[]
for lang in ['Perl', 'PHP', 'Python', 'Ruby']:
    num=lang_dict.get(lang, 0)
    lang_list.append([lang, str(num)])

param_dict={'languages':tuple(lang_list)}

renderer=SimpleTemplate(file_path=get_absolute_path('../template/favorite_language.html'))
res=Response()
res.set_body(renderer.render(param_dict=param_dict))
print(res.headers)
print('\n')
print(res.body)