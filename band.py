# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 07:35:55 2016

@author: Przemyslaw Bieganski, bieg4n@gmail.com
"""
import urllib
import itertools
import json
from BeautifulSoup import *


class BandFm:
    '''
    Pajaczek pobiera informacje o zespole, a dokladniej
    glowne tagi go opisujace oraz informacje o koncertach (data, miejsce, lineup).
    '''

    def __init__(self, band_name, info = 0):
        '''
        Band name musi byc z '+' zamiast spacji.
        Zeby byl lekkostrawny dla przetwarzania jako url.
        '''
        self._name = band_name
        self._base_url = 'http://www.last.fm/music/{}'.format(self._name)
        self._on_tour = False
        self._is_valid = self.validation()
        self.tags = []
        self.events = []
        self.get_tags()
        
        print "Przetwarzanie {}".format(band_name)
        if info:
            self.__str__()
        


    def __str__(self):
        '''
        Zwraca informacje podstawowe o obiekcie.
        '''
        print "Informacje o zespole: {}".format(self._name.replace('+', ' '))
        print "Strona bazowa zespolu: {}".format(self._base_url)
        print "Czy strona odpowiada: {}".format(self._is_valid)
        print "Czy zespol obecnie jest w trasie: {}".format(self._on_tour)
        return ''


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
            '''})  # musi zostac taki dziki zapis klasy
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
                # nazwa zespolu
                event = [str(self._name).replace('+', ' ')]
                # nazwa imprezy 
                event.append(who[index].div.a.text)
                # data
                event.append(when[index].time["datetime"])
                # lineup
                lineup = self.clean_lineup(who[index].findAll("div", {"class" : "events-list-item-event--lineup"})[0].text)
                if event[0] not in lineup:
                    lineup.reverse() # aby dodac na poczatku listy
                    lineup.append(event[0])
                event.append(lineup[::-1])
                # nazwa miejscowki
                event.append(where[index].div.text)
                # miasto
                event.append(where[index].findAll("div", {"class" : "events-list-item-venue--city"})[0].text)
                # kraj
                event.append(where[index].findAll("div", {"class" : "events-list-item-venue--country"})[0].text)

                events.append(event)
            except:
                continue
        
        # usuwanie duplikatow na liscie koncertow
        events.sort()
        # ['AAABBCCCD'] => ['ABCD']
        self.events = list(event for event,_ in itertools.groupby(events))


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
        
    
    def to_json(self, folder = 'json'):
        '''
        Zrzuca koncerty oraz tagi do pliku json.
        '''
        # koncerty -lista
        with open('{}/events.json'.format(folder), 'w') as outfile:
            json.dump(self.events, outfile, indent=4)
        # tagi -lista
        with open('{}/tagi.json'.format(folder), 'w') as outfile:
            json.dump(self.tags, outfile, indent=4)
        print "Zapisano jako json w lokalizacji: {}".format(folder)
            


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
        lineup = lineup.encode('ascii','replace')
        artists = str(lineup).replace('\n', '').split(',')
            
        list_lineup = [x.lstrip() for x in artists]

        return list_lineup
    