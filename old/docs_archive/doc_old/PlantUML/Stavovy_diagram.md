@startuml
' Příručka pro AI Agenta: Tvorba Stavových Diagramů v PlantUML

' --- Myšlenkový pochod (Chain of Thought) pro tvorbu této příručky ---
' 1. Cíl: Vytvořit stručnou a jasnou příručku pro AI agenta specificky pro Stavové Diagramy.
' 2. Klíčové prvky Stavového Diagramu:
'    - Stavy (jednoduché, složené/kompozitní).
'    - Přechody (Transitions) mezi stavy, včetně popisků (události, podmínky, akce).
'    - Počáteční a koncové stavy ([*]).
'    - Vnitřní aktivity/popisy stavů.
'    - Složené stavy a vnořené diagramy.
'    - Souběžné oblasti (Concurrent regions) pomocí -- nebo ||.
'    - Historie (History states) [H], [H*].
'    - Rozvětvení a spojení (Fork/Join) <<fork>>, <<join>>.
'    - Rozhodovací pseudostavy (Choice) <<choice>>.
'    - Vstupní/výstupní body (Entry/Exit points) <<entryPoint>>, <<exitPoint>>.
'    - Poznámky.
' 3. Struktura příručky: Úvod -> Základní syntaxe -> Stavy -> Přechody -> Speciální stavy a pseudostavy -> Složené stavy a souběžnost -> Poznámky -> Jednoduchý souhrnný příklad -> Tipy pro AI.
' 4. Jazyk: Čeština, srozumitelné pro AI.
' 5. Formát: PlantUML komentáře a jednoduché diagramy jako ilustrace.
' --- Konec myšlenkového pochodu ---

' === Úvod ===
' Stavový Diagram (State Machine Diagram) modeluje chování jednoho objektu nebo systému během jeho životního cyklu.
' Ukazuje stavy, ve kterých se objekt může nacházet, a přechody mezi těmito stavy vyvolané událostmi.
' Pro AI agenta je užitečný k:
'   - Pochopení a generování logiky řízené událostmi.
'   - Modelování životního cyklu objektů nebo komponent.
'   - Vizualizaci komplexního chování a reakcí na různé podněty.

' === 1. Základní Syntaxe ===
' Každý PlantUML diagram začíná @startuml a končí @enduml.
' Počáteční a koncový stav se značí [*].

' === 2. Stavy (States) ===
' Stavy se definují klíčovým slovem 'state' nebo implicitně jejich názvem.
' Názvy v uvozovkách pro víceslovné názvy.
' Aliasy se definují pomocí 'as'.

state StavA
state "Dlouhý Název Stavu" as DlouhyStav
state StavB #LightBlue ' Lze přiřadit barvu

note right of StavA
  Stav reprezentuje situaci,
  ve které se objekt/systém
  může nacházet.
end note

' -- Popis/Aktivity uvnitř stavu --
' Aktivity (entry/, exit/, do/) nebo popis se přidávají pomocí dvojtečky za názvem stavu.
StavA : entry / Inicializuj()
StavA : exit / UložStav()
StavA : do / ZpracovávejData()
StavA : Tento stav čeká na událost.

state StavC {
  StavC : Popis uvnitř složeného stavu.
  ' Vnitřní aktivity lze definovat i zde.
}


' === 3. Přechody (Transitions) ===
' Přechody mezi stavy se značí šipkou '-->'.
' Lze specifikovat směr (-up->, -left->, -right->, -down->).
StavA --> StavB
StavB -up-> StavC

' -- Popisky přechodů --
' Popisek (událost [podmínka] / akce) se přidává za dvojtečku za definicí šipky.
StavA --> DlouhyStav : UdálostX [PodmínkaY] / AkceZ()
StavB --> StavA : Timeout / Resetuj()

note on link
  Popisek typicky obsahuje:
  Událost (trigger)
  [Ochranná podmínka (guard)]
  / Akce (action)
end note

' === 4. Počáteční a Koncové Stavy ===
' Používá se [*]. Šipka z [*] značí start, šipka do [*] značí konec.
[*] --> StavA ' Počáteční přechod
StavC --> [*] ' Koncový přechod

' === 5. Speciální Stavy a Pseudostavy ===
' -- 5.1 Historie (History) --
' Pamatuje si poslední aktivní podstav složeného stavu.
' [H] : Povrchní historie (pamatuje si jen přímý podstav)
' [H*]: Hluboká historie (pamatuje si vnořený stav na jakékoli úrovni)
state SlozenyStav {
  state Podstav1
  state Podstav2
  [*] --> Podstav1
  Podstav1 --> Podstav2 : event1
  Podstav2 --> Podstav1 : event2
}
SlozenyStav --> [*] : Konec
[*] --> SlozenyStav.[H] : Obnovit ' Vrátí se do Podstav1 nebo Podstav2

