# -*- coding: utf-8 -*-
"""
Created on Fri Sep 16 23:35:10 2016

@author: Przemyslaw Bieganski, bieg4n@gmail.com
"""
# import modulow wlasnych
import band
import CrawlerMain
import geocoder


def example1():
    '''
    Pierwszy przykład ilustrujący pobranie informacji na temat koncertow dla
    pojedynczego zespolu. Oraz zrzut danych do json.
    '''
    print "Nazwiazanie polaczenia z strona poswiecona zespolowi"
    # info == 1 jesli chcemy wiecej szczegolow na temat polaczenia
    artist = band.BandFm('blink-182', info=1)
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
    # lokalizacje identyfikowane sa za pomoca uslugi google, a nastepnie wynik
    # zapisywany jest w bazie znane lokalizacje natomiast pobierane sa bezposrednio z bazy
    apikey = ""

    # plik json z danymi wejsiowymi. plik wyeksportowany z klasy band lub LastFmUser
    srcfile = "./example/example1/events.json" # dane wyeksportowane z example1

    destpath = "./example/example2" # gdzie zapisac dane wynikowe

    # sciezka do folderu z baza danych SQLite aplikacji django [do wyswietlania danych]
    # aplikacje zawiera repo DjangoApp4LastFmCrawler z mojego githuba
    # dostepne pod adresem https://github.com/bieganski88/DjangoApp4LastFmCrawler
    django_db = "D:/Cloud/Dropbox/IT/python/django/eventsMap/eventsMap"

    # instancjonowanie klasy
    geokodowanie = geocoder.Geocoder(apikey, srcfile, destpath, django_db)

    print "Rozpoczecie procesu geokodowania"
    geokodowanie.process()

    print "\nWyswietlam przykladowy rekord danych wynikowych.."
    print geokodowanie.results[0]

    # export odbywa sie zarowno do formatu json jak i geojson
    geokodowanie.export_to_json()

    # export danych do bazy danych wynikowej
    geokodowanie.export_to_db()

    # export danych do bazy danych django w celu wyswietlenia wynikow
    geokodowanie.export_to_django()



def example3():
    '''
    Przyklad wykorzystujacy pelnie mozliwosci aplikacji - nawizanie polaczenia
    z kontem last fm zadanego uzytkownika i pobranie informacji o koncertach,
    przesluchiwanych utworach oraz ulubionych wykonawcach.
    '''
    # instancjonowanie klasy LastFmUser - zawiazanie "polaczenia" z strona uzytkownika
    # "Biegan" - czyli moja - autora tej aplikacji
    user = CrawlerMain.LastFmUser('Biegan')

    # wyswietlanie informacji o nawiazanym polaczeniu
    str(user)

    # pobieram fragment histori sluchanych utworow, analiza calosci - ponad 1500 stron moze
    # zajac kilka godzin, dlatego pobieram w celach pokzowych jedynie kilka z nich
    # od strony 1 do 5 - czyli lacznie 250 rekordow
    print "Rozpoczecie analizy biblioteki utworow.."
    user.get_scrobbles(1, 5)

    # wyswietlam kilka pierwszych rekordow
    print "Kilka przykladowych rekordow:"
    print user.scrobbles[:5]
    print "Laczna ilosc pobranych scrobli: {}".format(len(user.scrobbles))

    # pobieram informacje o najpopularniejszych wykonawcach
    # pobieranie moze nastapic od dowolnej strony
    # im mniejszy index trony tym popularniejsi artysci
    print "Analiza biblioteki wykonawcow.."
    user.get_artists_all_time(3, 5) # pobiera jedna strone - 50 najczesciej sluchanych artystow

    # wyswietlam kilka przykladowych rekordow dotyczacych artystow
    print "Kilka przykladowych rekordow z sluchanymi artystami"
    print user.artists[:5]

    # pobieram informacje o koncertach, dla kazdego z zespolow
    # tworzona jest klasa Band i pobierane informacje o wystepach
    # dane skladowane sa w jednej liscie
    print "Pobieranie informacji o wystepach.."
    user.get_concertList(0.2) # analizuje 20% wykonacow w tym wypadku 0.2 *50 = 10

    print "Znalezionych wydarzen muzycznych: {}".format(len(user.concert_list))

    # export danych do json
    user.to_json('example/example3')

    # geokodowanie wynikow - opis zbyteczny gdyz zostal przedstaiwony przy
    # przykladzie numer 2
    apikey = "AIzaSyCABuxZRUVIDB7LtQeaoL8fcIuMCXHGlIM"
    srcfile = "./example/example3/events.json" # dane wyeksportowane z example1
    destpath = "./example/example3/geo" # gdzie zapisac dane wynikowe
    django_db = "D:/Cloud/Dropbox/IT/python/django/eventsMap/eventsMap"

    # instancjonowanie klasy
    geokodowanie = geocoder.Geocoder(apikey, srcfile, destpath, django_db)
    geokodowanie.process()

    # export odbywa sie zarowno do formatu json jak i geojson
    geokodowanie.export_to_json()

    # export danych do bazy danych wynikowej
    geokodowanie.export_to_db()

    # export danych do bazy danych django w celu wyswietlenia wynikow
    geokodowanie.export_to_django()


