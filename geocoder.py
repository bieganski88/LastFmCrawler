# -*- coding: utf-8 -*-
"""
Created on Tue Aug 02 23:18:28 2016

@author: Przemyslaw Bieganski, bieg4n@gmail.com
"""
# importowanie niezbednych modulow
import sqlite3
import os
import json
import urllib2

# constans
APIKEY = "A place for your API key" # klucz google maps api
SRCFILE = "./json/events.json" # sciezka do pliku zrodlowego
DESTPATH= "./sqlite" # sciezka do zapisu plikow wynikowych

class Geocoder:
    '''
    Klasa odpowiedzialna za geokodowanie informacji o koncertach.
    Geokodowanie odbywa sie z dokladnoscia do miasta, wykorzystywany jest 
    Google Maps API. Aby utowrzyć instancję tej klasy niezbędne jest podanie
    klucza dla usług Google. Wyniki zapisywane sa jako JSON oraz baza SQLite.
    '''
    
    def __init__(self, APIKEY, SRCFILE, DESTPATH):
        self._apikey = APIKEY
        self._srcfile = SRCFILE
        self._destpath = DESTPATH
        self._data = []
        self.results = []
        self._valid = False
        if self.validate() is True:
            print "\nInicjalizacja zakonczona powodzeniem."
            self._valid = True
            self._data = self.loadData()
    
    
    
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
        if self._valid is True:
            # nawiazanie polaczenia z baza danych
            conn = sqlite3.connect('LookupTable.db')
            cur = conn.cursor()
            
            for event in self._data:
                city, country = event[-2], event[-1] # city and country
                print city, country
                # zapytanie o to czy lokacja jest juz w bazie danych
                query = u'select * from GEOLOKALIZACJE where city = "{}" and country = "{}"'.format(city, country)
                rows = cur.execute(query.encode("UTF-8")).fetchall()
                
                if len(rows) > 0: # jest w bazie
                    lat = rows[0][3]
                    lng = rows[0][4]
                    
                else: # trzeba pozyskac dane od wujka Googla
                    try:
                        # tworze tresc zapytania do Google API
                        url_base = u'https://maps.googleapis.com/maps/api/geocode/json?'
                        url_location = u'address={}'.format((city+"+"+country).replace(' ', '+'))
                        url = u'{}{}&key={}'.format(url_base, url_location, self._apikey)
                        
                        #zapytanie do  google api
                        site = urllib2.urlopen(url.encode("UTF-8"))
                        data = json.load(site)
                        location = data['results'][0]['geometry']['location']
                        lat, lng = location['lat'], location['lng']
                        # insert do bazy danych
                        query = u'INSERT INTO GEOLOKALIZACJE VALUES(NULL, "{}", "{}", {}, {})'.format(country, city, lat, lng)
                        cur.execute(query.encode("UTF-8"))
                    except:
                        print "Cos poszlo nie tak dla >> {},{}".format(city, country)
                
                # tu juz czesc wspolna dla obu przypadkow
                geoEvent = event[:] # kopia listy
                geoEvent.append(lat)
                geoEvent.append(lng)
                
                self.results.append(geoEvent) # dodaje do wynikow
                
            # zamykam polaczenie z baza
            conn.commit()
            conn.close()
        else:
            print "Obiekt nie przeszedl inicjalizacji prawidlowo. Nie mozna kontynuowac."
        
        
    
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
            CREATE TABLE EVENTS
            (ID INTEGER PRIMARY KEY,
            TITLE CHAR(50) NOT NULL,
            DATE CHAR(25) NOT NULL,
            LINEUP TEXT,
            PLACE_NAME CHAR(50),
            CITY CHAR(50) NOT NULL,
            COUNTRY CHAR(50) NOT NULL,
            LATITUDE REAL NOT NULL,
            LONGITUDE REAL NOT NULL
            );''')
        print "Baza danych eventsGeom.db utworzona pomyslnie."
        conn.close()
        
        
    
    # FUNKCJE POMOCNICZE - EXPORT DANYCH
    def exportToJSON(self):
        '''
        Exportuje dane wynikowe do pliku w formacie JSON.
        '''
        with open('json/EventsGeodata.json', 'w') as outfile:
            json.dump(self.results, outfile)
        
        print "Export do pliku JSON zakończony powodzeniem."

    
    
    def exportToDB(self):
        '''
        Exportuje dane wynikowe do bazy danych SQLite.
        '''
        # nawiazuje polaczenie z baza danych
        conn = sqlite3.connect('{0}/eventsGeom.db'.format(self._destpath))
        cur = conn.cursor()
        # czyszcze tabele
        cur.execute("DELETE FROM EVENTS")
        conn.commit()
        
        # exportuje dane do bazy
        for record in self.results:
            # mapowanie wartosci do zmiennych
            title = record[0].replace('"','\'')
            date = record[1]
            lineup = str(record[2]).replace('"','\'')
            place = record[3].replace('"','\'')
            city = record[4]
            country = record[5]
            lat = record[6]
            lng = record[7]
            
            # insert do bazy danych
            try:
                query_part1 = u'INSERT INTO EVENTS VALUES'
                query_part2 = u'(NULL, "{}", "{}", "{}", "{}", "{}", "{}", {}, {})'.format(title, date, lineup, place, city, country, lat, lng)
                query = query_part1 + query_part2            
                cur.execute(query.encode("UTF-8"))
            except:
                print "Napotkano blad podczas wykonywania polecenia:"
                print query
                
        # commit wprowadzonych zmian
        conn.commit()
        conn.close()
        print "Export do bazy danych SQLite eventsGeom.db zakończony powodzeniem."



#proces = Geocoder(APIKEY, SRCFILE, DESTPATH)