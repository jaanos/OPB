Vzorec za projekt
=================

V datoteki `primer.py` se nahaja minimalen vzorec spletnega vmesnika s strežnikom `bottle.py`,
ki se poveže na bazo ter izpiše rezultate poizvedb.
Šablone za spletne strani se nahajajo v mapi `views`.

V mapi `primer` se nahaja minimalen vzorec spletnega vmesnika s paketom *Shiny*.
Za svoje delovanje potrebuje še paketa `dplyr` in `RPostgreSQL`.

Ker potrebujemo za povezavo na bazo avtentikacijo,
gesel pa nočemo objavljati na repozitoriju,
primera pričakujeta podatke za povezavo v datoteki `auth.py` oziroma `auth.R`.
Ti dve datoteki sta navedeni v `.gitignore`,
da ju ne bi po nesreči dodali v repozitorij.
Primer datoteke s podatki za povezavo
(tako za Python kot tudi za R)
je `auth.template`,
ki jo moramo seveda ustrezno preimenovati,
da bo želena aplikacija delovala.
