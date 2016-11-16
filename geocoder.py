# -*- coding: utf-8 -*-
"""
Created on Tue Aug 02 23:18:28 2016

@author: Przemyslaw Bieganski, bieg4n@gmail.com
"""
# importowanie niezbednych modulow
import sqlite3
import os
import json
import urllib
import traceback

# constans
APIKEY = "Place for your API key"  # klucz google maps api
SRCFILE = "./json/events.json"  # sciezka do pliku zrodlowego
DESTPATH = "./sqlite"  # sciezka do zapisu plikow wynikowych
DJANGO_DB = "D:\Cloud\Dropbox\IT\python\django\eventsMap\eventsMap"  # sciezka do bazy sqlite z aplikacji Django


class Geocoder:
    '''
    Klasa odpowiedzialna za geokodowanie informacji o koncertach.
    Geokodowanie odbywa sie z dokladnoscia do miasta, wykorzystywany jest 
    Google Maps API. Aby utowrzyć instancję tej klasy niezbędne jest podanie
    klucza dla usług Google. Wyniki zapisywane sa jako JSON oraz baza SQLite.
    '''

    def __init__(self, APIKEY, SRCFILE, DESTPATH, DJANGO_DB):
        self._apikey = APIKEY
        self._srcfile = SRCFILE
        self._destpath = DESTPATH
        self._django = DJANGO_DB
        self.data = []
        self.results = []
        print 'Inicjalizacja rozpoczeta..'
        self._valid = False
        if self.validate() is True:
            print "Inicjalizacja zakonczona powodzeniem.\n"
            self._valid = True
            self.data = self.loadData()


    def __str__(self):
        '''
        Zwraca ilość danych wejsciowych, aktualna ilosc danych wynikowych
        oraz sciezke do folderu wynikowego.
        '''
        print 'Ilosc zaladowanych danych wejsciowych: {} koncertow'.format(len(self.data))
        print 'Ilosc przetworzonych danych gotowych do exportu: {} koncertow'.format(len(self.results))
        print 'Sciezka zapisu wynikow: {}'.format(self._destpath)
        return ''


    def validate(self):
        '''
        Sprawdza kompletnosc danych poczatkowych:
        - poprawnosc sciezek,
        - obecnosc danych zrodlowych,
        - obecnosc baz danych (tworzy w przypadku ich braku)
        '''
        # czy istnieja dane wejsciowe
        flag = os.path.isfile(self._srcfile)
        if flag is False:
            print '\nNieudana inicjalizacja :Brak danych wejsciowych.'
            return False

        # czy istnieje folder na dane wyjsciowe
        if not os.path.exists(self._destpath):
            os.makedirs(self._destpath)

        # czy istnieje LookupTable.db
        flag = os.path.isfile('LookupTable.db')
        if flag is False:
            self.createLookupDB() 
        # tworze baza na dane wynikowe
        flag = os.path.isfile('{0}/eventsGeom.db'.format(self._destpath))
        if flag is False:
            self.createOutputDB()
        return True


    def loadData(self):
        '''
        Laduje plik JSON z danymi wejsciowymi.
        '''
        with open(self._srcfile) as json_data:
            data = json.load(json_data)

        return data


    def process(self):
        '''
        Pozyskiwanie geolokalizacji dla miejsc. Glowna metoda tej klasy.
        Wejscie dane zrodlowe pochodzace z JSON, wyjscie te same dane wzbogacone
        o wspolrzedne. Pomocniczo korzysta z LookupTable.db
        '''
        gmAPI = 0 # ile razy zostalo uzyte google maps api - istotne gdyz za darmo tylko 2500 dziennie
        if self._valid is True:
            # nawiazanie polaczenia z baza danych
            conn = sqlite3.connect('LookupTable.db')
            cur = conn.cursor()

            for event in self.data:
                city, country = event[-2], event[-1]  # city and country
                print city, country
                # zapytanie o to czy lokacja jest juz w bazie danych
                query = u'select * from GEOLOKALIZACJE where city = "{}" and country = "{}"'.format(city, country)
                rows = cur.execute(query.encode("UTF-8")).fetchall()

                if len(rows) > 0:  # jest w bazie
                    lat = rows[0][3]
                    lng = rows[0][4]

                else: # trzeba pozyskac dane od wujka Googla
                    try:
                        # tworze tresc zapytania do Google API
                        url_base = u'https://maps.googleapis.com/maps/api/geocode/json?'
                        url_location = u'address={}'.format((city+"+"+country).replace(' ', '+'))
                        url = u'{}{}&key={}'.format(url_base, url_location, self._apikey)
                        
                        #zapytanie do  google api
                        site = urllib.urlopen(url.encode("UTF-8"))
                        data = json.load(site)
                        location = data['results'][0]['geometry']['location']
                        lat, lng = location['lat'], location['lng']
                        # insert do bazy danych
                        query = u'INSERT INTO GEOLOKALIZACJE VALUES(NULL, "{}", "{}", {}, {})'.format(country, city, lat, lng)
                        cur.execute(query.encode("UTF-8"))
                        gmAPI += 1
                    except:
                        try:
                            print "Nie udane przetwarzanie dla >> {},{}".format(city, country)
                        except:
                            print "Nie udane przetwarzanie."

                # tu juz czesc wspolna dla obu przypadkow
                geoEvent = event[:]  # kopia listy
                geoEvent.append(lat)
                geoEvent.append(lng)

                self.results.append(geoEvent)  # dodaje do wynikow

            # zamykam polaczenie z baza
            conn.commit()
            conn.close()
        else:
            print "Obiekt nie przeszedl inicjalizacji prawidlowo. Nie mozna kontynuowac."
        
        print "Google Maps API zostalo uzyte: {} raz(y).".format(gmAPI)


    # FUNKCJE POMOCNICZE - TWORZENIE BAZ DANYCH SQLITE
    def createLookupDB(self):
        '''
        Baza danych w technologi SQLite, ktora gromadzic bedzie informacje
        o już zgeokodowanych lokalizacjach. Odwolanie do Google Api nastapi jedynie
        gdy szukanej lokalizacji nie bedzie w bazie danych.
        Struktura: kraj, miasto, szerokosc geo, dlugosc geo.
        '''
        # tworzenie pustej bazy danych
        conn = sqlite3.connect('LookupTable.db')
        # tworzenie tabeli
        conn.execute('''
            CREATE TABLE GEOLOKALIZACJE
            (ID INTEGER PRIMARY KEY,
            COUNTRY CHAR(50) NOT NULL,
            CITY CHAR(50) NOT NULL,
            LATITUDE REAL NOT NULL,
            LONGITUDE REAL NOT NULL
            );''')
        print "Baza danych LookupTable.db utworzona pomyslnie."
        conn.close()


    def createOutputDB(self):
        '''
        Baza danych w technologi SQLite, w ktorej zapisane zostana dane dotyczace
        koncertow wraz z geolokalizacją.
        '''
        # tworzenie pustej bazy danych
        conn = sqlite3.connect('{0}/eventsGeom.db'.format(self._destpath))
        # tworzenie tabeli
        conn.execute('''
            CREATE TABLE EVENTS_MUSICEVENTS
            (ID INTEGER PRIMARY KEY,
            ARTIST CHAR(50) NOT NULL,
            TITLE CHAR(50) NOT NULL,
            EVENT_DATE CHAR(25) NOT NULL,
            LINEUP TEXT,
            PLACE CHAR(50),
            CITY CHAR(50) NOT NULL,
            COUNTRY CHAR(50) NOT NULL,
            LATITUDE REAL NOT NULL,
            LONGITUDE REAL NOT NULL
            );''')
        print "Baza danych eventsGeom.db na dane wynikowe zostala utworzona pomyslnie."
        conn.close()


    # FUNKCJE POMOCNICZE - EXPORT DANYCH
    def exportToJSON(self):
        '''
        Exportuje dane wynikowe do pliku w formacie JSON.
        '''
        # export do standardowego jsona
        with open('{}/EventsGeodata.json'.format(self._destpath), 'w') as outfile:
            json.dump(self.results, outfile, indent=4)
            
        # export do geojson
        geodata = self.results
        properties_keys = ['artist', 'title', 'date', 'lineup', 'place',
                       'city', 'country'] # klucze do opisu danych nie geometrycznych
                       
        featureCollection = {'type': "FeatureCollection"} # element glowny pliku json
        features = [] # agregat na obiekty
        
        for event in geodata:
            coordinates = [event[-1], event[-2]]
            properties = event[:-2]
            feature = {"type": "Feature",
                       "geometry": {"type": "Point", "coordinates": coordinates},
                       "properties": dict(zip(properties_keys, properties))
                       }
            features.append(feature)
        
        featureCollection["features"] = features
        
        with open('{}/EventsGeoJSON.json'.format(self._destpath), 'w') as outfile:
            json.dump(featureCollection, outfile, indent=4)
                
        print "Export do pliku JSON oraz GEOJSON zakończony powodzeniem."


    def exportToDB(self, django = False):
        '''
        Exportuje dane wynikowe do bazy danych SQLite.
        '''
        # nawiazuje polaczenie z baza danych
        if django:
            try:
                conn = sqlite3.connect('{}\db.sqlite3'.format(self._django))
            except:
                print "Nie udalo sie nawiazac polaczenia z baza danych - SQLite."
                print "Prosze zweryfikowac zadeklarowana sciezke dostepu do aplikacji Django"
                return False
        else:
            conn = sqlite3.connect('{0}/eventsGeom.db'.format(self._destpath))
        cur = conn.cursor()
        # czyszcze tabele
        cur.execute("DELETE FROM EVENTS_MUSICEVENTS")
        conn.commit()
        
        # exportuje dane do bazy
        for record in self.results:
            # mapowanie wartosci do zmiennych
            artist = record[0].replace('"', '\'')
            title = record[1].replace('"', '\'')
            date = record[2]
            lineup = str(record[3]).replace('"', '\'')
            place = record[4].replace('"', '\'')
            city = record[5]
            country = record[6]
            lat = record[7]
            lng = record[8]
            
            # insert do bazy danych
            try:
                query_part1 = u'INSERT INTO events_musicevents (id, artist, title, event_date, lineup, place, city, country, latitude, longitude) VALUES'
                query_part2 = u'(NULL, "{}", "{}", "{}", "{}", "{}", "{}", "{}", {}, {})'.format(artist, title, date, lineup, place, city, country, lat, lng)
                query = query_part1 + query_part2            
                cur.execute(query.encode("UTF-8"))
            except:
                print "Napotkano blad podczas wykonywania polecenia:"
                print query
                tb = traceback.format_exc()
                print tb

        # commit wprowadzonych zmian
        conn.commit()
        conn.close()
        if django:
            print "Export do bazy SQLite dedykowanej aplikacji Django zakończony powodzeniem."
        else:
            print "Export do bazy danych SQLite eventsGeom.db zakończony powodzeniem."


    def exportToDjango(self):
        '''
        Eksport danych do skojarzonej bazy sqlite aplikacji Django,
        ktora posluzy do prezentacji danych na mapie.
        '''
        self.exportToDB(True) # true - oznacza import do bazy django