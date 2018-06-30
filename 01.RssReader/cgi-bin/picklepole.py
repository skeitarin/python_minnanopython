#!/usr/bin/env python 
# coding: utf-8
import pickle
from httphandler import Request, Response, get_htmltemplate
import cgitb; cgitb.enable() 

form_body=u"""
<form method="POST" action="/cgi-bin/picklepole.py">
好きな軽量言語は?<br />
%s
<input type="submit" />
</form>"""

radio_parts=u"""
<input type="radio" name="language" value="%s" />%s
<div style="border-left: solid %sem red; ">%s</div>
"""

lang_dict = {}
try:
    # f=open('./favorite_language.dat')
    # lang_dict=pickle.load(f)
    with open('./data/favorite_language.pickle', mode='rb') as f:
        lang_dict=pickle.load(f)
except IOError:
    pass

content=""
req=Request()
if 'language' in req.form:
    lang=req.form['language'].value
    lang_dict[lang]=lang_dict.get(lang, 0)+1
# f=open('./favorite_language.dat', 'w')
# pickle.dump(lang_dict, f)
with open('./data/favorite_language.pickle', mode='wb') as f:
    pickle.dump(lang_dict, f)


for lang in ['Perl', 'PHP', 'Python', 'Ruby']:
    num=lang_dict.get(lang, 0)
    content+=radio_parts % (lang, lang, num, num)

res=Response()
body=form_body % content
res.set_body(get_htmltemplate() % body)
print(res.make_output())