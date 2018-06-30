#!/usr/bin/env python
html_body = """
<html><body>
<h1>querytest</h1>
foo = %s
</body></html>"""

import cgi
form=cgi.FieldStorage()    # (1)
print("Content-type: text/html\n")
print(html_body % form.getvalue('foo', 'N/A'))      # (2)