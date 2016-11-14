# -*- coding: utf-8 -*-
"""
Created on Fri Jul 22 22:16:20 2016

@author: Przemyslaw Bieganski, bieg4n@gmail.com

Crawler LastFm - pobiera informacje o przesluchanych utworach, sluchanych wykonawcach,
znajomych.
Zawiera glowna klase: LastFmUser.

"""

import urllib
import band
import json
from BeautifulSoup import *

# glowna klasa
class LastFmUser:
    '''
    Glowna klasa. Tworzy pajaczka, ktory przeszukuje konto Last FM podanego
    uzytkownika. pobiera informacje o przesluchanych utworach, przesluchanych wykonawcow
    oraz liste znajomych.
    '''

    def __init__(self, username):
        self._username = username
        self._nrOfPages = self.get_info()  # klucze: 'scrobbles', 'artists'
        self.artists = []
        self.scrobbles = []
        self.concertList = []


    def __str__(self):
        '''
        Zwraca podstawowe informacje o klasie.
        '''
        print 'Nawiazuje polaczenie z kontem: {}'.format(self._username)
        print 'Konto zawiera {} stron scrobbli oraz {} stron z wykonawcami'.format(self._nrOfPages['scrobbles'], self._nrOfPages['artists'])
        print '(po 50 na stronie).'
        return ''


    def get_info(self):
        '''
        Wzraca liste stron z przesluchanymi utworami oraz wykonawcami (jako inty).
        '''
        url = [u'http://www.last.fm/user/{}/library'.format(self._username),
               u'http://www.last.fm/user/{}/library/artists'.format(self._username)]
        
        pages = { 'scrobbles': self.checkPages(self.makeSoup(url[0])),
                 'artists': self.checkPages(self.makeSoup(url[1]))}

        return pages


    def clean(self):
        '''
        Przywraca wartosci poczatkowe dla self.artists, self.scrobbles, self.concertList
        '''
        self.artists = []
        self.scrobbles = []
        self.concertList = []


    def get_scrobbles(self, start_page, end_page):
        '''
        Pobiera informacje o przesluchanych utworach z zadanej ilosci stron.
        '''
        if start_page <= 0:
            start_page = 1  # korekta wartosci
            
        if end_page > self._nrOfPages['scrobbles']:
            print 'Zbyt duzy argument wejsciowy'
            return None
 
        # generuje linki dla stron do sprawdzenia
        url = u'http://www.last.fm/user/{}/library'.format(self._username)
        linki = [u'{}?page={}'.format(url, x) for x in range(start_page, end_page+1)]

        # ekstrakcja playlisty
        przesluchane = []
        for link in linki:
            przesluchane += self.looking4music(link)
            print u'Przetwazanie strony: {} - OK'.format(link)
        self.scrobbles = przesluchane


    def get_artists(self, start_page, end_page):
        '''
        Pobiera informacje o ulubionych artystach z zdanej ilosci stron.
        '''
        if start_page <= 0:
            start_page = 1
        
        if end_page > self._nrOfPages['artists']:
            print 'Zbyt duzy argument wejsciowy'
            return None

        # generuje linki dla stron do sprawdzenia
        url = u'http://www.last.fm/user/{}/library/artists'.format(self._username)
        linki = [u'{}?page={}'.format(url, x) for x in range(start_page, end_page+1)]

        # ekstrakcja playlisty
        wykonawcy = []
        for link in linki:
            wykonawcy += self.looking4artist(link)
            print u'Przetwazanie strony: {} - OK'.format(link)
        self.artists = wykonawcy


    def get_concertList(self, limit = 1):
        '''
        Dla ulubionych artystow pobiera informacje o koncertach.
        Jesli brak artystow - nie robi nic.
        parametr "limit" - jaka czesc dostepnych atrystow ma zostac przeanalizowana.
        1 - calosc, 0 - nikt, 0.1 - 10% itd
        '''
        # jesli brak artystow
        if self.artists == []:
            print 'Brak artystow'
            return None

        # pobiera liste koncertow - iteruje po wykonawcach
        concerts = []

        # ilu artystow przeszukac
        if limit <= 0:
            ilosc = 0
        elif limit >= 1:
            ilosc = len(self.artists)
        else:
            ilosc = int(len(self.artists)*limit)
        
        iterator = 0
        for row in self.artists:
            if iterator >= ilosc:
                break
            else:
                try:
                    band_name = row[0]
                    band_object = band.BandFm(band_name)
                    band_object.get_events()
                    if len(band_object.events) > 0:
                        for element in band_object.events:
                            concerts.append(element)
                except:
                    print 'Cos poszlo nie tak dla zespolu >> {}'.format(band_name)
            iterator += 1

        self.concertList = concerts


    def to_json(self, folder = 'json'):
        '''
        Zrzuca scroble, artystow oraz koncerty do jsona.
        '''
        # przesluchane utwory -lista
        with open('{}/scrobbles.json'.format(folder), 'w') as outfile:
            json.dump(self.scrobbles, outfile, indent=4)
        # przesluchane utwory - slownik
        scrobble_keys = ['artist', 'title', 'date']
        scrobbles_with_keys = []
        for scrobble in self.scrobbles:
            scrobbles_with_keys.append(dict(zip(scrobble_keys, scrobble)))
        with open('{}/scrobblesDict.json'.format(folder), 'w') as outfile:
            json.dump(scrobbles_with_keys, outfile, indent=4)
        
        # ulubieni wykonawcy - lista
        with open('{}/artists.json'.format(folder), 'w') as outfile:
            json.dump(self.artists, outfile, indent=4)
        # ulubieni wykonawcy - slownik
        artist_keys = ['artist', 'url', 'scrobbles']
        artists_with_keys = []
        for artist in self.artists:
            artists_with_keys.append(dict(zip(artist_keys, artist)))
        with open('{}/artistsDict.json'.format(folder), 'w') as outfile:
            json.dump(artists_with_keys, outfile, indent=4)

        # koncerty - lista
        with open('{}/events.json'.format(folder), 'w') as outfile:
            json.dump(self.concertList, outfile, indent=4)
        # koncerty - dict
        event_keys = ['artist', 'title', 'date', 'lineup', 'place', 'city', 'country']
        events_with_keys = []
        for event in self.concertList:
            events_with_keys.append(dict(zip(event_keys, event)))
        with open('{}/eventsDict.json'.format(folder), 'w') as outfile:
            json.dump(events_with_keys, outfile, indent=4)
        
        print "Zapisano do formatu JSON w lokalizacji ./{}".format(folder)


    # pobieranie danych dotyczacych scrobbli
    def looking4music(self, url):
        '''
        Na wejsciu url, na wyjsciu lista
        zespol, tytul, data przesluchania
        jako lista.
        '''
        # docelowo ZESPOL, TYTUL, DATA
        soup = self.makeSoup(url)
        songs = soup.findAll("td", {"class" : "chartlist-name"})  # zawiera zesplol oraz utwor
        dates = soup.findAll("td", {"class" : "chartlist-timestamp"})  # zawiera daty

        #print len(songs), len(dates)

        playlista = []  # na gotowe kawalki

        for song in songs:
            x = song('a')
            try:
                playlista.append([x[0].string, x[1].string])
            except:
                playlista.append(['None', 'None'])


        spis_dat = []
        for date in dates:
            spis_dat.append([date.span['title']])

        if len(playlista) == len(spis_dat):
            new = zip(playlista, spis_dat)
            przesluchane = [list(elem[0] + elem[1]) for elem in new]
        else:
            przesluchane = []

        return przesluchane 


    # pobieranie danych dotyczacych wykonawcow
    def looking4artist(self, url):
        '''
        Na wejsciu URL do przeskanowania,
        na wyjsciu lista artystow: nazwa, ilosc scrobli, url do ich strony LFM.
        '''
        soup = self.makeSoup(url)
        raw_info = soup.findAll("a", {"class" : "countbar-bar-value"})
        page, name, count = [], [], []

        for paragraph in raw_info:
            href = paragraph['href']
            prefix = '/user/{}/library/music/'.format(self._username)

            # nazwa zespolu
            name.append(href.replace(prefix, ''))

            # strona profilu na last fm
            page.append('http://www.last.fm/music/{}'.format(name[-1]))

            # ile razy przesluchany
            count.append(paragraph.text.replace('scrobbles', ''))

        return zip(name, page, count)


    # FUNKCJE POMOCNICZE
    # stworz obiekt beautifulsoup z url
    def makeSoup(self, url):
        '''
        Podajesz URL, zwraca sparsowanego HTML'a.
        '''
        html = urllib.urlopen(url).read()
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)

        return soup


    # sprawdz ile stron w bibliotece
    def checkPages(self, soup):
        '''
        Na podstawie wejsciowego url'a sprawdza
        laczna ilosc stron w bibliotece.
        '''
        # find liczbe stron w bibliotece
        tags = soup.findAll("li", {"class" : "pages"})
        tag = tags[0]
        pages = tag.string.lstrip().split()[-1]

        return pages