def example4():
    '''
    Przyklad analogiczny do poprzedniego, rowniez bazowac bedziemy na koncie
    uzytkownika 'Biegan'. Tym razem artystow nie bedziemy pobierac bazujac na
    aktualnych preferencjach uzytkownika. Czyli najpopulatniejszych z ostatnich 30 dni.
    get_artist_recent() - przyjmuje poza tym wartosci: 7, 90, 180 oraz 365.
    '''
    user = CrawlerMain.LastFmUser('Biegan')
    str(user)

    print "Wyszukiwanie najpopularniejszych artystow z ostatnich 30 dni.."
    user.get_artists_recent('90')
    print "Odnaleziono {} artystow".format(len(user.artists))

    print "Pobieranie informacji o koncertach.."
    user.get_concertList(0.2)

    user.to_json('example/example4')

    apikey = ""
    srcfile = "./example/example4/events.json" # dane wyeksportowane z example1
    destpath = "./example/example4/geo" # gdzie zapisac dane wynikowe
    django_db = "D:/Cloud/Dropbox/IT/python/django/eventsMap/eventsMap"

    # instancjonowanie klasy
    geokodowanie = geocoder.Geocoder(apikey, srcfile, destpath, django_db)
    geokodowanie.process()

    # export odbywa sie zarowno do formatu json jak i geojson
    geokodowanie.export_to_json()

    # export danych do bazy danych django w celu wyswietlenia wynikow
    geokodowanie.export_to_django()



def example5():
    '''
    Nie każdy musi mieć konto LastFM lub też bogatą historię przesłuchanych utworow.
    W zwiazku z czym dodalem mozliwosc wyszukiwania koncertow, bazujac na
    zdefiniowanej przez uzytkownika liscie wykonawcow.
    '''
    # lokalizacja pliku z danymi poczatkowymi
    src_path = "./example/example5/zespoly.json"
    # wskazanie folderu do zapisu danych wynikowych
    dest_path = "./example/example5/wyniki"
    # rozpoczecie przetwarzania
    band.zespoly_z_listy(src_path, dest_path)

    apikey = ""
    srcfile = "./example/example5/wyniki/events.json" # dane wyeksportowane z example1
    destpath = "./example/example5/wyniki" # gdzie zapisac dane wynikowe
    django_db = "D:/Cloud/Dropbox/IT/python/django/eventsMap/eventsMap"

    # instancjonowanie klasy
    geokodowanie = geocoder.Geocoder(apikey, srcfile, destpath, django_db)
    geokodowanie.process()

    # export odbywa sie zarowno do formatu json jak i geojson
    geokodowanie.export_to_json()

    # export danych do bazy danych django w celu wyswietlenia wynikow
    geokodowanie.export_to_django()
