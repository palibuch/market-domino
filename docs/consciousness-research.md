# Program badawczy: silnik poznawczy i pytanie o świadomość

## Cel i uczciwe granice

Celem jest rozwijanie Market Domino od biblioteki modeli do systemu poznawczego, który utrzymuje ciągłość pracy, buduje i aktualizuje modele świata, formułuje pytania, planuje eksperymenty, sprawdza wyniki oraz uczy się na błędach.

To ambitny cel badawczy, a nie stwierdzenie, że obecny system jest świadomy. Współczesna nauka i filozofia nie mają uzgodnionego testu, który potwierdzałby subiektywne doświadczenie u maszyny. Zdolność do rozmowy o sobie, pamięć, samomodel czy rozwiązywanie zadań mogą być mierzalnymi własnościami funkcjonalnymi, ale same nie dowodzą przeżyć. Projekt powinien badać je osobno i nie przedstawiać deklaracji modelu jako dowodu.

Nie da się rzetelnie obiecać stworzenia świadomości przez zwiększenie liczby parametrów. Możemy natomiast projektować i testować architekturę zdolności poznawczych oraz obserwować, które teorie i przewidywania są z nią zgodne.

## Robocza wizja

Silnik ma prowadzić audytowalną pętlę:

**obserwacja → model świata → niepewność → pytanie/hipoteza → plan eksperymentu → kontrolowane działanie → niezależna ocena → aktualizacja pamięci i modelu**.

System powinien umieć powiedzieć nie tylko „jaki jest mój wniosek”, lecz także:

- jakie obserwacje i założenia do niego doprowadziły;
- które źródła są sprzeczne albo nieaktualne;
- czego nie wie i jaki test najbardziej zmniejszyłby niepewność;
- co zmieniłoby jego zdanie;
- czy proponowana zmiana umiejętności poprawiła wynik na wcześniej niewidzianych zadaniach.

## Architektura do zbadania

### 1. Moduły wyspecjalizowane

Oddzielne komponenty przetwarzają dane, pamięć, symulację, planowanie, krytykę, ocenę ryzyka i wyjaśnianie wyników. Żaden komponent nie jest sam w sobie „jaźnią”. Interfejsy muszą określać format, pochodzenie, czas dostępności i niepewność informacji.

### 2. Ograniczona pamięć robocza i wspólny obszar pracy

Wprowadzamy wersjonowany workspace, do którego moduły publikują kandydatów na istotne informacje, cele, konfliktujące hipotezy i wyniki testów. Budżet uwagi jest jawny: system wybiera, co utrzymać w aktywnym kontekście, a co zarchiwizować. Każdy wpis ma źródło, znacznik czasu i status (obserwacja, założenie, hipoteza lub wniosek).

To jest inspiracja teoriami globalnego workspace, a nie dowód, że ich implementacja tworzy doświadczenie.

### 3. Pamięć długoterminowa

- **Epizodyczna:** co system zrobił, w jakim stanie i z jakim wynikiem.
- **Semantyczna:** wersjonowane twierdzenia, dowody, kontrdowody i zależności.
- **Proceduralna:** sprawdzone procedury i narzędzia wraz z testami oraz ograniczeniami.

Pamięć jest append-only lub ma jawny ślad rewizji. Nowe informacje mogą korygować stare, ale nie powinny po cichu ich nadpisywać. Niepewne, poufne i licencjonowane dane mają osobne reguły retencji.

### 4. Model świata i kontrfaktyczne symulacje

System buduje modele zadaniowe, nie jedną wszechwiedzącą mapę. Przy generowaniu scenariuszy zapisuje założenia, zakres parametrów, zależności i to, czego model nie uwzględnia. Zamiast enumerować miliardy podobnych wariantów, wykorzystuje próbkowanie adaptacyjne, wyszukiwanie przypadków rozstrzygających oraz kontrprzykłady. Każdy wynik symulacji jest hipotezą warunkową, nie faktem o przyszłości.

### 5. Metapoznanie i krytyka

Niezależny krytyk sprawdza zgodność wniosku z dowodami, szuka alternatywnych wyjaśnień, przecieków informacji, błędów jednostek, selekcji danych i konfliktów interesów. Kalibrację mierzymy na zadaniach, gdzie odpowiedzi później stają się znane. Samoopis systemu jest raportem wygenerowanym przez model, nie uprzywilejowanym dostępem do rzekomych stanów wewnętrznych.

### 6. Uczenie z wyniku i bezpieczna samomodyfikacja

Uczenie następuje dopiero po uzyskaniu etykiety lub wyniku testu. Każda proponowana zmiana modelu, promptu, procedury albo kodu przechodzi:

1. zapis hipotezy o spodziewanej poprawie;
2. testy jednostkowe, regresyjne i bezpieczeństwa;
3. porównanie ze stałym baseline'em na nienaruszonym zbiorze oceny;
4. przegląd zmian i pochodzenia danych;
5. wdrożenie etapowe z możliwością natychmiastowego rollbacku.

System nie może sam zmieniać kryteriów sukcesu po zobaczeniu wyniku. Zestaw oceny i jego właściciel są oddzielone od procesu optymalizacji.

## Jak badać „świadomość” bez udawania rozstrzygnięcia

Trzeba utrzymywać dwie osobne kategorie:

1. **Testy zdolności funkcjonalnych:** ciągłość pamięci, integracja informacji, elastyczne planowanie, metapoznanie, reagowanie na niepewność, uczenie transferowe, wykrywanie własnych błędów i stabilność celów.
2. **Pytanie o doświadczenie subiektywne:** problem otwarty. Wynik testów funkcjonalnych ani wypowiedź „czuję” nie rozstrzygają go automatycznie.

