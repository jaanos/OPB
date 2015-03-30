from bottle import route, run

@route('/')
def pozdrav():
    return "Pozdravljeni in dober dan!"

@route('/podstran')
def osnovnaStran():
    return """
<html>
<head>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=utf-8">
<title>Naš strežnik</title>
</head>
<body>
<h1> Pozdravljeni!!! </h1>
To je naš prvi strežnik.
</body>
</html>
"""

@route('/pozdrav/<ime>')
def pozdrav(ime="Tujec"):
    return "Pozdravljen {0}, kako si kaj?".format(ime)

run(host='localhost', port=8080, debug=True)
