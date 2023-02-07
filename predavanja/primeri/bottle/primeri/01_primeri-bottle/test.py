
def popravi(niz):
    def izpis(f):
        def popravljena(a, b):
            print(niz, a, b)
            return f(a, b)
        return popravljena
    return izpis
    
@popravi("---")
def sestej(a, b):
    return a + b

@popravi("???")
def odstej(a, b):
    return a - b
