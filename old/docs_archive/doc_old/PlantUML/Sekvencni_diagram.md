@startuml
' Příručka pro AI Agenta: Tvorba Sekvenčních Diagramů v PlantUML

' --- Myšlenkový pochod (Chain of Thought) pro tvorbu této příručky ---
' 1. Cíl: Vytvořit stručnou a jasnou příručku pro AI agenta specificky pro Sekvenční Diagramy.
' 2. Klíčové prvky Sekvenčního Diagramu:
'    - Účastníci (Participants, Actors, Boundary, Control, Entity, Database, Collections, Queue).
'    - Zprávy (synchronní, asynchronní, návratové, ztracené, vlastní).
'    - Životní čáry (Lifelines) a pruhy aktivace (Activation bars).
'    - Kombinované fragmenty (alt, opt, loop, group, break, critical, par).
'    - Vytváření a ničení účastníků (create, destroy).
'    - Poznámky (Notes).
'    - Odkazy (References - ref).
'    - Děliče (Dividers).
'    - Zpoždění (Delay).
' 3. Struktura příručky: Úvod -> Základní syntaxe -> Účastníci -> Zprávy -> Aktivace -> Kombinované fragmenty -> Další prvky -> Jednoduchý souhrnný příklad -> Tipy pro AI.
' 4. Jazyk: Čeština, srozumitelné pro AI.
' 5. Formát: PlantUML komentáře a jednoduché diagramy jako ilustrace.
' --- Konec myšlenkového pochodu ---

' === Úvod ===
' Sekvenční Diagram (Sequence Diagram) zobrazuje interakce mezi objekty (účastníky) v časovém sledu.
' Ukazuje, jaké zprávy si objekty vyměňují a v jakém pořadí.
' Pro AI agenta je užitečný k:
'   - Pochopení a generování dynamického chování systému.
'   - Vizualizaci toku řízení a výměny dat mezi komponentami.
'   - Detailnímu popisu scénářů interakce.

' === 1. Základní Syntaxe ===
' Každý PlantUML diagram začíná @startuml a končí @enduml.
' Účastníci se obvykle nemusí explicitně deklarovat, vytvoří se automaticky při první zmínce.

' === 2. Účastníci (Participants) ===
' Účastníci reprezentují objekty nebo entity, které si vyměňují zprávy.
' Mohou být různého typu (mění jejich vizuální podobu).
' Syntaxe: typ NazevUcastnika ["Alias v uvozovkách"] [jako AliasBezUvozovek] [#barvaPozadi]

participant Uzivatel1
actor "Systém A" as SysA #LightBlue
boundary RozhraníB
control KontrolerC
entity EntitaD
database DatabazeE
collections KolekceF
queue FrontaG

note right of Uzivatel1
  Implicitně vytvořený účastník.
  'participant' je výchozí typ.
end note
note left of SysA
  Explicitně definovaný 'actor'
  s aliasem 'SysA' a barvou pozadí.
end note

' Pořadí účastníků lze ovlivnit pořadím jejich první deklarace nebo pomocí `order`.
' participant Prvni order 10
' participant Druhy order 20

' === 3. Zprávy (Messages) ===
' Zprávy reprezentují komunikaci mezi účastníky.
' -- 3.1 Synchronní zpráva --
' Plná šipka: -> nebo <-
Uzivatel1 -> SysA : Požadavek na data()
SysA --> Uzivatel1 : Odpověď s daty

' -- 3.2 Asynchronní zpráva --
' Otevřená šipka: ->> nebo <<--
Uzivatel1 ->> KontrolerC : Odeslat notifikaci
' Není zde explicitní návratová zpráva pro asynchronní volání

' -- 3.3 Návratová zpráva (Reply Message) --
' Přerušovaná šipka: --> nebo <--
' Často se používá jako odpověď na synchronní zprávu. (viz výše)

' -- 3.4 Zpráva sama sobě (Self Message) --
Uzivatel1 -> Uzivatel1 : Přepočítat interní stav

