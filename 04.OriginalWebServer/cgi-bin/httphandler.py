import cgi
import os
import time
_weekdayname = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
_monthname = [None,
              "Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

class Request:    
    """
    HTTPのリクエストをハンドリングするクラス
    CGI側でインスタンスを生成することによって利用する
    クエリデータや環境変数へのアクセス,主要ヘッダへの
    アクセス用メソッドを提供
    """
    def __init__(self, environ=os.environ):
        self.form=cgi.FieldStorage()
        self.environ=environ


class Response:
    """
    HTTPのレスポンスをハンドリングするクラス
    レスポンスを送る前にインスタンスを生成して利用する
    レスポンスやヘッダの内容の保持,ヘッダを含めたレスポンスの
    送信を行う
    """
    def __init__(self, charset='utf-8'):
        self.headers = {'Content-type':'text/html; charset=%s' % charset}
        self.body=''
        self.status=200
        self.status_message=''
    
    def set_headers(self, name, value):
        self.headers[name] = value
    
    def get_headers(self, name):
        return self.headers.get(name, None)
    
    def set_body(self, body_str):
        self.body=body_str
    
    def make_output(self, timestamp=None):
        if timestamp is None:
            timestamp = time.time()
            year, month, day, hh, mm, ss, wd, y, z = time.gmtime(timestamp)
            dt_str="%s, %02d %3s %4d %02d:%02d:%02d GMT" % (
                         _weekdayname[wd], day,
                         _monthname[month], year,
                         hh, mm, ss)
            self.set_headers("Last-Modified", dt_str)
            headers='¥n'.join(["%s: %s" % (k, v)
                               for k,v in self.headers.items()])
        return headers + '\n' + self.body
    
    def __str__(self):
        return self.make_output()
    
def get_htmltemplate():
    html_body=u"""
    <html>
      <head>
        <meta http-equiv="content-type"
              content="text/html;charset=utf-8" />
      </head>
      <body>
      %s
      </body>
    </html>"""
    return html_body
