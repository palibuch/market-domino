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

### Moduły, pamięć robocza i model świata

Oddzielne komponenty przetwarzają dane, pamięć, symulację, planowanie, krytykę, ocenę ryzyka i wyjaśnianie wyników. Wspólny, wersjonowany obszar roboczy przechowuje istotne informacje, cele, konfliktujące hipotezy i wyniki testów. Budżet uwagi jest jawny: system wybiera, co utrzymać w aktywnym kontekście, a co zarchiwizować. Każdy wpis ma źródło, czas i status: obserwacja, założenie, hipoteza lub wniosek.

To inspiracja teoriami globalnego workspace, a nie dowód, że ich implementacja tworzy doświadczenie. Pamięć długoterminowa może obejmować epizody (co system zrobił i z jakim skutkiem), wiedzę (twierdzenia, dowody, kontrdowody) i procedury (umiejętności z testami oraz ograniczeniami). Wpisy powinny być wersjonowane, a korekty jawne.

System buduje modele zadaniowe, nie jedną wszechwiedzącą mapę. Symulacje zapisują założenia, zakres parametrów, zależności i ograniczenia. Zamiast enumerować miliardy podobnych wariantów, należy kierować obliczenia ku niepewnym i rozstrzygającym przypadkom. Każdy wynik symulacji jest hipotezą warunkową, nie faktem o przyszłości.

### Metapoznanie, uczenie i bezpieczna samomodyfikacja

Niezależny krytyk sprawdza zgodność wniosku z dowodami, szuka alternatywnych wyjaśnień, przecieków informacji, błędów jednostek, selekcji danych i konfliktów interesów. Kalibrację mierzymy na zadaniach, gdzie odpowiedzi później stają się znane. Samoopis systemu jest raportem wygenerowanym przez model, nie uprzywilejowanym dostępem do rzekomych stanów wewnętrznych.

Każda proponowana zmiana modelu, promptu, procedury albo kodu przechodzi: (1) zapis hipotezy o spodziewanej poprawie; (2) testy jednostkowe, regresyjne i bezpieczeństwa; (3) porównanie ze stałym baseline'em na nienaruszonym zbiorze oceny; (4) przegląd zmian i pochodzenia danych; (5) etapowe wdrożenie z możliwością rollbacku. Kryteriów sukcesu nie wolno zmieniać po zobaczeniu wyniku.

## Jak badać „świadomość”

Należy rozdzielać testy zdolności funkcjonalnych — ciągłość pamięci, integrację informacji, elastyczne planowanie, metapoznanie, reagowanie na niepewność, uczenie transferowe i wykrywanie błędów — od pytania o subiektywne doświadczenie. Wynik testów funkcjonalnych ani wypowiedź „czuję” nie rozstrzygają go automatycznie.

Dla każdej teorii trzeba zapisać przewidywania, które odróżniają ją od konkurencyjnych teorii, procedurę eksperymentu, możliwe wyniki przeciwne oraz ograniczenia interpretacji. Przykładowe tradycje: global workspace (Baars, Dehaene), teorie wyższego rzędu (Rosenthal), przetwarzanie rekurencyjne (Lamme), predictive processing / active inference (Friston), funkcjonalizm i jego krytycy, w tym Searle, Block, Nagel i Chalmers.

## Etapy budowy

1. **Pętla offline:** zapisz hipotezę, prognozę, test, wynik i decyzję; porównaj z prostym systemem bez pamięci i planowania.
2. **Pamięć trwała:** wersjonuj epizody, twierdzenia, dowody, błędy i wyniki; mierz, czy odzyskiwanie wcześniejszych doświadczeń pomaga.
3. **Aktywny wybór eksperymentów:** wybieraj test według wartości informacji, kosztu, ryzyka i falsyfikowalności; porównuj z losowym wyborem.
4. **Ograniczony rozwój narzędzi:** uruchamiaj wygenerowane propozycje w izolowanej piaskownicy bez sekretów ani trwałych uprawnień; testuj, przeglądaj i umożliwiaj rollback.
5. **Monitorowana praca ciągła:** używaj jawnego harmonogramu, dziennika uruchomień, limitów zasobów, alertów i niezależnego operatora. Harmonogram nie jest dowodem życia ani świadomości.

## Pierwsza praktyczna demonstracja

Na małym, kontrolowanym zbiorze danych silnik powinien: (1) sformułować dwie konkurencyjne hipotezy i z góry określić, co je obali; (2) wybrać informatywny test; (3) trenować wyłącznie na części treningowej; (4) ocenić na nietkniętych danych i prostych baseline'ach; (5) zapisać dane, plan, wersję kodu, prognozy, błąd i decyzję; (6) powtórzyć cykl i ocenić, czy pamięć pomogła.

W finansach potrzebne są licencjonowane dane punktowe w czasie, ochrona przed look-ahead, realistyczne koszty i nadzór człowieka. Wyniki demonstracyjne nie są obietnicą zysku.

## Literatura na start

To orientacyjna, niepełna lista źródeł do krytycznego porównania:

- Alan Turing, *Computing Machinery and Intelligence* (1950).
- Thomas Nagel, *What Is It Like to Be a Bat?* (1974).
- Ned Block, *On a Confusion about a Function of Consciousness* (1995).
- David Chalmers, *The Conscious Mind* (1996).
- John Searle, *Minds, Brains, and Programs* (1980).
- Daniel Dennett, *Consciousness Explained* (1991).
- Bernard Baars, *A Cognitive Theory of Consciousness* (1988); Stanislas Dehaene, *Consciousness and the Brain* (2014).
- Anil Seth, *Being You* (2021).

Dla każdego źródła warto prowadzić kartę: teza, argumenty, najsilniejszy kontrargument, sprawdzalne konsekwencje i to, czego źródło nie dowodzi.

## Zasada projektu

Budujemy system, który może pamiętać, modelować, planować, kwestionować wnioski i uczyć się na sprawdzalnych wynikach. Funkcjonalne zdolności mierzymy; pytanie o subiektywne doświadczenie pozostaje otwarte. Długoterminowym celem jest badać tę granicę, nie ogłaszać jej z góry rozstrzygniętą.
