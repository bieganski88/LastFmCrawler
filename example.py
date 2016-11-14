# -*- coding: utf-8 -*-
"""
Created on Fri Sep 16 23:35:10 2016

@author: Przemyslaw Bieganski, bieg4n@gmail.com
"""
# import modulow
import band
import crawlerMain
import geocoder


def example1():
    '''
    Pierwszy przykład ilustrujący pobranie informacji na temat koncertow dla
    pojedynczego zespolu. Oraz zrzut danych do json.
    '''
    print "Nazwiazanie polaczenia z strona poswiecona zespolowi"
    artist = band.BandFm('blink-182', info = 1) # info == 1 jesli chcemy wiecej szczegolow na temat polaczenia
    # pobiera tagi opisujace zespol
    artist.get_tags()
    # pobiera informacje o koncertach
    artist.get_events()
    
    print "Najpopularniejsze tagi:"
    print artist.tags
    
    print "Liczba koncertow:\n{}".format(len(artist.events))
    
    print "Informacje o przykładowym wydarzeniu:"
    print artist.events[0]
    
    # zrzut do pliku json
    artist.to_json('example/example1')



def example2():
    '''
    Przykład poświęcony geokodowaniu koncertow - czyli zidentyfikowaniu wspolrzednych
    miejsca bazujac na opisie slownym. w tym wypadku geolokalizacja okreslana jest z dokladnoscia
    co do miasta.
    '''
    # troche stalych niezbednych dla utworzenia obiektu klasy geokoder.
    
    # klucz do google maps api - usluga geokodowania. wszystkie nieznane dla aplikacji
    # lokalizacje identyfikowane sa za pomoca uslugi google, a nastepnie wynik zapisywany jest w bazie
    # znane lokalizacje natomiast pobierane sa bezposrednio z bazy
    APIKEY = ""
    
    # plik json z danymi wejsiowymi. plik wyeksportowany z klasy band lub LastFmUser
    SRCFILE = "./example/example1/events.json" # dane wyeksportowane z example1
    
    DESTPATH = "./example/example2" # gdzie zapisac dane wynikowe
    
    # sciezka do folderu z baza danych SQLite aplikacji django [do wyswietlania danych]
    # aplikacje zawiera repo DjangoApp4LastFmCrawler z mojego githuba
    # dostepne pod adresem https://github.com/bieganski88/DjangoApp4LastFmCrawler
    DJANGO_DB = ""
    
    # instancjonowanie klasy
    geokodowanie = geocoder.Geocoder(APIKEY, SRCFILE, DESTPATH, DJANGO_DB)
    
    print "Rozpoczecie procesu geokodowania"
    geokodowanie.process()
    
    print "\nWyswietlam przykladowy rekord danych wynikowych.."
    print geokodowanie.results[0]
    
    # export odbywa sie zarowno do formatu json jak i geojson
    geokodowanie.exportToJSON()
    
    # export danych do bazy danych wynikowej
    geokodowanie.exportToDB()
    
    # export danych do bazy danych django w celu wyswietlenia wynikow
    geokodowanie.exportToDjango()



def example3():
    '''
    Przyklad wykorzystujacy pelnie mozliwosci aplikacji - nawizanie polaczenia
    z kontem last fm zadanego uzytkownika i pobranie informacji o koncertach,
    przesluchiwanych utworach oraz ulubionych wykonawcach.
    '''
    # instancjonowanie klasy LastFmUser - zawiazanie "polaczenia" z strona uzytkownika
    # "Biegan" - czyli moja - autora tej aplikacji
    user= crawlerMain.LastFmUser('Biegan')
    
    # wyswietlanie informacji o zawiazanym polaczeniu
    str(user)
    
    # pobieram fragment histori sluchanych utworow, analiza calosci - ponad 1500 stron moze
    # zajac kilka godzin, dlatego pobieram w celach pokzowych jedynie kilka z nich
    # od strony 1 do 5 - czyli lacznie 250 rekordow
    print "Rozpoczecie analizy biblioteki utworow.."
    user.get_scrobbles(1,5)
    
    # wyswietlam kilka pierwszych rekordow
    print "Kilka przykladowych rekordow:"
    print user.scrobbles[:5]
    print "Laczna ilosc pobranych scrobli: {}".format(len(user.scrobbles))
    
    # pobieram informacje o najpopularniejszych wykonawcach
    # pobieranie moze nastapic od dowolnej strony
    # im mniejszy index trony tym popularniejsi artysci
    print "Analiza biblioteki wykonawcow.."
    user.get_artists(1,1) # pobiera jedna strone - 50 najczesciej sluchanych artystow
    
    # wyswietlam kilka przykladowych rekordow dotyczacych artystow
    print "Kilka przykladowych rekordow z sluchanymi artystami"
    print user.artists[:5]
    
    # pobieram informacje o koncertach, dla kazdego z zespolow
    # tworzona jest klasa Band i pobierane informacje o wystepach
    # dane skladowane sa w jednej liscie
    print "Pobieranie informacji o wystepach.."
    user.get_concertList(0.2) # analizuje 20% wykonacow w tym wypadku 0.2 *50 = 10
    
    print "Znalezionych wydarzen muzycznych: {}".format(len(user.concertList))
    
    # export danych do json
    user.to_json('example/example3')
    
    # geokodowanie wynikow - opis zbyteczny gdyz zostal przedstaiwony przy
    # przykladzie numer 2
    APIKEY = ""
    SRCFILE = "./example/example3/events.json" # dane wyeksportowane z example1
    DESTPATH = "./example/example3/geo" # gdzie zapisac dane wynikowe
    DJANGO_DB = ""
    
    # instancjonowanie klasy
    geokodowanie = geocoder.Geocoder(APIKEY, SRCFILE, DESTPATH, DJANGO_DB)
    geokodowanie.process()
    
    # export odbywa sie zarowno do formatu json jak i geojson
    geokodowanie.exportToJSON()
    
    # export danych do bazy danych wynikowej
    geokodowanie.exportToDB()
    
    # export danych do bazy danych django w celu wyswietlenia wynikow
    geokodowanie.exportToDjango()
