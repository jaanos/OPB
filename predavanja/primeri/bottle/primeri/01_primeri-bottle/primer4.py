from bottle import run, get, post, request # or route

# zahtevek GET s formo
@get('/prijava') # lahko tudi @route('/prijava')
def prijavno_okno():
    return """
<html>
<head>
</head>
<body>
<form action="/prijava" method="post">
    <span>Uporabniško ime:</span> <input name="uime" type="text" />
    <span>Geslo:</span> <input name="geslo" type="password" />
    <input value="Prijava" type="submit" />
</form>
</body>
</html>
"""

# zahtevek POST
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