' -- 3.5 Ztracená zpráva (Lost Message) --
' Šipka končící křížkem: ->x
Uzivatel1 ->x SysA : Zpráva se ztratila

' -- 3.6 Nalezená zpráva (Found Message) --
' Šipka začínající tečkou: .->
' [ -> SysA : Nalezena zpráva (z vnějšku)

' -- 3.7 Popisky zpráv --
' Text za dvojtečkou za definicí šipky. Může být na více řádků pomocí \n.
SysA -> DatabazeE : Uložení dat:\n{id: 123, hodnota: "text"}

' -- 3.8 Číslování zpráv --
' autonumber ' Zapne automatické číslování
' autonumber stop ' Vypne číslování
' autonumber resume ' Obnoví číslování
' autonumber "<b>[000]" ' Formát číslování

' === 4. Životní Čáry a Aktivace (Lifelines and Activation) ===
' Životní čára (svislá čára pod účastníkem) reprezentuje existenci účastníka v čase.
' Aktivace (obdélník na životní čáře) značí období, kdy účastník aktivně zpracovává zprávu.
' Používají se klíčová slova 'activate' a 'deactivate'.
' 'destroy' ukončuje životní čáru účastníka.

Uzivatel1 -> KontrolerC : ZpracujÚkol()
activate KontrolerC #Gold ' Aktivace s barvou
  KontrolerC -> EntitaD : NajdiData()
  activate EntitaD
    EntitaD --> KontrolerC : DataNalezena
  deactivate EntitaD

  KontrolerC --> Uzivatel1 : ÚkolDokončen
deactivate KontrolerC

' Zkrácená syntaxe pro aktivaci/deaktivaci: ++ (aktivuj cíl), -- (deaktivuj zdroj)
' SysA -> SysB ++ : zpráva
' SysB --> SysA -- : odpověď

' === 5. Kombinované Fragmenty (Combined Fragments) ===
' Umožňují modelovat složitější scénáře.
' -- 5.1 Alternativa (alt/else) --
alt Úspěšný případ
  SysA -> Uzivatel1 : Operace úspěšná
else Selhání
  SysA -> Uzivatel1 : Chyba: Operace selhala
  Uzivatel1 -> SysA : Potvrdit chybu
end

' -- 5.2 Volitelná část (opt) --
opt Pokud je podmínka splněna
  KontrolerC -> SysA : Doplňující informace
end

' -- 5.3 Smyčka (loop) --
loop 3 krát ' Nebo "Dokud platí podmínka"
  Uzivatel1 -> SysA : Opakovaný požadavek
  SysA --> Uzivatel1 : Odpověď
end

' -- 5.4 Skupina (group) --
' Pro vizuální seskupení zpráv.
group Validace Vstupu
  Uzivatel1 -> RozhraníB : ValidujData()
  RozhraníB --> Uzivatel1 : DataOK
end

' -- 5.5 Přerušení (break) --
' Pokud je splněna podmínka, zbytek fragmentu se neprovede a sekvence pokračuje za fragmentem.
loop Dokud jsou data
  SysA -> DatabazeE : Načti další data
  alt Data nalezena
    DatabazeE --> SysA : Další data
  else Data nenalezena
    break ' Ukončí smyčku
  end
end
SysA -> SysA : Zpracuj všechna data

' -- 5.6 Kritická sekce (critical) --
' Zprávy uvnitř jsou nedělitelné (atomické).
critical Přístup ke sdílenému zdroji
  EntitaD -> DatabazeE : ZamkniZáznam()
  activate DatabazeE
  EntitaD -> DatabazeE : AktualizujZáznam()
  DatabazeE --> EntitaD : ZáznamAktualizován
  deactivate DatabazeE
end

' -- 5.7 Paralelní zpracování (par) --
' Více sekvencí zpráv probíhá souběžně.
par
  SysA -> KolekceF : Paralelní úkol 1
