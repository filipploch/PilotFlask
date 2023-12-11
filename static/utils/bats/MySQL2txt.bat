@echo off
setlocal enabledelayedexpansion

rem Ustawienia do bazy danych MySQL
set DB_HOST=127.0.0.1
set DB_USER=root
set DB_PASS=
set DB_NAME=futsal

rem Zapytanie SQL
set SQL_QUERY=SELECT matches.score_a, matches.score_b FROM `matches` WHERE matches.actual=1;

rem Wykonaj zapytanie i zapisz wyniki do zmiennych
echo %SQL_QUERY% | mysql -h%DB_HOST% -u%DB_USER% -p%DB_PASS% -D%DB_NAME% -N -B > result.txt

rem Odczytaj wyniki z pliku
set /p result=<result.txt
del result.txt

rem Podziel wynik na zmienne
for %%a in (%result%) do (
    set "score_a=%%a"
    set "score_b=%%b"
)

rem Wyświetl wyniki
echo Wynik: score_a=%score_a%, score_b=%score_b%
