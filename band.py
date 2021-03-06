# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 07:35:55 2016

@author: Przemyslaw Bieganski, bieg4n@gmail.com
"""
# import modulow
import urllib
import itertools
import json
import os
from BeautifulSoup import BeautifulSoup


class BandFm(object):
    '''
    Pobiera informacje o zespole, a dokladniej
    glowne tagi go opisujace oraz informacje o koncertach (data, miejsce, lineup).
    '''

    def __init__(self, band_name, info=0):
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
            soup = self.make_soup(url)
            self._on_tour = self.is_on_tour(soup)
            return True
        except:
            return False


    def is_on_tour(self, beautiful_soup_object):
        '''
        Zwraca True jeśli zespol obecnie koncertuje,
        False jeśli nie koncertuje.
        '''
        # szukam info o trasie koncertowej
        koncert_info = beautiful_soup_object.findAll("div", {"class" : '''
                header-title-label-wrap
                header-title-column-ellipsis-wrap
            '''})  # musi zostac taki dziki zapis klasy
        tour = koncert_info[0].findAll("a", {"class" : "label"})

        if tour == []:
            return False
        else:
            return bool(tour[0].text == u'on tour')



    def get_events(self):
        '''
        Pobiera liste nadchodzacych koncertow.
        '''
        if self._on_tour is False or self._is_valid is False:
            self.events = []
            return None

        url = '{}/+events'.format(self._base_url)
        soup = self.make_soup(url)

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
        self.events = list(event for event, _ in itertools.groupby(events))


    def get_tags(self):
        '''
        Pobiera najpopularniejsze tagi jakimi został opisany wykonawca.
        '''
        # jesli url wadliwy
        if self._is_valid is False:
            self.tags = []
            return None

        url = self._base_url
        soup = self.make_soup(url)

        # wyszukuje sekcje z tagami
        sekcja = soup.findAll("section", {"class" : "tag-section"})

        # pozyskuje tagi
        tags = sekcja[0].findAll("a")

        self.tags = [tag.text for tag in tags]


    def to_json(self, folder='json'):
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
    def make_soup(self, url):
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
        lineup = lineup.encode('ascii', 'replace')
        artists = str(lineup).replace('\n', '').split(',')

        list_lineup = [x.lstrip() for x in artists]

        return list_lineup


def zespoly_z_listy(src_path, dest_path):
    '''
    Kolejno dla kazdego zespolu z listy ZAPISANEJ JAKO JSON wyszukiwane sa informacje
    o koncertach. Zwracane są pliki JSON z wynikami, ktore pozniej mozna poddac geokodowaniu.
    Dwa parametry wejsciowe: sciezka do pliku JSON z zespolami
    oraz sciezka do zapisu danych wynikowych (katalog musi juz istniec).
    '''
    # test czy podane lokalizacje w ogole istnieja
    if not os.path.isfile(src_path):
        return u'Brak pliku wejsciowego w zadeklarowanej lokalizacji.'
    if not os.path.isdir(dest_path):
        return u'Zadeklarowany folder wynikowy nie istnieje. Prosze sprawdzic parametry wejsciowe\
        i sprobowac ponownie.'
    # wczytywanie danych
    try:
        with open(src_path) as json_data:
            band_list = json.load(json_data)[0] # aby pozbyc sie zagniezdzenia
    except:
        return u'Nie udalo sie zaladowac danych z pliku json.'

    # iteracja po elementach listy
    events = []
    for band in band_list:
        band = band.replace(' ', '+') # adres url nie lubi spacji
        artist = BandFm(band, info=0)
        artist.get_events()
        print '{} >>Liczba koncertow: {}'.format(artist._name, len(artist.events))
        # scalam wyniki
        for event in artist.events:
            events.append(event)

    # eksport do json
    with open('{}/events.json'.format(dest_path), 'w') as outfile:
        json.dump(events, outfile, indent=4)

    return "Zakonczono przetwarzanie listy."
