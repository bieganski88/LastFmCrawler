# -*- coding: utf-8 -*-
"""
Created on Fri Sep 16 23:35:10 2016

@author: Przemyslaw Bieganski, bieg4n@gmail.com
"""
# import modulow
import band
import crawlerMain

# Przypadek 1 - użycie klasy LastFmUser
user= crawlerMain.LastFmUser('Biegan') # inicjuje obiekt
user.get_scrobbles(3) # pobiera 5 stron - 250 ostatnio przesluchanych utworow
user.get_artists(1) # pobiera jedna strone - 50 najczesciej sluchanych artystow
user.get_concertList() # pobiera informacje o koncertach dla zespolow pobranych metoda get_artists
user.to_json() # zrzuca wyniki do plikow JSON (lokalizacja /json)

# Przypadek 2 - użycie klasy BandFm
artist = band.BandFm('Sum+41')
artist.get_tags()
artist.get_events()
print "TAGI"
print artist.tags
print "Koncerty"
print artist.events