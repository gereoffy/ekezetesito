
0. lepes:  gen_map.py
- ha nincs wordmap.pck fileod (csak ekezetes alakban hasznalatos gyakori szavak listaja), ezzel csinalhatsz :)

1. lepes:  gen_map_count.py
- olvassa a TXT/ konyvtarban levo szovegfileokat (jo minosegu magyar nyelvu ekezetes utf8 txt)
- hasznalja a wordmap.pck-t a TXT szuresere
- megszamolja a szavakat/parokat, ha tul sok mar az adat, akkor a legritkabbakat mar menet kozben torli
- az eredmenyt elmenti: wcount.pck, walias.pck, wpairs.pck

2. lepes:  gen_map_reduce.py
- beolvassa az 1. lepesben eloallitott fileokat: wcount.pck, walias.pck, wpairs.pck
- redukalja a tablak meretet, kiszuri a hibakat, es hunspell-el is ellenorzi
- az eredmenyt ide menti: wordmap.pck, wordpairs.pck

3. lepes: teszteles
- validate_map_split.py: ez a test.txt ekezetes szovegfileon vegez ellenorzo statisztikat
- use_map.py: ezzel egy ekezet nelkuli szoveget lehet ekezetesiteni

4. lepes:  mktree\*.py
- wordmap.dat & wordpairs.dat eloallitasa
- wordmap.pck & wordpairs.pck binaris faba konvertalasa (mktree9 tomoriti is!)
