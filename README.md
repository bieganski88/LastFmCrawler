# LAST FM CRAWLER #

Aplikacja ma na celu stworzenie prostego pajączka zbierającego informacje z serwisu LastFm.
##### MODUŁY APLIKACJI #####
* crawlerMain.py - pobiera dane z konta LastFM zadanego użytkownika
* band.py - pobiera informacje o zadanym zespole, a dokładniej tagi go opisujące oraz informacje o koncertach
* geodecoder.py - dla listy koncertów wygenerowanych za pomocą band.py przypisuje lokalizację przestrzenna [klasa w opracowaniu].

##### WYMAGANE BIBLIOTEKI #####
Lista bibliotek zewnętrznych niezbędnych do prawidłowego działania aplikacji:
* urllib,
* BeautifulSoup,
* json.

### ZAWARTOŚĆ MODUŁU 'CRAWLER MAIN' ###
##### Klasa LastFmUser
Podczas instancjonowania klasa przyjmuje jeden parametr wejsciowy - nazwe uzytkownika LastFm, z którego kontem ma nawiązać połączenie.
###### Dostępne atrybuty:
* __artists__ - przechowuje listę przesłuchanych wykonawców,
* __scrobbles__ - przechowuje liste przesluchanych utworow wraz z datami
* __concertList__ - lista koncertow.

###### Główne metody w klasie:
* __str__ - zwraca podstawowe informacje o koncie, z którym nawiązano połączenie (liczbę stron w bibliotece utworów oraz bibliotece wykonawców)
* __get_scrobbles__ - pobiera informacje o przesluchanych utworach, jako  argument wejsciowy przyjmuje ilość stron z biblioteki utworów do splądrowania . Strony analizowane są od najnowszej do najstarszej. Wyniki zapisywane sa w __scrobbles__. Uwaga w przypadku pobierania całej biblioteki (np. ponad 1000 stron w bibliotece) może być to proces bardzo czasochłonny. Wartosc przetestować najpierw na mniejszej próbce.
* __get_artists__ - Pobiera informacje o najczęsciej słuchanych artystach. Argumentem wejściowym jest ilość stron z biblioteki do przeanalizowania, rozpoczynając od najpopularniejszych. Wyniki zapisywane są w __artists__.
* __get_concertList__ - wywołuje klasę __BandFm__ z modułu __band__, a następnie pobiera listę koncertów dla wszystkich artystów podpisanych obecnie pod __artists__. Wyniki zapisuje pod __concertList__.
* __to_json__ - zrzuca zawartość atrybutów artists, scrobbles oraz concertList do plików JSON. Struktura zapisu jest nastepująca: dla artystów >> [Nazwa zespolu,  adres URL, ilość odtworzeń];
dla utworów >> [Zespól, Nazwa utworu, Data Przesluchania]; dla koncertów >> [Nazwa imprezy, data, lineup imprezy, miejsce, miejscowość, kraj]
* __clean__ - czyści wartość atrubytów __artists__, __scrobbles__ oraz __concertList__.

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
