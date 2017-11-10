from bottle import run, get, post, request # or route

@get('/prijava') # lahko tudi @route('/prijava')
def prijavno_okno():
    return """
<html>
<head>
<style type="text/css">
body {
  font-family: Verdana
}
.neki {
  font-weight: bold;
  color: red
}
</style>
</head>
<body>
<form action="/prijava" method="post">
    <span class="neki">Uporabniško ime:</span> <input name="uime" type="text" />
    <span style="font-size:xx-large;text-decoration: underline">Geslo:</span> <input name="geslo" type="password" />
    <input value="Prijava" type="submit" />
</form>
</body>
</html>
"""

@post('/prijava') # or @route('/prijava', method='POST')
def prijava():
    uime = request.forms.get('uime')
    geslo = request.forms.get('geslo')
    if preveri(uime, geslo):
        return "<p>Dobrodošel {0}.</p>".format(uime)
    else:
        return '''<p>Napačni podatki za prijavo.
Poskusite <a href="/prijava">še enkrat</a></p>'''


def preveri(uime, geslo):
    return uime=="janez" and geslo=="kranjski"

run(host='localhost', port=8080, debug=True)
