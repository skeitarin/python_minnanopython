#!/usr/bin/env python
# coding: utf-8
import re
import os

if_pat=re.compile(r"\$if\s+(.*\:)")                
endif_pat=re.compile(r"\$endif")
for_pat=re.compile(r"\$for\s+(.*)\s+in\s+(.*\:)")
endfor_pat=re.compile(r"\$endfor")
value_pat=re.compile(r"\${(.+?)}")

class SimpleTemplate(object):
    """
    シンプルな機能を持つテンプレートエンジン
    """
    def __init__(self, body='', file_path=None):
        if file_path:
            with open(file_path) as f:
                body=f.read()
        body=body.replace('\r\n', '\n')
        self.lines=body.split('\n')
        self.sentences=((if_pat, self.handle_if),
                        (for_pat, self.handle_for),
                        (value_pat, self.handle_value),)
    
    def render(self, param_dict={}):
        l, o=self.process(param_dict=param_dict)
        return o

    def process(self, exit_pats=(), start_line=0, param_dict={}):
        output=''
        cur_line=start_line
        while len(self.lines) > cur_line:
            line=self.lines[cur_line]
            for exit_pat in exit_pats:
                if exit_pat.search(line):
                    return cur_line+1, output
            for pat, handler in self.sentences:
                m=pat.search(line)
                pattern_found=False
                if m:
                    try:
                        cur_line, out=handler(m, cur_line, param_dict)
                        pattern_found=True
                        output+=out
                        break
                    except Exception as e:
                        raise "Following error occured in line {line}\n{ex}".format(line=cur_line, ex=e[0])
            if not pattern_found:
                output+=line+'\n'
            cur_line+=1 
        if exit_pats:
            raise "End of lines while parsing"
        return cur_line, output
    
    def handle_if(self, _match, _line_no, _param_dict={}):
        _cond=_match.group(1)
        if not _cond:
            raise "SyntaxError: invalid syntax in line {line}".format(line=line_no)
        _cond=_cond[:-1]
        locals().update(_param_dict)
        _line, _out=self.process(((endif_pat), ), _line_no+1, _param_dict)
        if not eval(_cond):
            _out=''
        return _line-1, _out

    def handle_for(self, _match, _line_no, _param_dict={}):
        _var=_match.group(1)
        _exp=_match.group(2)
        if not _var or not _exp:
            raise "SyntaxError: invalid syntax in line {line}".format(line=line_no)
        locals().update(_param_dict)
        _seq=eval(_exp[:-1])
        _out=''
        if not _seq:
            return self.find_matchline(endfor_pat, _line_no), _out
        for _v in _seq:
            _param_dict.update({_var:_v})
            _line, _single_out=self.process((endfor_pat, ), _line_no+1, _param_dict)
            _out+=_single_out
        return _line-1, _out

    def handle_value(self, _match, _line_no, _param_dict={}):
        _line=self.lines[_line_no]
        _rep=[]
        locals().update(_param_dict)
        pos=0
        while True:
            _m=value_pat.search(_line[pos:])
            if not _m:
                break
            pos+=_m.end()
            _rep.append(((_m.group(1), eval(_m.group(1)))))
        for t, r in _rep:
            _line=_line.replace('${%s}'%t, r)
        return _line_no, _line+'\n'

    def find_matchline(self, pat, start_line=0):
        cur_line=start_line
        for line in self.lines[start_line:]:
            if pat.search(line):
                return cur_line
            cur_line+=1
        return -1

