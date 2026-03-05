
INSERT INTO oseba (id, ime, rojstvo) VALUES (1, 'Marjan', '1953-7-16');
INSERT INTO oseba (id, ime, rojstvo) VALUES (2, 'Marjan', '1982-9-20');
INSERT INTO oseba (id, ime, rojstvo) VALUES (3, 'Štefan', '1987-6-1');
INSERT INTO oseba (id, ime, rojstvo) VALUES (4, 'Marjan', '1994-7-16');
INSERT INTO oseba (id, ime, rojstvo) VALUES (1, 'Ralf', '1977-7-20'); -- napaka: id 1 ze obstaja
INSERT INTO oseba (id, ime, rojstvo) VALUES (100, 'Ralf', '1977-7-20');
INSERT INTO oseba (id, ime, rojstvo) VALUES (101, 'Hans', '1991-7-20');
INSERT INTO oseba (id, ime, rojstvo) VALUES (102, 'Georg', '2005-8-20');
INSERT INTO oseba (id, ime, rojstvo) VALUES (103, 'Hanna', '1972-7-16');
INSERT INTO oseba (id, ime, rojstvo) VALUES (201, 'Franc', '1947-8-8');
INSERT INTO oseba (id, ime, rojstvo) VALUES (202, 'Franci', '1967-1-29');
INSERT INTO oseba (id, ime, rojstvo) VALUES (203, 'Francek', '1976-9-20');
INSERT INTO oseba (id, ime, rojstvo) VALUES (999, 'Brian', '0001-8-8');
INSERT INTO oseba (id, ime) VALUES (123, 'Ole McDonald'); -- napaka: datum je obvezen podatek
INSERT INTO oseba (id, rojstvo) VALUES (123, now()); -- napaka: ime je obvezen podatek

INSERT INTO otroci VALUES (999, (SELECT id FROM oseba WHERE ime='Ralf'));
INSERT INTO otroci VALUES (1, 2);
INSERT INTO otroci VALUES (1, 3);
INSERT INTO otroci VALUES (1, 4);
INSERT INTO otroci VALUES (100, 101);
INSERT INTO otroci VALUES (100, 102);
INSERT INTO otroci VALUES (103, 101);
INSERT INTO otroci VALUES (103, 102);
INSERT INTO otroci VALUES (201, 202);
INSERT INTO otroci VALUES (201, 203);
INSERT INTO otroci VALUES (203, 203); -- napaka: ne mores biti sam svoj stars
INSERT INTO otroci VALUES (201, 203); -- napaka: ne mores biti dvakrat otrok istega starsa
INSERT INTO otroci VALUES (999, 123); -- napaka: otrok ne obstaja
INSERT INTO otroci VALUES (123, 999); -- napaka: stars ne obstaja

INSERT INTO znamka (ime) VALUES ('Ferrari');
INSERT INTO znamka (ime) VALUES ('Mercedes');
INSERT INTO znamka (ime) VALUES ('Puch');
INSERT INTO znamka (ime) VALUES ('John Deere');
INSERT INTO znamka (ime) VALUES ('Edelstahl');
INSERT INTO znamka (ime) VALUES ('Tomos');
INSERT INTO znamka (ime) VALUES ('John Deere'); -- napaka: ne moremo imeti dveh znamk z istim imenom
INSERT INTO znamka (id) VALUES (100); -- napaka: ime je obvezen podatek

INSERT INTO traktor (lastnik, znamka, barva, nakup) VALUES (102, 1, 'rdeca', '2085-01-01'); -- napaka: nakup se je zgodil v prihodnosti
INSERT INTO traktor (lastnik, znamka, barva) VALUES (102, 1, 'rdeca'); 
INSERT INTO traktor (lastnik, znamka) VALUES (100, 3);
INSERT INTO traktor (lastnik, znamka, barva, nakup) VALUES (100, 3, 'rumena', '1980-9-28');
INSERT INTO traktor (lastnik, znamka, barva, nakup) VALUES (201, 4, 'rumena', '1995-12-25');
INSERT INTO traktor (lastnik, znamka, barva, nakup) VALUES (2, 4, 'siva', '1986-4-26'); 
INSERT INTO traktor (lastnik, znamka, barva, nakup) VALUES (3, 4, 'bela', '1999-5-7');
INSERT INTO traktor (lastnik, znamka, barva, nakup) VALUES (3, 6, 'modra', '2001-4-2');
INSERT INTO traktor (lastnik, znamka, barva, nakup) VALUES (3, 2, 'rdeca', '2012-02-24');
INSERT INTO traktor (lastnik, znamka, barva, nakup) VALUES (4, 3, 'rjava', '2002-12-19');
INSERT INTO traktor (lastnik, znamka, barva) VALUES (100, 3, 'rdeca');
INSERT INTO traktor (lastnik, znamka, barva) VALUES (100, 3, 'zelena'); 
INSERT INTO traktor (lastnik, znamka, barva) VALUES (100, 3, 'modra');
INSERT INTO traktor (lastnik, znamka, barva) VALUES (100, 3, 'losos');
INSERT INTO traktor (lastnik, znamka, barva) VALUES (100, 3, 'antracitna');
INSERT INTO traktor (lastnik, znamka) VALUES (101, 6);
INSERT INTO traktor (lastnik, znamka) VALUES (102, 6);
INSERT INTO traktor (lastnik, znamka) VALUES (102, 3);
INSERT INTO traktor (lastnik, znamka, barva) VALUES (201, 3, 'rdeca');
INSERT INTO traktor (lastnik, znamka) VALUES (201, 2);
INSERT INTO traktor (lastnik, znamka, barva) VALUES (202, 3, 'rdeca');
INSERT INTO traktor (lastnik, znamka) VALUES (203, 2);
INSERT INTO traktor (lastnik, znamka) VALUES (123, 5); -- napaka: lastnik ne obstaja
INSERT INTO traktor (lastnik, znamka) VALUES (999, 100); -- napaka: znamka ne obstaja

INSERT INTO deli (lastnik, znamka, tip, stevilo) VALUES (2, 3, 'kolo', 4);
INSERT INTO deli (lastnik, znamka, tip, stevilo) VALUES (101, 6, 'kolo', 4);
INSERT INTO deli (lastnik, znamka, tip, stevilo) VALUES (101, 6, 'auspuh', 2);
INSERT INTO deli (lastnik, znamka, tip, stevilo) VALUES (101, 6, 'auspuh', 3);
INSERT INTO deli (lastnik, znamka, tip, stevilo) VALUES (202, 6, 'volan', 3);
INSERT INTO deli (lastnik, znamka, tip) VALUES (203, 2, 'volan');
INSERT INTO deli (lastnik, znamka, tip, stevilo) VALUES (203, 4, 'menjalnik', 1);
INSERT INTO deli (lastnik, znamka, tip, stevilo) VALUES (203, 4, 'menjalnik', -51); -- napaka: negativno stevilo delov
INSERT INTO deli (lastnik, tip, stevilo) VALUES (203, 'menjalnik', 5); -- napaka: manjka znamka
INSERT INTO deli (lastnik, znamka, stevilo) VALUES (1, 1, 5); -- napaka: manjka tip
INSERT INTO deli (lastnik, znamka, tip) VALUES (123, 5, 'volan'); -- napaka: lastnik ne obstaja
INSERT INTO deli (lastnik, znamka, tip) VALUES (999, 100, 'volan'); -- napaka: znamka ne obstaja