' -- 5.2 Rozvětvení/Spojení (Fork/Join) --
' Pro modelování souběžných cest. Používají se stereotypy <<fork>> a <<join>>.
state rozvetveni <<fork>>
state spojeni <<join>>
[*] --> rozvetveni
rozvetveni --> StavParalelniA
rozvetveni --> StavParalelniB
StavParalelniA --> spojeni
StavParalelniB --> spojeni
spojeni --> [*]

' -- 5.3 Rozhodování (Choice) --
' Umožňuje dynamické větvení na základě podmínek. Používá se stereotyp <<choice>>.
state rozhodnuti <<choice>>
StavA --> rozhodnuti : ZkontrolujData
rozhodnuti --> StavB : [DataOK]
rozhodnuti --> StavC : [DataError] / ZalogujChybu()

' -- 5.4 Vstupní/Výstupní Body (Entry/Exit Points) --
' Umožňují definovat specifické body vstupu/výstupu do/ze složeného stavu.
' Používají se stereotypy <<entryPoint>> a <<exitPoint>>.
state SlozenySVstupy {
  state vstup1 <<entryPoint>>
  state vystupA <<exitPoint>>
  state VnitrniStav
  vstup1 --> VnitrniStav
  VnitrniStav --> vystupA
}
[*] -> vstup1
vystupA -> [*]

' === 6. Složené Stavy (Composite States) a Souběžnost (Concurrency) ===
' Stavy mohou obsahovat vnořené stavové diagramy.
state Aktivni {
  state Ceka
  state Zpracovava
  [*] --> Ceka
  Ceka --> Zpracovava : PrijataData
  Zpracovava --> Ceka : Hotovo
  Zpracovava --> Zpracovava : DalsiKrok

  ' -- Souběžné oblasti (Concurrent Regions) --
  ' Oddělují se pomocí '--' (horizontálně) nebo '||' (vertikálně).
  -- ' Horizontální oddělovač
  state LedSviti
  state LedNesviti
  [*] --> LedNesviti
  LedNesviti --> LedSviti : ZapniLed
  LedSviti --> LedNesviti : VypniLed
}
StavC --> Aktivni
Aktivni --> [*]

' === 7. Poznámky (Notes) ===
' Přidávají dodatečné informace k prvkům diagramu.
' Syntaxe: note left/right/top/bottom of NazevElementu: Text poznámky
'          note "Text plovoucí poznámky" as AliasPoznamky
note bottom of Aktivni
  Tento složený stav reprezentuje
  hlavní aktivní fázi systému.
end note

' === 8. Jednoduchý Souhrnný Příklad ===
' @startuml
' title Stavový diagram automatu na kávu
'
' [*] --> CekaNaMince : Start
' state CekaNaMince {
'   CekaNaMince : Vložte mince (cena: 20 Kč)
' }
' CekaNaMince --> CekaNaVolbu : VlozenaMince(hodnota) / suma += hodnota
'
' state CekaNaVolbu <<choice>>
' CekaNaMince --> CekaNaVolbu : [suma >= 20]
'
' CekaNaVolbu --> PripravaKavy : ZvolenaKava [suma >= 20] / vratPreplatek(suma-20)
' CekaNaVolbu --> PripravaCaje : ZvolenCaj [suma >= 20] / vratPreplatek(suma-20)
' CekaNaVolbu --> CekaNaMince : Zrusit / vratMince(suma)
'
' state PripravaKavy : Probíhá příprava kávy...
' state PripravaCaje : Probíhá příprava čaje...
'
' PripravaKavy --> VydajNapoj : KavaHotova
' PripravaCaje --> VydajNapoj : CajHotov
'
' state VydajNapoj : Odeberte si nápoj.
' VydajNapoj --> [*] : NapojOdebran
'
' note "Suma mincí je interní proměnná" as N1
' @enduml

' === Tipy pro AI Agenta při generování Stavových Diagramů ===
' 1. Identifikuj stavy: V jakých různých situacích se může objekt/systém nacházet?
' 2. Definuj přechody: Jaké události (triggery) způsobují změnu stavu?
' 3. Podmínky a akce: Existují podmínky (guards), které musí být splněny pro přechod? Jaké akce se provedou během přechodu?
' 4. Start a konec: Nezapomeň na počáteční ([*] -->) a případně koncové (--> [*]) stavy.
' 5. Složené stavy: Pokud je stav komplexní, rozlož ho na podstavy. Použij 'state Nazev {...}'.
' 6. Souběžnost: Pokud části systému fungují nezávisle a paralelně, použij souběžné oblasti (-- nebo ||).
' 7. Pseudostavy: Použij <<choice>>, <<fork>>, <<join>>, [H], [H*] pro modelování složitějšího chování.
' 8. Komentáře v PlantUML: Používej apostrof (') pro komentáře v PlantUML kódu.

@enduml