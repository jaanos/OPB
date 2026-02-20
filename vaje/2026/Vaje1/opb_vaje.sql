-- Izvedemo  poizvedbo, ki vrne vse možne vrstice

SELECT *
FROM student;

-- Vstavimo novo vrstico s svojimi podatki
-- INSERT INTO tabela (stolpec1, stolpec2, ...)
-- VALUES (vrednost1, vrednost2, ...)

INSERT INTO student (ime, priimek, letnik, smer, email)
VALUES ('Gašper Domen', 'Romih', 1995, 'MAT', 'gasper.romih@fmf.uni-lj.si')

-- Da se izognemo podvojitva, lahko nekatere vrstice tudi izbrišemo:

delete from student
where ime = 'Gašper Domen';

-- Pozor: ker v tabeli ni primarnega ključa, s tem ukazom izbrišemo vse
-- ponovitve kjer je ime= Gašper Domen