from bottle import run, get, post, request, response, redirect # or route

skrivnost = 'te skrivnosti ne bo nihče uganil!'


# zahtevek GET s formo
@get('/prijava') # lahko tudi @route('/prijava')
def prijavno_okno():
    if request.get_cookie('uime', secret=skrivnost):
        redirect('/dobrodosel/')
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
        response.set_cookie('uime', uime, path='/', secret=skrivnost)
        redirect('/dobrodosel/')
    else:
        return '''<p>Napačni podatki za prijavo.
Poskusite <a href="/prijava">še enkrat</a></p>'''


@get('/dobrodosel/')
def dobrodosel():
    uime = request.get_cookie('uime', secret=skrivnost)
    if not uime:
        redirect('/prijava')
    return '<p>Dobrodošel {0}.</p> <form action="/odjava/" method="post"><input type="submit" value="Odjava" /></form>'.format(uime)


@post('/odjava/')
def odjava():
    response.delete_cookie('uime', path='/')
    redirect('/prijava')


@get("/google")
def google():
    q = request.query.q
    return f"""
    <html>
        <form action="/google" method="GET">
            <input name="q" type="text" />
            <input type="submit" value="Išči" />
        </form>

        <a href="https://www.google.com/search?q={q}">Poguglaj {q}!</iframe>
    </html>
    """

def preveri(uime, geslo):
    return uime=="janez" and geslo=="kranjski"

run(host='localhost', port=8080, debug=True, reloader=True)
