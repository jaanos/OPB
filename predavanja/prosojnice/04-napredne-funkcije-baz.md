---
marp: true
style: "@import url('style.css')"
plugins: mathjax
---

# Napredne funkcionalnosti na bazah

* Namestitev Linuxa, PostgreSQL
* Uporabniki, vloge ter dostop
* Indeksi
* Transakcije
* Določanje dostopa
* Shranjene funkcije
* Prožilci (*triggers*)
* Pogledi (*views*)
* Ogledali si bomo na RDBMS PostgreSQL

---

# Namestitev Linuxa

* Virtualizacija: zaganjanje drugega operacijskega sistema (celotnega računalnika) kot programa.
* VirtualBox - program za virtualizacijo (Oracle).
* Iz spleta naložimo program [VirtualBox](https://www.virtualbox.org/).
* Iz spleta naložimo sliko `.iso` za namestitev operacijskega sistema [Linux Ubuntu Server](https://www.ubuntu.com/download/server).
* Po [navodilih](https://linuxhint.com/install-ubuntu22-04-virtual-box/) nastavimo virtualni računalnik in namestimo Linux.
* POZOR: za uporabnika nastavimo uporabniško ime `ubuntu` in dogovorjeno geslo.

---

# Osnovno delo v terminalu

* Namestili smo *Ubuntu Server*, ki omogoča samo terminalski dostop.
* Lahko bi si namestili *Ubuntu Desktop*, ki ponuja tudi uporabo preko grafičnega vmesnika.  
* V terminal se po zagonu prijavimo kot uporabnik `ubuntu`.
* Uporabnik `ubuntu` je član skupine `sudoers` in lahko preko ukaza `sudo` izvaja operacije s pravicami administratorja.
* Spoznamo se z nekaj [osnovnimi ukazi](https://help.ubuntu.com/community/Beginners/BashScripting#Commands) v ukazni lupini `bash`.

---

# Pomembni ukazi v `bash`

* `pwd` - v kateri mapi se nahajamo
* `ls` - izpis vsebine mape (`ls -l`, `ls -lt`)
* `cd` - spremeni mapo (`cd podmapa`, `cd ..`, `cd /home/ubuntu`, `cd`, ...)
* `cp` - kopiranje (`cp datoteka1 datoteka2`, `cp -r pot/do/mape pot/do/cilja`)
* `mv` - premikanje oz. preimenovanje (`mv datoteka1 datoteka2`, `mv mapa1 pot/do/mape2`)
* `rm` - briši (`rm datoteka`, `rm -r mapa`)
* `nano` - preprost tekstovni urejevalnik (`nano pot/do/datoteke.txt`)
* `sudo` - izvajanje ukazov z administratorskimi pravicami

---

# [Namestitev PostgreSQL](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-22-04)

* Nameščanje na Ubuntu izvajamo preko paketnega sistema in ukaza `apt`.
  ```bash
  sudo apt update
  sudo apt install postgresql postgresql-contrib
  ```
* Ob namestitvi se na sistemu ustvari uporabnik `postgres`, ki je tudi administrator na bazi.
* Vstop v vlogo (uporabnika) `postgres`:
  ```bash
  sudo -i -u postgres
  ```

<!-- ## Ukazi na sistemu -->

<!-- - Ustvarjanje uporabnika v `bash` (interaktivno, navedemo pravice). -->
<!-- ```bash -->
<!-- createuser --interactive -->
<!-- ``` -->
<!-- - Vstop v vlogo (uporabnika). -->
<!-- ```bash -->
<!-- sudo -i -u uporabnisko_ime -->
<!-- ``` -->
<!-- - Izhod iz vloge. -->
<!-- ```bash -->
<!-- exit -->
<!-- ``` -->
<!-- - Ustvarjanje baze. -->
<!-- ```bash -->
<!-- createdb ime_baze -->
<!-- ``` -->

---

# Program `psql`

* Program za priklop na bazo - `psql`. Priklop na bazo kot uporabnik `postgres`.
  ```bash
  psql
  ```
* Poln ukaz za priklop (glej tudi `man psql`).
  ```bash
  psql -h baza.fmf.uni-lj.si -U student banka
  ```
* `\q` - izhod
* `\h` - pomoč glede ukazov v SQL
* `\conninfo` - parametri priklopa na bazo
* `\du` - pregled vlog na bazi
* `\d` - pregled tabel
* `\?` - pomoč z izpisom vsah ukazov v `psql`

---

# Uporabniki na bazi

* Na bazo se priklopimo z zadostnimi pravicami.
* Npr. na Linuxu pod uporabniškim imenom `postgres` zaženemo klienta `psql`.
* Ustvarjanje uporabnika:
  ```sql
  CREATE USER uporabnisko_ime
    WITH ENCRYPTED PASSWORD '********';
  ```
* PostgreSQL pozna uporabnike in skupine, ampak jih enovito uporablja preko posplošitve (vloge) - `ROLE`.
* Uporabnika definiramo lahko tudi takole:
  ```sql
  CREATE ROLE ime_vloge WITH LOGIN;
  ```
* Vlogam dodeljujemo pravice, vlogo lahko obravnavamo kot uporabnika (če ima pravico `WITH LOGIN`) ali kot skupino.

---

# Vloge

* Ustvarjanje vloge:
  ```sql
  CREATE ROLE ime_vloge;
  ```
* Brisanje vloge:
  ```sql
  DROP ROLE ime_vloge;
  ```
* Brisanje neobstoječe vloge vrne napako. Lahko uporabnimo tole:
  ```sql
  DROP ROLE IF EXISTS ime_vloge;
  ```

---

# [Določanje pravic vlogam](https://www.digitalocean.com/community/tutorials/how-to-use-roles-and-manage-grant-permissions-in-postgresql-on-a-vps--2)

* Ustvarjanje vloge z dodelitvijo pravice prijave:
  ```sql
  CREATE ROLE demo_role WITH LOGIN;
  ```
* Popravek pravice prijave:
  ```sql
  ALTER ROLE ime_vloge WITH NOLOGIN;
  ```

---

# Ustvarjanje podatkovnih baz 

* Na bazo moramo biti priklopljeni kot uporabnik z dovolj pravicami (npr. administrator `postgres`)
  ```sql
  CREATE DATABASE ime_baze;
  ```
* Ustvarimo novo bazo, se priklopimo nanjo in preverimo priklop.
  ```sql
  CREATE DATABASE nova;
  \c nova
  \conninfo
  ```
* Ustvarimo novo tabelo in nekaj vnosov.
  ```sql
  CREATE TABLE oseba (emso TEXT PRIMARY KEY,
                      ime TEXT, priimek TEXT);
  INSERT INTO oseba (emso, ime, priimek)
       VALUES ('1234', 'Janez', 'Novak');
  ```

---

# [Dodelitev pravic na vloge](https://www.digitalocean.com/community/tutorials/how-to-use-roles-and-manage-grant-permissions-in-postgresql-on-a-vps--2)

* Splošen ukaz za dodelitev pravice:
  ```sql
  GRANT tip_pravice ON tabela TO ime_vloge;
  ```
* Dodelitev pravice popravljanja na tabeli uporabniku:
  ```sql
  GRANT UPDATE ON tabela TO uporabnik;
  ```
* Dodelitev vseh pravic na tabeli uporabniku:
  ```sql
  GRANT ALL ON tabela TO uporabnik;
  ```

---

# [Odvzemanje pravic vlogam](https://www.digitalocean.com/community/tutorials/how-to-use-roles-and-manage-grant-permissions-in-postgresql-on-a-vps--2)

* Odvzemanje pravic:
  ```sql
  REVOKE tip_pravice ON tabela FROM ime_vloge;
  ```
* Primer: onemogočanje vstavljanja vsem uporabnikom (ki nimajo ustrezne pravice dodeljene na drug način):
  ```sql
  REVOKE INSERT ON tabela FROM PUBLIC;
  ```

---

# Sheme

* Uporabniki in vloge so vidne preko celotnega Postgres RDBMS.
* S `psql` ali kakim drugim klientom (npr. pgAdmin 4) se lahko priklopimo na točno določeno bazo.
* Sheme so imenski prostori znotraj ene podatkovne baze, v katerih živijo tabele in drugi logični objekti (npr. števci, shranjene funkcije).
* Uporabljamo jih za lažje določanje pravic na tabelah, boljšo logično organizacijo objektov in razreševanje imenskih konfliktov.
* Ko ustvarimo neko podatkovno bazo, se ustvari tudi shema `public`, v kateri so nove tabele.
* Na tabele na podatkovni bazi se sklicujemo v obliki `ime_sheme.ime_tabele`.

---

# Primer

* Ustvarimo uporabnika `janez`.
  ```sql
  CREATE USER janez WITH ENCRYPTED PASSWORD 'pomlad';
  ```
* Poglejmo obstoječe uporabnike.
  ```sql
  \du
  ```
* Odjavimo se in poskusimo priklopiti na bazo.
  ```bash
  psql -h localhost -U janez nova
  ```
* Poizvedba ni možna:
  ```sql
  SELECT * FROM oseba;
  ```

---

# Primer

* Odjavimo se in prijavimo kot uporabnik `postgres`.
  ```bash
  psql nova
  ```
* Izvedemo naslednje:
  ```sql
  REVOKE ALL ON DATABASE nova FROM PUBLIC;
  GRANT CONNECT ON DATABASE nova TO janez;
  GRANT USAGE ON SCHEMA public TO janez;
  GRANT ALL ON ALL TABLES IN SCHEMA public TO janez;
  GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO janez;
  ```
* Preverimo pravice na bazi, shemi in tabelah na bazi.
  ```sql
  \l
  \dn+
  \dp
  ```

---

# Vloge kot skupine

* Ustvarjanje skupine in dodajanje uporabnikov:
  ```sql
  CREATE ROLE skupina;
  GRANT skupina TO uporabnik1;
  GRANT skupina TO uporabnik2;
  ```
* V resnici dajamo lahko "vloge na vloge" - tako kot bi dajali skupine v skupine, uporabnike pa si predstavljamo kot elementarne skupine s pravico priklopa.
* Uporabnik v neki skupini se začne obnašati skladno z vlogo, če to vklopimo:
  ```sql
  SET ROLE skupina;
  ```

---

# Skupine

* Vrnimo se v osnovno vlogo:
  ```sql
  RESET ROLE;
  ```
* Lahko pa uporabniku posebej nastavimo, da avtomatično podeduje pravice iz skupin/vlog (privzeto).
  ```sql
  ALTER ROLE uporabnik INHERIT;
  ```
* To pomeni: če uporabniku nastavimo lastnost `INHERIT`, mu ni treba vsakič "skakati" v vloge s pomočjo `SET ROLE`, ampak se pravice iz vseh vlog, katerih član je, avtomatično upoštevajo.

---

# Primer - dovoljevanje dostopa preko skupine

* Odjavimo se in se prijavimo kot uporabnik `postgres`.
  ```bash
  psql nova
  ```
* Izvedimo naslednje:
  ```sql
  CREATE ROLE novaadmini;
  REVOKE ALL ON DATABASE nova FROM PUBLIC;
  GRANT CONNECT ON DATABASE nova TO novaadmini;
  GRANT USAGE ON SCHEMA public TO novaadmini;
  GRANT ALL ON ALL TABLES IN SCHEMA public
     TO novaadmini;
  GRANT ALL ON ALL SEQUENCES IN SCHEMA public
     TO novaadmini;
  \l
  \dn+
  \dp
  ```

---

# Primer - dovoljevanje dostopa preko skupine

* Uporabniku dodelimo pravico.
  ```sql
  CREATE USER metka WITH ENCRYPTED PASSWORD 'pomlad';
  ALTER ROLE metka NOINHERIT;
  GRANT novaadmini TO metka;
  \du
  ```
* Če želimo ohranjanje privzetih pravic na novih objektih:
  ```sql
  ALTER DEFAULT PRIVILEGES
    FOR ROLE metka IN SCHEMA public
  GRANT ALL ON TABLES TO novaadmini;

  ALTER DEFAULT PRIVILEGES
    FOR ROLE metka IN SCHEMA public
  GRANT ALL ON SEQUENCES TO novaadmini;
  ```

---

# Lažji oddaljen priklop na bazo

* Tipično imamo podatkovno bazo na nekem strežniku.
* Lahko se sicer priklopimo nanjo preko programa `psql` (ukazna vrstica).
* Tipkanje v terminalu `psql` je velikokrat nepriročno.
* Najbolj priročno je do baze dostopati preko ustreznih aplikacij z grafičnim vmesnikom.
* Primer take aplikacije: phpPgAdmin (<http://baza.fmf.uni-lj.si>), ki se uporablja na vajah.

---

# Konfiguracija strežnika za oddaljen dostop

* Najprej popravimo datoteko `postgresql.conf`.
* Lokacijo najdemo z ukazom
  ```bash
  psql -U postgres -c 'SHOW config_file'
  ```
* S pomočjo urejevalnika `nano` popravimo ustrezno vrstico na:
  ```bash
  listen_addresses = '*'
  ```
  - Urejevalnik zaženemo npr. kot
    ```bash
    nano /etc/postgresql/14/main/postgresql.conf
    ```

---

# Oddaljen dostop - konfiguracija

* Lokacijo konfiguracijske datoteke `pg_hba.conf` najdemo z ukazom
  ```bash
  psql -U postgres -c 'SHOW hba_file'
  ```
* S pomočjo urejevalnika `nano` popravimo vrstico oblike 
  ```bash
  host    all     all     127.0.0.1/32   scram-sha-256
  ```
  v vrstico
  ```bash
  host    all     all     0.0.0.0/0      scram-sha-256
  ```
  - Urejevalnik zaženemo npr. kot
    ```bash
    nano /etc/postgresql/14/main/pg_hba.conf
    ```

---

# Oddaljen dostop - konfiguracija

* Da uveljavimo nove nastavitve, ponovno zaženemo strežnik (kot uporabnik `ubuntu`):
  ```bash
  service postgresql restart
  ```
* Za ustavljanje in zagon RDBMS PostgreSQL lahko uporabimo podoben ukaz (namesto parametra `restart` lahko uporabimo parametra `stop` oz. `start`).

---

# PgAdmin 4 

* Namizna alternativa: program *PgAdmin 4* (namestimo iz: <https://www.pgadmin.org/download/>).
* V programu konfiguriramo povezavo podobno kot v `psql`.
* Namesto ukazov v `psql` oblike `\ukaz` imamo grafične preglede in ukaze preko menijev.
* Poizvedbe izvajamo preko orodja *Query tool*.

---

# Priklop preko PgAdmin 4

* Virtualni strežnik mora imeti mrežni vmesnik nastavljen na `Bridged Adapter`, t.j., na isti mreži, kot je naš računalnik.
* Za priklop rabimo naslov strežnika (`host`), uporabnika (`user`), njegovo geslo in ime podatkovne baze, na katero se priklapljamo.
* IP številko virtualnega računalnika dobimo z ukazom v terminalu:
  ```bash
  ip address
  ```
* Preden omogočimo uporabniku `postgres` (t.j., administratorju) oddaljen priklop, mu moramo nastaviti geslo (dvakrat vnesemo novo geslo):
  ```bash
  psql
  \password
  ```

* V nadaljevanju bomo komunicirali s podatkovno bazo preko PgAdmin 4.

---

# Indeksi

* Iskanje po splošnem stolpcu v podatkovni bazi zahteva $O(n)$ časa.
* Če je podatkovni tip stolpca linearno urejena množica, lahko nad vrsticami stolpca izgradimo iskalno strukturo, ki omogoča iskanje v $O(1)$ ali $O(\log n)$.
* Strukturo imenujemo *indeks*.

---

# Indeksi - primer

* Ustvarimo tabelo.
  ```sql
  CREATE TABLE tabela (
    id INTEGER,
    vsebina TEXT
  );
  ```
* Na stolpcu `id` ustvarimo indeks.
  ```sql
  CREATE INDEX index1 ON tabela (id);
  ```
* Poglejmo, kakšne indekse imamo.
  ```sql
  \di
  ```

---

# Indeksi

* Vzdrževanje indeksov zahteva določeno dodatno delo (ob vsakem popravku baze).
* Odstranjevanje indeksa:
  ```sql
  DROP INDEX index1;
  ```
* Tipi indeksov:
  - B-tree: linearno urejene množice
  - Hash: zgoščena tabela. Možno samo iskanje po enakosti.
  - GiST, SP-GiST, GIN, ...
* Primer:
  ```sql
  CREATE INDEX ime_indeksa ON tabela USING hash (stolpec);
  ```

---

# Indeksi

* Indekse se lahko naredi za več stolpcev.
  ```sql
  CREATE INDEX ime_indeksa
      ON tabela (stolpec1, stolpec2);
  ```
* Primarni in sekundarni ključi so že indeksirani.
* Indeksi na izrazih nad stolpci:
  ```sql
  CREATE INDEX users_lower_email ON users(lower(email));
  ```
* Tak indeks omogoča hitro iskanje po pogojih oblike `WHERE lower(email) = ??`

---

# Transakcije

* Lastnosti transakcij - ACID:
    - Atomarnost: vse operacije v transakciji izvedene ali zavrnjene.
    - Konsistentnost: pred in po transakciji je stanje v bazi konsistentno.
    - Izolacija: transakcije so izolirane med seboj in medsebojni vpogled ni mogoč.
    - Trajnostnost: rezultat transakcije je trajno shranjen.
* Ukazi:
    - `BEGIN` ali `BEGIN TRANSACTION` - začetek transakcije
    - `COMMIT` ali `END TRANSACTION` - konec transakcije, shrani spremembe
    - `ROLLBACK` - razveljavi spremembe

---

# Primer

```sql
\c nova
CREATE TABLE blagajna
  (ime TEXT, znesek NUMERIC(10,2));
INSERT INTO blagajna (ime, znesek)
     VALUES ('Janez', 10), ('Metka', 10);
BEGIN;
  UPDATE blagajna SET znesek = znesek - 5 
   WHERE ime = 'Janez';
  UPDATE blagajna SET znesek = znesek + 5 
   WHERE ime = 'Metka';
COMMIT;
```

---

# Nivo izolacije

* Problemi:
  - *umazano branje* - preberemo nepotrjene podatke.
  - *neponovljivo branje* - v transakciji večkrat beremo iste podatke, a se je nek podatek vmes spremenil.
  - *fantomsko branje* - v transakciji večkrat naredimo isto poizvedbo in zaradi spremembe podatkov dobimo več ali manj vrstic.
* Nivoji izolacije:
  ![height:250px](slike/nivoji_izolacije.png)

---

# Nivo izolacije

* Privzeti nivo je `READ COMMITED`.
* Lahko ga nastavimo:
  ```sql
  SET TRANSACTION ISOLATION LEVEL SERIALIZABLE | REPEATABLE READ | 
                                  READ COMMITTED | READ UNCOMMITTED;
  ```

---

# Shranjene funkcije

* Na RDBMS lahko napišemo posebne funkcije v različnih programskih jezikih.
* Prednosti:
  - Zmanjšanje komunikacije s podatkovno bazo
  - Izboljšanje učinkovitosti
  - Souporaba v več bazah
* Slabosti:
  - Počasnejši in težji razvoj programske opreme
  - Težko razhroščevanje, vodenje verzij
  - Težja prenosljivost med različnimi RDBMS
* Razen v posebnih primerih se v veliki večini primerov danes izogibamo uporabe shranjenih funkcij.

---

# [Definicija funkcij](http://www.postgresqltutorial.com/postgresql-create-function/)

* Sintaksa:
  ```sql
  CREATE FUNCTION function_name(p1 type, p2 type)
  RETURNS INTEGER AS
    BEGIN
      -- koda ...
    END;
  LANGUAGE language_name;
  ```

---

# Definicija funkcij - primer

```sql
CREATE FUNCTION povecaj(n INTEGER)
RETURNS INTEGER AS
  $$ 
  BEGIN
    RETURN n + 1;
  END;
  $$
LANGUAGE plpgsql;
```
* Uporaba:
  ```sql
  SELECT povecaj(20);
  ```

---

# Prožilci 

* angl. *trigger* - posebna funkcija, ki je povezana s tabelo.
* Sproži se ob dogodkih, povezanih z operacijami: `INSERT`, `UPDATE`, `DELETE`.
* Lahko se proži za vsak stavek posebej ali za vsako vrstico posebej.
* Lahko se proži pred dogodkom ali po njem.

---

# [Prožilci - primer](http://www.postgresqltutorial.com/creating-first-trigger-postgresql/)

* Ustvarimo tabelo zaposlenih:
  ```sql
  CREATE TABLE zaposleni (
    id      SERIAL PRIMARY KEY,
    ime     TEXT   NOT NULL,
    priimek TEXT   NOT NULL
  );
  ```

---

# [Prožilci - primer](http://www.postgresqltutorial.com/creating-first-trigger-postgresql/)

* Ustvarimo tabelo sprememb:
  ```sql
  CREATE TABLE zaposleni_spremembe (
    id           SERIAL       PRIMARY KEY,
    zaposleni_id INTEGER      NOT NULL,
    priimek      TEXT         NOT NULL,
    spremenjeno  TIMESTAMP(6) NOT NULL
  );
  ```

---

# Prožilci - primer

* Prožilna funkcija:
  ```sql
  CREATE OR REPLACE FUNCTION belezi_spremembe()
  RETURNS trigger AS
  $BODY$
  BEGIN
    IF NEW.priimek <> OLD.priimek THEN
       INSERT INTO zaposleni_spremembe
       (zaposleni_id, priimek, spremenjeno)
	   VALUES (OLD.id, OLD.priimek, now());
	END IF;
	RETURN NEW;
  END;
  $BODY$ LANGUAGE plpgsql;
  ```

---

# Prožilci - primer

* Povezava funkcije s prožilcem:
  ```sql
  CREATE TRIGGER zadnje_spremembe
  BEFORE UPDATE ON zaposleni
     FOR EACH ROW EXECUTE PROCEDURE belezi_spremembe();
  ```

  ```sql
  INSERT INTO zaposleni (ime, priimek)
       VALUES ('Janez', 'Novak');
  INSERT INTO zaposleni (ime, priimek)
       VALUES ('Metka', 'Lepše');  
  SELECT * FROM zaposleni;
  UPDATE zaposleni SET priimek = 'Zelenko' WHERE id = 2;
  SELECT * FROM zaposleni;
  SELECT * FROM zaposleni_spremembe;
  ```

---

# [Pogledi (`VIEW`)](http://www.tutorialspoint.com/postgresql/postgresql_views.htm)

* Virtualne tabele kot rezultat poizvedbe, s katerimi lahko delamo tako kot s pravimi tabelami (poizvedbe, pravice).
* Pogled lahko predstavlja tabelo, ki določenim uporabnikom bolje predstavi podatke, ki jih pogosto povzamemo iz več tabel (npr. seštevki transakcij po računih).
* Uporabnikom lahko dodelimo pravice samo na (izbrane) poglede.
* Pogledi so definirani kot (shranjene) poizvedbe.

---

# [Pogledi (`VIEW`)](http://www.tutorialspoint.com/postgresql/postgresql_views.htm)

* Ustvarjanje pogleda:
  ```sql
  CREATE VIEW ime_pogleda AS
       SELECT ...;
  ```
* Brisanje pogleda:
  ```sql
  DROP VIEW ime_pogleda;
  ```

---

# Pogledi - primer

```sql
CREATE VIEW samo_priimki_zaposlenih AS
     SELECT id, priimek FROM zaposleni;

SELECT * FROM samo_priimki_zaposlenih;
```
