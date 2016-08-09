# -*- coding: utf-8 -*-
"""
Created on Fri Jul 22 22:16:20 2016

@author: Przemyslaw Bieganski, bieg4n@gmail.com

Crawler LastFm - pobiera informacje o przesluchanych utworach, sluchanych wykonawcach,
znajomych.
Zawiera glowna klase: LastFmUser.

"""

import urllib
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
        self._nrOfPages = self.get_info() # klucze: 'scrobbles', 'artists'
        self.artists = []
        self.scrobbles = []
    
    
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
        Przywraca wartosci poczatkowe dla self.artists oraz self.scrobbles
        '''
        self.artists = []
        self.scrobbles = []
    
    
    
    def get_scrobbles(self, number_of_pages):
        '''
        Pobiera informacje o przesluchanych utworach z zadanej ilosci stron.
        '''
        if number_of_pages > self._nrOfPages['scrobbles']:
            print 'Zbyt duzy argument wejsciowy'
            return None
            
        # generuje linki dla stron do sprawdzenia
        url = u'http://www.last.fm/user/{}/library'.format(self._username)
        linki = [u'{}?page={}'.format(url, x+1) for x in range(number_of_pages)]
        
        # ekstrakcja playlisty
        przesluchane = []
        for link in linki:
            print u'Przetwazanie strony: {}'.format(link)
            przesluchane += self.looking4music(link)
            print 'ok'
        self.scrobbles = przesluchane
    
    
    
    def get_artists(self, number_of_pages):
        '''
        Pobiera informacje o ulubionych artystach z zdanej ilosci stron.
        '''
        if number_of_pages > self._nrOfPages['artists']:
            print 'Zbyt duzy argument wejsciowy'
            return None
        
        # generuje linki dla stron do sprawdzenia
        url = u'http://www.last.fm/user/{}/library/artists'.format(self._username)
        linki = [u'{}?page={}'.format(url, x+1) for x in range(number_of_pages)]
        
        # ekstrakcja playlisty
        wykonawcy = []
        for link in linki:
            print u'Przetwazanie strony: {}'.format(link)
            wykonawcy += self.looking4artist(link)
            print 'ok'
        self.artists = wykonawcy
        
    
    
    # pobieranie danych dotyczacych scrobbli
    def looking4music(self, url):
        '''
        Na wejsciu url, na wyjsciu lista
        zespol, tytul, data przesluchania
        jako lista.
        '''
        # docelowo ZESPOL, TYTUL, DATA
        soup = self.makeSoup(url)
        songs = soup.findAll("td", {"class" : "chartlist-name"}) # zawiera zesplol oraz utwor
        dates = soup.findAll("td", {"class" : "chartlist-timestamp"}) # zawiera daty
        
        print len(songs), len(dates)
        
        playlista = [] # na gotowe kawalki
        
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
        
        


# WYWOLANIA
user= LastFmUser('Biegan')