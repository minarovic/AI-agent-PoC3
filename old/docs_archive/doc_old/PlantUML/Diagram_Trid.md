startuml
' Příručka pro AI Agenta: Tvorba Diagramů Tříd v PlantUML

' --- Myšlenkový pochod (Chain of Thought) pro tvorbu této příručky ---
' 1. Cíl: Vytvořit stručnou a jasnou příručku pro AI agenta specificky pro Diagramy Tříd.
' 2. Klíčové prvky Diagramu Tříd:
'    - Definice tříd (včetně abstraktních, rozhraní, výčtů).
'    - Atributy (název, typ, viditelnost, statické, pouze pro čtení).
'    - Metody (název, parametry, návratový typ, viditelnost, abstraktní, statické).
'    - Značky viditelnosti (+, -, #, ~).
'    - Vztahy (dědičnost, implementace, asociace, agregace, kompozice, závislost).
'    - Kardinalita.
'    - Poznámky.
'    - Seskupování (Packages).
' 3. Struktura příručky: Úvod -> Základní syntaxe -> Definice tříd a členů -> Vztahy -> Ostatní prvky -> Tipy pro AI.
' 4. Jazyk: Čeština, srozumitelné pro AI.
' 5. Formát: PlantUML komentáře a jednoduché diagramy jako ilustrace.
' --- Konec myšlenkového pochodu ---

' === Úvod ===
' Diagram Tříd popisuje strukturu systému zobrazením tříd, jejich atributů, metod a vztahů mezi nimi.
' Je to statický strukturní diagram UML.
' Pro AI agenta je užitečný k:
'   - Pochopení a generování objektově orientovaného návrhu.
'   - Definování datových struktur, jejich vlastností a chování.
'   - Specifikaci kontraktů a vztahů mezi různými entitami v systému.

' === 1. Základní Syntaxe ===
' Každý PlantUML diagram začíná @startuml a končí @enduml.

' === 2. Definice Tříd, Rozhraní a Výčtů ===
' -- 2.1 Třídy (Classes) --
' Definují se klíčovým slovem 'class'.
' Aliasy se definují pomocí 'as'.
class Uzivatel
class "Třída s mezerami" as TridaSM

note right of Uzivatel
  Třídy jsou základními stavebními bloky
  objektově orientovaného návrhu.
  Mohou obsahovat atributy a metody.
end note

' -- 2.2 Abstraktní Třídy (Abstract Classes) --
' Definují se pomocí 'abstract class' nebo 'abstract NazevTridy'.
' Název abstraktní třídy a jejích abstraktních metod se typicky zobrazuje kurzívou.
abstract class Zvire
abstract class Plaz
Zvire <|-- Plaz

' -- 2.3 Rozhraní (Interfaces) --
' Definují se pomocí 'interface NazevRozhrani'.
' Mohou být také definovány zkráceně pomocí () "Název" jako u komponent, ale 'interface' je explicitnější.
interface Pohyblivy
interface Letajici

' -- 2.4 Výčtové Typy (Enums) --
' Definují se pomocí 'enum NazevEnum'.
enum DenVTydnu {
  PONDELI
  UTERY
  STREDA
  CTVRTEK
  PATEK
  SOBOTA
  NEDELE
}
enum Barva {
  CERVENA
  ZELENA
  MODRA
}

' === 3. Členy Třídy: Atributy a Metody ===
' -- 3.1 Atributy (Fields/Attributes) --
' Definují se uvnitř bloku třídy {...} nebo přímo pod názvem třídy.
' Syntaxe: [viditelnost] nazevAtributu: Typ [= vychoziHodnota]
' Modifikátory: {static}, {readonly} (nebo {readOnly})
class Produkt {
  -id: int
  +nazev: String
  #cena: double
  skladem: boolean = true ' Atribut s výchozí hodnotou
  {static} DPH: double = 0.21 ' Statický atribut
  {readonly} KOD_PRODUKTU: String ' Atribut pouze pro čtení
}

' -- 3.2 Metody (Methods/Operations) --
' Definují se uvnitř bloku třídy {...} nebo přímo pod názvem třídy.
' Syntaxe: [viditelnost] nazevMetody([parametry]): NavratovyTyp
' Parametry: nazevParametru: TypParametru, ...
' Modifikátory: {abstract}, {static}
abstract class ZpracovatelObjednavky { ' Přejmenováno pro lepší příklad abstraktní metody
    {abstract} #zpracujPlatbu(metoda: String): boolean ' Abstraktní metoda
}
class Objednavka extends ZpracovatelObjednavky {
  +pridejPolozku(polozka: Produkt, mnozstvi: int): void
  -vypocitejCelkovouCenu(): double
  #zpracujPlatbu(metoda: String): boolean ' Implementace abstraktní metody
  {static} +zjistiMaximalniPocetPolozek(): int ' Statická metoda
}

' -- 3.3 Viditelnost (Visibility) --
' + public (veřejný)
' - private (soukromý)
' # protected (chráněný)
' ~ package private / default (viditelný v rámci balíčku) - často výchozí, pokud není specifikováno

' === 4. Vztahy mezi Třídami ===
' -- 4.1 Dědičnost (Generalization) --
' Značí se šipkou s nevyplněným trojúhelníkovým hrotem: <|--
' TřídaPotomek <|-- TridaRodic
class Auto
class AutoPersonalni
class AutoNakladni
AutoPersonalni <|-- Auto ' AutoPersonalni dědí od Auto
AutoNakladni <|-- Auto ' AutoNakladni dědí od Auto