else
  SysA -> FrontaG : Paralelní úkol 2
end

' === 6. Vytváření a Narušování Účastníků ===
' -- 6.1 Vytvoření (create) --
' Používá se 'create' před první zprávou pro nového účastníka.
Uzivatel1 -> KontrolerC : VytvořNovýObjekt()
activate KontrolerC
  create EntitaD
  KontrolerC -> EntitaD : new()
  activate EntitaD
  EntitaD --> KontrolerC : ObjektVytvořen
  deactivate EntitaD
deactivate KontrolerC

' -- 6.2 Zničení (destroy) --
' Ukončí životní čáru účastníka.
KontrolerC -> EntitaD : UvolniZdroje()
activate EntitaD
  EntitaD --> KontrolerC : ZdrojeUvolněny
  destroy EntitaD ' EntitaD přestává existovat
deactivate KontrolerC

' === 7. Další Užitečné Prvky ===
' -- 7.1 Poznámky (Notes) --
' note left/right of Ucastnik : Text poznámky
' note over Ucastnik1, Ucastnik2 : Text přes více účastníků
' note on link : Text k poslední zprávě
Uzivatel1 -> SysA : Důležitá zpráva
note on link
  Tato zpráva vyžaduje
  okamžitou reakci.
end note

note right of SysA #Yellow
  SysA je momentálně
  pod vysokou zátěží.
end note

' -- 7.2 Odkazy (References - ref) --
' Pro odkazování na jiný (nebo stejný) sekvenční diagram.
ref over Uzivatel1, SysA : Proces Autentizace
' Zde by mohl být detailní diagram autentizace.

' -- 7.3 Děliče (Dividers) --
' Pro vizuální oddělení částí diagramu.
== Inicializační Fáze ==
Uzivatel1 -> SysA : Připojit se
...
== Hlavní Zpracování ==
SysA -> DatabazeE : Načíst data
...

' -- 7.4 Zpoždění (Delay) --
' Pro naznačení plynutí času.
Uzivatel1 -> SysA : Počkej chvíli
...5 minut později...
SysA --> Uzivatel1 : Jsem připraven

' === 8. Jednoduchý Souhrnný Příklad ===
' @startuml
' title Jednoduchý Login Proces
' autonumber "<b>[0]"
'
' actor Uživatel as User
' participant "Login Systém" as LoginSys
' database "Databáze Uživatelů" as UserDB
'
' User -> LoginSys ++ : ZadatPřihlašovacíÚdaje(jméno, heslo)
'   LoginSys -> UserDB ++ : OvěřitUživatele(jméno, hash(heslo))
'     UserDB --> LoginSys -- : VýsledekOvěření(platné)
'   alt Úspěšné přihlášení
'     LoginSys --> User -- : PřihlášeníÚspěšné(token)
'   else Neúspěšné přihlášení
'     LoginSys --> User -- : Chyba: Neplatné údaje
'   end
' @enduml

' === Tipy pro AI Agenta při generování Sekvenčních Diagramů ===
' 1. Identifikuj účastníky: Které objekty, komponenty nebo systémy spolu komunikují?
' 2. Definuj zprávy: Jaké zprávy si vyměňují? Jsou synchronní nebo asynchronní? Jaké mají popisky?
' 3. Sleduj časovou osu: Zprávy by měly být uspořádány shora dolů podle času.
' 4. Používej aktivace: Znázorni, kdy je účastník aktivní (zpracovává zprávu).
' 5. Využívej fragmenty: Pro složitější logiku (podmínky, smyčky) použij `alt`, `opt`, `loop` atd.
' 6. Buď explicitní: Jasně pojmenuj účastníky a zprávy. Používej aliasy pro lepší čitelnost.
' 7. Iteruj: Začni jednoduchým scénářem a postupně přidávej detaily a alternativní toky.
' 8. Komentáře v PlantUML: Používej apostrof (') pro komentáře v PlantUML kódu pro vysvětlení.

@enduml