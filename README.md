# LAST FM CRAWLER #
Web Crawler wyszukujący informacje w serwisie LastFm. Informacje pobierane są w oparciu o nazwę zespołu, lub bazując na podanej nazwie użytkownika. Więcej informacji przy opisie klas poniżej.
##### MODUŁY APLIKACJI #####
* CrawlerMain.py - odpowiedzialny za interakcje z kontem LastFm zadanego użytkownika
* band.py - pobiera informacje o zadanym zespole, a dokładniej tagi go opisujące oraz informacje o koncertach
* geocoder.py - dla listy koncertów z pliku JSON przypisuje lokalizację przestrzenna, w oparciu o Google Maps API (dla nowych lokalizacji). Gromadzi informacje o poznanych miejscach. Eksportuje dane do GeoJson oraz bazy danych  Sqlite3.
* example.py - zawiera szereg przykładów ułatwiających zapoznanie się z poszczególnymi funkcjonalnościami oraz procesem pozyskiwania danych.

##### WYMAGANE BIBLIOTEKI #####
Lista bibliotek zewnętrznych niezbędnych do prawidłowego działania aplikacji:
* urllib,
* BeautifulSoup,
* json
* sqlite3

### ZAWARTOŚĆ MODUŁU 'CrawlerMain' ###
##### Klasa LastFmUser
Podczas instancjonowania klasa przyjmuje jeden parametr wejsciowy - nazwe uzytkownika LastFm, z którego kontem ma nawiązać połączenie.
###### Dostępne atrybuty:
* __.artists__ - przechowuje listę słuchanych artystów przez podanego użytkownika, lista artystów zależy od parametrów wejściowych metod pobierających informacje o artystach: get_artists_recent() oraz get_artists_all_time().
* __.scrobbles__ - przechowuje liste przesluchanych utworow wraz z datą i godziną. Lista utworów zasilana jest poprzez wywołanie metody get_scrobbles().
* __.concertList__ - lista koncertow. Wyszukiwane informacje o koncertach dla listy zespołów przechowywanej w ````artists````. Dla każdego z koncertów wyszukiwane są następujące informacje:
artist, city, title, country, place, date, lineup.

###### Metody:
* __str()__ - zwraca podstawowe informacje o koncie, z którym nawiązano połączenie (liczbę stron w bibliotece utworów oraz bibliotece wykonawców)
* __.get_info()__ - zwraca dicitionary z dwoma kluczami ````scrobbles```` oraz ````artists````. Zawierającymi informacje o liczbie stron w bibliotece dopowiednio dla przesluchanych utworów oraz wykonawców.
* __.get_scrobbles(start_page, end_page)__ - pobiera informacje o przesluchanych utworach, jako  argument wejsciowy przyjmuje dwie wartosci: numer strony początkowej oraz końcowej z bibilioteki do przeanalizowania. Wyniki zapisywane sa w __scrobbles__. Uwaga w przypadku pobierania całej biblioteki (np. ponad 1000 stron w bibliotece) może być to proces bardzo czasochłonny. Wartosc przetestować najpierw na mniejszej próbce. Po 50 utworów na stronie.
* __get_artists_all_time(start_page, end_page)__ - Pobiera informacje o najczęsciej słuchanych artystach. Dwa parametry wejsciowe: indeks strony poczatkowej oraz koncowej z biblioteki wykonawcow do przeanalizowania. Wyniki zapisywane są w __artists__. Pierwsza strona oznacza najpopularniejszych atrystów. Po 50 zespołów na stronie. 
* __get_artists_recent(*args)__ - Pobiera informacje o ostatnio słuchanych artystach. Przyjmuje nastepujace wartości dla argumentu wejściowego: '7', '30', '90', '180', '365'. Muszą być typu tekstowego. Dzięki temu zostanie pobrane zestawienie 50 najczęściej słychanych wykonawców z ostatnich 7, 30, 90, 180, 365 dni. Wyniki zapisywane są w __artists__.
* __get_concertList(limit)__ - Dla każdego artysty znajdującego się na liście ````artists```` tworzy obiekt klasy __BandFm__ z modułu __band__, a następnie pobiera listę koncertów. Wyniki zapisuje pod __concertList__. Parametr wejściowy ````limit```` określa jaka część artystów z listy ma zostać przetworzona (wartość z zakresu 0 do 1, domyslnie 1). Czy jeśli na liście widnieje 100 artystów, a parametr ustawimy na 0.2, wydarzenia zostaną wyszukane dla 20 pierwszych.
* __to_json(folder)__ - zrzuca zawartość atrybutów artists, scrobbles oraz concertList do plików JSON. oOpcjonalny parametr wejściowy to ścieżka do folderu gdzie mają zostać zapisane wyniki. Struktura zapisu jest nastepująca: dla artystów >> [Nazwa zespolu,  adres URL, ilość odtworzeń]; dla utworów >> [Zespól, Nazwa utworu, Data Przesluchania]; dla koncertów >> [Nazwa imprezy, data, lineup imprezy, miejsce, miejscowość, kraj]. Dane zapisywane są dwukrotnie - raz w postaci listy wartości, drugi raz w postaci słownika klucz-wartość.
* __clean()__ - zeruje wartość atrubytów __artists__, __scrobbles__ oraz __concertList__.

