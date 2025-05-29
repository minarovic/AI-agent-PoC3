@startuml
' Příručka pro AI Agenta: Tvorba Diagramu Aktivit v PlantUML (Nová syntaxe)

' --- Myšlenkový pochod (Chain of Thought) pro tvorbu této příručky ---
' 1. Cíl: Vytvořit stručnou a jasnou příručku pro AI agenta, zaměřenou na novou syntaxi diagramů aktivit.
' 2. Klíčové prvky diagramu aktivit (nová syntaxe): Start/Stop/End, Akce, Spojnice (tok), Podmínky (if/then/else/elseif), Smyčky (while, repeat), Paralelní zpracování (fork), Oddíly (partition), Plavecké dráhy (swimlanes), Poznámky.
' 3. Struktura příručky: Úvod -> Základní syntaxe -> Jednotlivé prvky s příklady -> Jednoduchý souhrnný příklad -> Tipy pro AI.
' 4. Jazyk: Čeština, srozumitelné pro AI.
' 5. Formát: PlantUML komentáře a jednoduché diagramy jako ilustrace. Použít novou syntaxi.
' --- Konec myšlenkového pochodu ---

' === Úvod ===
' Diagram aktivit vizualizuje posloupnost akcí a tok řízení v procesu nebo algoritmu pomocí nové, flexibilnější syntaxe PlantUML.
' Pro AI agenta je užitečný k:
'   - Pochopení a generování krok-za-krokem logiky.
'   - Znázornění rozhodovacích bodů a alternativních cest.
'   - Komunikaci komplexních procesů člověku.

' === 1. Základní Syntaxe ===
' Každý PlantUML diagram začíná @startuml a končí @enduml.
' Pro diagram aktivit se používají klíčová slova 'start' a 'stop' (nebo 'end').

start
note right: Diagram začíná klíčovým slovem 'start'.

' === 2. Aktivity (Akce) ===
' Aktivity se definují pomocí dvojtečky na začátku a středníku na konci.
' Mohou být na více řádků a obsahovat Creole formátování.
:První akce;
:Druhá akce\nna více řádků;
note left
  Toto je jednoduchá akce.
  Může obsahovat **formátování** //Creole//.
end note
#LightGreen:Akce s barvou pozadí; ' Barvu lze nastavit přímo

' === 3. Spojnice (Tok) ===
' Aktivity jsou implicitně propojeny v pořadí definice.
' Explicitní spojnice se značí šipkou '->'.
' Popisky na spojnicích se dávají za šipku (bez závorek, pokud nejde o podmínku).
-> Popisek toku;
:Třetí akce;
-[#blue,dashed]-> Modrá přerušovaná šipka; ' Styl a barva šipky
:Čtvrtá akce;

' === 4. Podmíněná Logika (Větvení) ===
' Používají se klíčová slova 'if', 'then', 'else', 'elseif', 'endif'.
' Podmínka a popisky větví se píší do kulatých závorek.

if (Je podmínka splněna?) then (Ano)
  #PaleGreen:Akce pro Ano větev;
else (Ne)
  #LightCoral:Akce pro Ne větev;
  if (Jiná podmínka?) then (Ano)
    :Akce pro vnořené Ano;
  else (Ne)
    :Akce pro vnořené Ne;
  endif
endif
note right of if
  Podmínky umožňují větvení toku.
  Popisky větví (Ano/Ne) jsou důležité
  pro srozumitelnost.
end note
:Pokračování po if; ' Spojení větví je automatické

' === 5. Smyčky ===
' -- 5.1. Smyčka While --
' Používá 'while' a 'endwhile'. Podmínka a popisky jsou v ().
while (Je třeba opakovat?) is (Ano)
  :Akce ve smyčce while;
endwhile (Ne)
:Pokračování po while;

' -- 5.2. Smyčka Repeat --
' Používá 'repeat' a 'repeat while'.
repeat
  :Akce ve smyčce repeat;
repeat while (Testovací podmínka pro repeat) is (Pokračovat) not (Ukončit)
note on link
  Popisek 'is' pro pokračování,
  'not' pro ukončení smyčky.
end note
:Pokračování po repeat;

' === 6. Paralelní Zpracování ===
' Používá se 'fork', 'fork again', 'end fork' (nebo 'end merge').
fork
  :Paralelní větev 1 - Akce A;
  :Paralelní větev 1 - Akce B;
fork again
  :Paralelní větev 2 - Akce C;
end fork
note left: 'fork again' odděluje paralelní větve. 'end fork' je spojí.
:Pokračování po fork;

' === 7. Oddíly (Partitions) a Plavecké Dráhy (Swimlanes) ===
' -- 7.1 Oddíly (Partitions) --
' Pro vizuální seskupení aktivit.
partition "Fáze Zpracování" #LightBlue {
  :Akce 1 ve fázi;
  :Akce 2 ve fázi;
}

' -- 7.2 Plavecké Dráhy (Swimlanes) --
' Pro znázornění zodpovědnosti (kdo co dělá).
|Uživatel|
  :Akce uživatele;
|#Technology|Systém|
  :Akce systému;
|Uživatel|
  :Další akce uživatele;

' === 8. Poznámky ===
' Kód již obsahuje několik příkladů poznámek.
' note left/right/top/bottom: Text poznámky; (k poslední aktivitě)
' note left/right/top/bottom of [element]: Text poznámky; (k specifickému prvku, pokud má element definovaný alias nebo je to např. 'if')
' note on link \n Text \n end note (k poslední spojnici)
' floating note: Plovoucí poznámka;

' === 9. Ukončení toku (Kill / Detach) ===
' Pro explicitní ukončení větve toku.
if (Nastala kritická chyba?) then (Ano)
  :Zaloguj chybu;
  kill ' Ukončí celý diagram
  ' detach ' Ukončí pouze tuto větev
else (Ne)
  :Pokračuj normálně;
endif

' === 10. Jednoduchý Souhrnný Příklad ===
' start
' :Přijmout požadavek;
' if (Validovat požadavek?) then (Platný)
'   fork
'     :Aktualizovat databázi;
'   fork again
'     :Odeslat notifikaci;
'   end fork
'   :Odpovědět klientovi: OK;
' else (Neplatný)
'   :Odpovědět klientovi: Chyba;
'   note right: Požadavek zamítnut.
' endif
' stop

' === Tipy pro AI Agenta při generování Diagramu Aktivit ===
' 1. Požádej o dekompozici: Pokud je proces složitý, požádej o jeho rozdělení na menší, lépe popsatelné kroky.
' 2. Jasné popisky: Používej výstižné popisky pro aktivity, podmínky a spojnice.
' 3. Důraz na větve: U podmínek vždy specifikuj, co se děje v 'Ano' (then) a 'Ne' (else) větvi pomocí popisků v ().
' 4. Smyčky: Jasně definuj vstupní/výstupní podmínku smyčky a popisky větví (is/not).
' 5. Paralelizace: Použij 'fork', pokud akce mohou běžet souběžně.
' 6. Zodpovědnost: Pokud je důležité, kdo co dělá, použij plavecké dráhy (|Swimlane|).
' 7. Komentáře v PlantUML: Používej apostrof (') pro jednořádkové komentáře v PlantUML kódu pro vysvětlení logiky diagramu.
'    ' Toto je příklad komentáře v PlantUML
' 8. Iterace: Buď připraven generovat diagram iterativně na základě zpětné vazby.

stop
note left: Diagram končí klíčovým slovem 'stop' nebo 'end'.
@enduml