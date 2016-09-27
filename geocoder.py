# -*- coding: utf-8 -*-
"""
Created on Tue Aug 02 23:18:28 2016

@author: Przemyslaw Bieganski, bieg4n@gmail.com
"""
# importowanie niezbednych modulow
import sqlite3
import os
import json

# constans
APIKEY = "" # klucz google maps api
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
        self._valid = False
        if self.validate() is True:
            print "\nInicjalizacja zakonczona powodzeniem."
            self._valid = True
    
    
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
        return True
        
    
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
            (ID INT PRIMARY KEY NOT NULL,
            COUNTRY CHAR(50) NOT NULL,
            CITY CHAR(50) NOT NULL,
            LONGITUDE REAL NOT NULL,
            LATITUDE REAL NOT NULL
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
            (ID INT PRIMARY KEY NOT NULL,
            TITLE CHAR(50) NOT NULL,
            DATE CHAR(25) NOT NULL,
            LINEUP TEXT,
            PLACE_NAME CHAR(50),
            CITY CHAR(50) NOT NULL,
            COUNTRY CHAR(50) NOT NULL,
            LONGITUDE REAL NOT NULL,
            LATITUDE REAL NOT NULL
            );''')
        print "Baza danych eventsGeom.db utworzona pomyslnie."
        conn.close()
        
    
    # FUNKCJE POMOCNICZE - EXPORT DANYCH
    def exportToJSON():
        '''
        Exportuje dane wynikowe do pliku w formacie JSON.
        '''
        # usuwa istniejacy plik
        
        # tworzy nowy plik i exportuje do niego dane
        
        return True
    
    
    def exportToDB():
        '''
        Exportuje dane wynikowe do bazy danych SQLite.
        '''
        # czysci wynikowa tabele jesli baza juz istnieje
        
        # exportuje dane do bazy
        
        return True


proces = Geocoder(APIKEY, SRCFILE, DESTPATH)
print proces._valid