##### Przykład:
````
# instancjonowanie klasy LastFmUser
user = crawlerMain.LastFmUser('Biegan')

# wyswietlanie informacji o nawiazanym polaczeniu
str(user)

# pobieram fragment histori sluchanych utworow, od strony 1 do 5 - czyli lacznie 250 rekordow
user.get_scrobbles(1, 5)

# wyswietlam kilka pierwszych rekordow
print user.scrobbles[:5]

# pobieram informacje o najpopularniejszych wykonawcach
user.get_artists_all_time(3, 5)

# wyswietlam kilka przykladowych rekordow dotyczacych artystow
print user.artists[:5]

# pobieram informacje o koncertach, dla 20% wykonawców
user.get_concertList(0.2)

# export danych do json
user.to_json('example/example3')
````

###### Fragment pliku JSON z przesłuchanymi utworami - wersja list
````
[
    [
        "Percival Schuttenbach", 
        "You're... Immortal?", 
        "Monday 14 Nov 2016, 5:43pm"
    ], 
]
````
###### Fragment pliku JSON z przesłuchanymi utworami - wersja dict
````
[
    {
        "date": "Monday 14 Nov 2016, 5:43pm", 
        "title": "You're... Immortal?", 
        "artist": "Percival Schuttenbach"
    }, 
]
````

### ZAWARTOŚĆ MODUŁU 'band' ###
##### Klasa BandFm
Podczas instancjonowania klasa przyjmuje jeden argument wejściowy - nazwę zespołu - o którym ma pobrać informacje.
###### Dostępne atrybuty:
* __tags__ - przechowuje tagi, którymi został opisany zespół
* __events__ - przechowuje informacje o przyszłych koncertach, jeżeli zespół jest obecnie w trasie koncertowej.

###### Główne metody w klasie:
* __str__ - zwraca podstawowe informacje o zespole: czy strona odpowiada, czy zespół obecnie jest w trasie koncertowej
* __get_events__ - pobiera listę nadchodzących koncertów, o ile wykonawca jest w trasie koncertowej
* __get_tags__ - pobiera najpopularniejsze tagi jakimi został opisany wykonawca

#### W pliku example.py zawarte zostały przykłady użycia powyższych klas.

### ZAWARTOŚĆ MODUŁU 'geocoder' ###
##### Klasa Geocoder
Podczas instancjonowania przyjmuje trzy parametry wejściowe APIKEY - klucz do Google Maps API - wykorzystywana będzie usługa geokodowania,
SRCFILE - ścieżka do pliku wejściowego z listą koncertów w formacie JSON,  DESTPATH - ścieżka do zapisu plików wynikowych, zawierającego to samo co plik wejściowy plus współrzędne geograficzne.
###### Dostępne atrybuty:
* __data__ - przechowuje zaczytane dane źródłowe
* __results__ - przechowuje wyniki, czyli informacje o koncertach wraz z georeferencją

###### Główne metody w klasie:
* __str__ - 
* __process__ - pobiera geolokalizację dla koncertów, lokalizacja określana jest z dokładnością do miasta. nieznane lokalizacje sprawdza za pomocą Google Maps Geocoding API. raz sprawdzona miejscowość trafia do pomocniczej bazy danych, tak żeby sprawdzać jej już kolejny raz za pomocą API.
* __exportToJSON__ - eksportuje wyniki do pliku JSON w folderze wynikowym
* __exportToDB__ - eksportuje wyniki do tabeli w bazie danych SQLite w folderze wynikowym

