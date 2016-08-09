# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 07:35:55 2016

@author: Przemyslaw Bieganski, bieg4n@gmail.com
"""
import urllib
from BeautifulSoup import *

class BandFm:
    '''
    Pajaczek pobiera informacje o zespole, a dokladniej
    glowne tagi go opisujace oraz informacje o koncertach (data, miejsce, lineup).
    '''
    
    def __init__(self, band_name):
        '''
        Band name musi byc z '+' zamiast spacji.
        Zeby byl lekkostrawny dla
        '''
        self._name = band_name
        self._base_url = 'http://www.last.fm/music/{}'.format(self._name)
        self._on_tour = False
        self._is_valid = self.validation()
        self.tags = []
        self.events = []
        
        self.__str__()
        self.get_tags()
    
    
    def __str__(self):
        '''
        Zwraca informacje podstawowe o obiekcie.
        '''
        print "Informacje o zespole: {}".format(self._name.replace('+', ' '))
        print "Strona bazowa zespolu: {}".format(self._base_url)
        print "Czy strona odpowiada: {}".format(self._is_valid)
        print "Czy zespol obecnie jest w trasie: {}".format(self._on_tour)
    
    
    # metody w klasie
    def validation(self):
        '''
        Sprawdza czy podana nazwa zespolu jest prawidlowa.
        Czy BeautifulSoup coś zwraca.
        '''
        # link do stronki do przestestowania
        url = self._base_url
        try:
            soup = self.makeSoup(url)
            self._on_tour = self.is_on_tour(soup)
            return True
        except:
            return False
    
    
    def is_on_tour(self, BeautifulSoupObject):
        '''
        Zwraca True jeśli zespol obecnie koncertuje,
        False jeśli nie koncertuje.
        '''
        # szukam info o trasie koncertowej
        koncert_info = BeautifulSoupObject.findAll("div", {"class" : '''
                header-title-label-wrap
                header-title-column-ellipsis-wrap
            '''}) # musi zostac taki dziki zapis klasy
        tour = koncert_info[0].findAll("a", {"class" : "label"})

        if tour == []:
            return False
        else:
            if tour[0].text == u'on tour':
                return True
            else:
                return False
    
    
    def get_events(self):
        '''
        Pobiera liste nadchodzacych koncertow.
        '''
        if self._on_tour is False or self._is_valid is False:
            self.events = []
            return None
        
        url = '{}/+events'.format(self._base_url)
        soup = self.makeSoup(url)
        
        # wyszukuje sekcji z koncertami
        when = soup.findAll("td", {"class" : "events-list-item-art"})
        who = soup.findAll("td", {"class" : "events-list-item-event"})
        where = soup.findAll("td", {"class" : "events-list-item-venue"})
        
        events = []
        
        for index in range(len(when)):
            try:
                event = []
                # nazwa imprezy 
                event.append(who[index].div.a.text)
                # data
                event.append(when[index].time["datetime"])
                # lineup
                lineup = self.clean_lineup(who[index].findAll("div", {"class" : "events-list-item-event--lineup"})[0].text)
                event.append(lineup)
                # nazwa miejscowki
                event.append(where[index].div.text)
                # miasto
                event.append(where[index].findAll("div", {"class" : "events-list-item-venue--city"})[0].text)
                # kraj
                event.append(where[index].findAll("div", {"class" : "events-list-item-venue--country"})[0].text)
                
                events.append(event)
            except:
                continue
        
        self.events = events
        
    
    
    def get_tags(self):
        '''
        Pobiera najpopularniejsze tagi jakimi został opisany wykonawca.
        '''
        # jesli url wadliwy
        if self._is_valid is False:
            self.tags = []
            return None
            
        url = self._base_url
        soup = self.makeSoup(url)
        
        # wyszukuje sekcje z tagami
        sekcja = soup.findAll("section", {"class" : "tag-section"})
        
        # pozyskuje tagi
        tags = sekcja[0].findAll("a")
        
        self.tags = [tag.text for tag in tags]
        
    
    
    # FUNKCJE POMOCNICZE

    # stworz obiekt beautifulsoup z url
    def makeSoup(self, url):
        '''
        Podajesz URL, zwraca sparsowanego HTML'a.
        '''
        html = urllib.urlopen(url).read()
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)
        
        return soup
    
    
    def clean_lineup(self, lineup):
        '''
        Porzadkuje string wesjciowy z lineupem.
        Dla pojedynczego wykonawcy zwraca nazwe tego wykonawcy.
        Dla kilku usuwa biale znaki i niepotrzebne linie.
        '''
        # gdy gra tylko jeden wykonawca
        if lineup == '':
            return [self._name.replace('+', ' ')]
        
        # gdy jest kilku
        artists = str(lineup).replace('\n', '').split(',')
        list_lineup = [x.lstrip() for x in artists]
        
        return list_lineup
    
    

#del x
band = BandFm("Sum+41")
band.get_events()
x = band.events