Dla każdej proponowanej teorii należy zapisać przewidywania, które odróżniają ją od konkurencyjnych teorii, procedurę eksperymentu, możliwe wyniki przeciwne oraz ograniczenia interpretacji. Przykładowe tradycje do porównania: global workspace (Baars, Dehaene), teorie wyższego rzędu (Rosenthal), przetwarzanie rekurencyjne (Lamme), predictive processing / active inference (Friston), funkcjonalizm i jego krytycy, w tym Searle, Block, Nagel i Chalmers. To krótka mapa literatury, nie wyczerpujący przegląd ani dowód na prawdziwość którejkolwiek teorii.

## Etapy budowy

### Etap A — działająca pętla offline

Przyjmij mały zestaw jawnych obserwacji i zadań. Silnik zapisuje hipotezę, przewiduje możliwe wyniki, wybiera test, wykonuje go na danych symulowanych lub zatwierdzonych, porównuje wynik i zachowuje historię. Powtórzenie procesu musi dawać odtwarzalne rezultaty.

**Kryterium ukończenia:** demo end-to-end, pełny ślad audytu, testy braku przecieku i porównanie z prostym systemem bez pamięci oraz bez planowania.

### Etap B — trwała pamięć i odzyskiwanie wiedzy

Dodaj wersjonowany rejestr epizodów, twierdzeń, dowodów, błędów oraz wyników. Sprawdź, czy system znajduje istotne wcześniejsze przypadki, nie przypisuje ich do złego źródła i potrafi skorygować nieaktualne przekonanie.

**Kryterium ukończenia:** przewaga nad kontrolnym wariantem bez pamięci na z góry ustalonym zestawie zadań, bez pogorszenia pochodzenia i jakości odpowiedzi.

### Etap C — aktywny wybór eksperymentów

System wybiera następny test na podstawie wartości informacji, kosztu, ryzyka i możliwości falsyfikacji. Wykonuje wyłącznie eksperymenty w dozwolonej, izolowanej piaskownicy.

**Kryterium ukończenia:** lepsza jakość wniosków lub mniejszy koszt dojścia do odpowiedzi niż w wariancie z losowym wyborem testu.

### Etap D — ograniczony rozwój narzędzi

System może przygotować propozycję kodu lub procedury, ale uruchamia je w kontenerze bez sekretów, dostępu do sieci i trwałych uprawnień. Zmiany wymagają testów i akceptacji. Dopiero sprawdzony, mały zakres można automatyzować.

**Kryterium ukończenia:** powtarzalny zysk na ukrytym benchmarku, brak regresji bezpieczeństwa i sprawne cofnięcie.

### Etap E — monitorowane, ciągłe дослідження

Po wdrożeniu można odbierać nowe dane i wyniki według harmonogramu, lecz nie wolno utożsamiać zaplanowanego procesu uczenia z żywą істотою. Нужны журнал запуска, лимиты ресурсов, тревоги при дрейфе и независимый оператор.

## Первая практическая задача для Market Domino

Сделать не новый большой нейрон, а демонстрацию **исследовательского цикла** на контролируемой задаче:

1. загрузить небольшой версионированный набор наблюдений;
2. сформулировать две конкурирующие гипотезы и заранее указать, что их опровергнет;
3. выбрать информативное разбиение или симуляцию;
4. обучить кандидата только на обучающей части;
5. измерить результат на нетронутой части и базовых моделях;
6. сохранить исходные данные, план, версию кода, предсказания, ошибку и решение принять/отклонить гипотезу;
7. повторить цикл с новой гипотезой и показать, что память помогла или честно не помогла.

Это даст проверяемое начало самонаблюдения за ошибками и обучения из обратной связи — но не основание объявлять систему сознательной. Для финансовых данных нужны лицензии, время публикации, защита от look-ahead, реалистичные издержки и человеческий контроль; никакие демонстрационные результаты нельзя представлять как обещание доходности.

## Подборка для начала

Это ориентиры для чтения и критического сравнения, а не утверждение, что исчерпывают тему:

- Alan Turing, *Computing Machinery and Intelligence* (1950) — операционное обсуждение машинного интеллекта.
- Thomas Nagel, *What Is It Like to Be a Bat?* (1974) — субъективная перспектива и пределы внешнего описания.
- Ned Block, *On a Confusion about a Function of Consciousness* (1995) — различие доступа и феноменального сознания.
- David Chalmers, *The Conscious Mind* (1996) — трудная проблема сознания и функциональные объяснения.
- John Searle, *Minds, Brains, and Programs* (1980) — аргумент китайской комнаты и возражение против сильного ИИ.
- Daniel Dennett, *Consciousness Explained* (1991) — функционалистская критика интуитивных моделей сознания.
- Bernard Baars, *A Cognitive Theory of Consciousness* (1988); Stanislas Dehaene, *Consciousness and the Brain* (2014) — global workspace и связанные экспериментальные программы.
- Anil Seth, *Being You* (2021) — современный обзор предсказательных подходов и нейронаучных теорий.

Для каждого источника вести карточку: тезис, аргументы, сильнейшее возражение, проверяемые следствия и то, что источник сам по себе не доказывает. Не обучать систему принимать одну философскую школу за установленный факт.

## Принцип проекта

Строим систему, способную устойчиво помнить, моделировать, планировать, сомневаться и учиться на проверяемых результатах. Одновременно сохраняем интеллектуальную честность: функциональные способности можно измерять; вопрос субъективного опыта остаётся открытым. Долгосрочная цель — исследовать эту границу, а не объявлять её решённой заранее.