' -- 4.2 Implementace Rozhraní (Realization) --
' Značí se přerušovanou šipkou s nevyplněným trojúhelníkovým hrotem: <|..  nebo ..|>
class Ptak implements Letajici, Pohyblivy ' Alternativní syntaxe
Ptak <|.. Letajici
Ptak <|.. Pohyblivy

' -- 4.3 Asociace (Association) --
' Reprezentuje obecný vztah mezi třídami.
' Plná čára: -- (obousměrná) nebo --> (jednosměrná navigovatelnost).
' Může mít název, role na koncích a kardinalitu.
class Student
class Kurz
Student "0..*" --> "1..*" Kurz : "navštěvuje >"
' Popisek "navštěvuje >" znamená, že Student navštěvuje Kurz. Šipka u popisku ukazuje směr čtení.
' Šipka na konci spojnice (-->) ukazuje navigovatelnost (Student ví o Kurzu).

' -- 4.4 Agregace (Aggregation) --
' "Má" vztah (has-a), kde část může existovat nezávisle na celku.
' Značí se plnou čárou s nevyplněným kosočtvercem na straně celku: o--
class Adresa
Uzivatel "1" o-- "0..*" Adresa : "má adresu" ' Uživatel může mít více adres, adresa může existovat i bez uživatele

' -- 4.5 Kompozice (Composition) --
' Silný "je složen z / vlastní" vztah (owns-a), kde část nemůže existovat bez celku.
' Značí se plnou čárou s vyplněným kosočtvercem na straně celku: *--
class Motor
Auto "1" *-- "1" Motor : "je složen z" ' Auto je složeno z jednoho motoru, motor neexistuje bez auta

' -- 4.6 Závislost (Dependency) --
' Slabý vztah, kde jedna třída závisí na druhé (např. používá ji jako parametr metody, vytváří její instanci).
' Značí se přerušovanou šipkou: ..>
class Tiskarna
Objednavka ..> Tiskarna : "tiskne na" ' Objednávka používá Tiskárnu

' -- 4.7 Kardinalita (Multiplicity) --
' Umisťuje se na konce vztahů (asociace, agregace, kompozice) v uvozovkách.
' "1"      : Přesně jedna
' "0..1"   : Nula nebo jedna
' "*"      : Nula až mnoho (alternativně "0..*")
' "1..*"   : Jedna až mnoho
' "n"      : Přesně n (kde n je číslo)
' "m..n"   : Od m do n (kde m, n jsou čísla)

' === 5. Poznámky (Notes) ===
' Přidávají dodatečné informace k prvkům diagramu.
' Syntaxe: note left/right/top/bottom of NazevElementu: Text poznámky
'          note "Text plovoucí poznámky" as AliasPoznamky
class Pokladna
note left of Pokladna
  Tato třída zpracovává
  finanční transakce.
  Může být na více řádků.
end note

note "Důležité: Zabezpečit!" as SecNote
Pokladna .. SecNote ' Propojení plovoucí poznámky

' === 6. Seskupování (Packages) ===
' Pro organizaci tříd do logických celků.
package "ModelyDat" {
  class Produkt
  class Objednavka
  class Uzivatel
}
package "ServisniVrstva" {
  class ProduktovyServis {
    +najdiProdukt(id: int): Produkt
  }
  ProduktovyServis ..> Produkt : "používá"
}

' === 7. Souhrnný Příklad Diagramu Tříd ===
' package "EvidenceKnih" {
'   abstract class Publikace {
'     #nazev: String
'     #rokVydani: int
'     +getNazev(): String
'     {abstract} +getTypMedia(): String
'   }
'
'   class Kniha extends Publikace {
'     -autor: String
'     -pocetStran: int
'     +getAutor(): String
'     +getTypMedia(): String
'   }
'
'   class Casopis extends Publikace {
'     -cisloVydani: int
'     +getTypMedia(): String
'   }
'
'   interface Vypujcitelny {
'     +vypujcSi(uzivatel: Uzivatel): boolean
'     +vratit(uzivatel: Uzivatel): void
'   }
'
'   Kniha <|.. Vypujcitelny
'   Casopis <|.. Vypujcitelny
'
'   class Uzivatel {
'     -jmeno: String
'     -idUzivatele: String
'   }
'
'   Uzivatel "1" -- "0..*" Kniha : "vypůjčuje si >"
'   Uzivatel "1" -- "0..*" Casopis : "odebírá >"
'
'   class Knihovna {
'     -seznamPublikaci: Publikace[*]
'     +pridejPublikaci(p: Publikace)
'   }
'   Knihovna "1" o-- "*" Publikace : "obsahuje"
' }


' === Tipy pro AI Agenta při generování Diagramů Tříd ===
' 1. Buď explicitní:
'    - Názvy tříd, rozhraní, výčtů.
'    - Stereotypy (abstract, interface, enum), pokud jsou relevantní.
'    - Atributy: Viditelnost, název, typ, případně výchozí hodnota a modifikátory ({static}, {readonly}).
'    - Metody: Viditelnost, název, parametry (s názvy a typy), návratový typ a modifikátory ({abstract}, {static}).
'    - Vztahy: Přesný typ (dědičnost, implementace, asociace, agregace, kompozice, závislost).
'    - U asociací, agregací a kompozicí uveď názvy rolí (pokud jsou známy) a kardinalitu na obou koncích.
' 2. Používej aliasy ('as'): Pro složitější názvy nebo pro zkrácení, aby byl kód přehlednější.
' 3. Seskupování ('package'): Pro větší diagramy použij balíčky k logickému členění.
' 4. Iteruj: Začni jednodušší verzí a postupně přidávej detaily na základě zpětné vazby.
' 5. Komentáře v PlantUML: Používej apostrof (') pro komentáře v PlantUML kódu pro vysvětlení specifických částí diagramu nebo rozhodnutí.

@enduml