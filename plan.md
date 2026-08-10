# Verbesserungsplan für den Entnahme-Simulator

## Zielbild

Die Anwendung soll weiterhin ohne Build-Schritt direkt als statische HTML-Datei laufen, aber eine verlässlich getestete Simulationslogik, eine eindeutige Quelle für Änderungen und reproduzierbare Veröffentlichungen erhalten. Die fachlichen Annahmen sollen im UI und in der Berechnung konsistent und nachvollziehbar sein.

## Priorität 0: Aktuelle Synchronisationsabweichung beheben

### Befund

Die drei Anwendungsdateien enthalten nicht denselben Stand:

- `index.html` enthält bereits `isCalculating` mit Ladeanzeige.
- `index.html` verwendet beim Debouncing ein memoisiertes Parameterobjekt.
- `index.html` berücksichtigt `etfTer` in der Sensitivitätsberechnung.
- `index.html` enthält eine korrigierte `ChartBlock`-Zeile ohne überflüssige schließende Klammer.
- `entnahme-simulator.jsx` enthält diese Änderungen nicht.
- `entnahme-simulator.html` und `index.html` sind derzeit inhaltlich gleich.

Damit ist die Aussage in `AGENTS.md`, die Dateien seien identisch, nicht mehr korrekt.

### Geplante Änderung

1. Einen eindeutigen Quellcode festlegen, vorzugsweise `entnahme-simulator.jsx`.
2. Die HTML-Ausgabe künftig aus diesem Quellcode erzeugen oder zumindest einen dokumentierten Synchronisationsschritt einführen.
3. Die derzeit fehlenden Änderungen gezielt abgleichen, ohne unbeabsichtigt funktionierende Änderungen zu überschreiben.
4. Eine automatisierte Prüfung ergänzen, die bei abweichender Simulationslogik zwischen JSX und HTML fehlschlägt.
5. `entnahme-simulator.html` als bewusst benannte alternative Ausgabe behandeln oder entfernen, falls sie nicht benötigt wird.

### Abnahmekriterien

- Die drei Dateien haben entweder eine klar dokumentierte Rolle oder werden automatisch synchron gehalten.
- Ein Vergleich erkennt keine unerwarteten Unterschiede in der Anwendungslogik.
- Die Browser-Anwendung und die JSX-Quelle enthalten dieselbe fachliche Berechnung.

## Priorität 1: Testbare Simulationslogik

### Befund

Die Kernlogik ist in einer großen JSX-Datei enthalten, obwohl wesentliche Funktionen keine React-Abhängigkeit haben. Es gibt aktuell keine Test-, Build- oder Lint-Konfiguration.

### Geplante Änderung

1. Die reinen Funktionen schrittweise in ein separates JavaScript-Modul auslagern:
   - Renditeumrechnung und monatliche Datenaufbereitung
   - Entnahme-Engine
   - Aggregation
   - historische Runner und Monte-Carlo-Runner
   - Renten- und Mietertragsberechnung
2. Einen kleinen Test-Runner ohne Browser-Abhängigkeit ergänzen.
3. Tests für deterministische Hilfsfunktionen schreiben:
   - `percentile()` bei leerem, ein-elementigem und mehr-elementigem Input
   - `wilsonCI()` bei `n = 0` und Grenzwerten
   - `realAssetReturns()`
   - Rentenanpassung und Mietertragsreihe
4. Tests für die Entnahme-Engine schreiben:
   - Entnahme-Reihenfolge in guten und schlechten Marktphasen
   - monatliche und jährliche Frequenz
   - dynamische und statische Strategie
   - harter Boden sowie Ceiling/Floor
   - Renten- und Mieteinnahmen
   - vollständige und erschöpfte Reserven
   - ETF-TER-Abzug
   - Ausfallstatus, Endvermögen und Ausfallkurve
5. Einen reproduzierbaren Smoke-Test für alle vier Simulationsmodi mit festem Seed ergänzen.

### Abnahmekriterien

- Kernfehler können ohne Browser reproduziert werden.
- Änderungen an der Entnahme-Engine werden durch Tests abgesichert.
- Ein fester Seed erzeugt stabile Testergebnisse.

## Priorität 1: Fachliche Konsistenz und Eingabevalidierung

### Befund

Mehrere fachliche Annahmen sind direkt in Konstanten, UI-Texten und Berechnungen verteilt. Besonders auffällig ist die Rentenaltersgrenze: `REGELALTERSGRENZE` ist auf 70 gesetzt, während ein UI-Hinweis weiterhin 67 nennt. Die Anwendung verarbeitet außerdem URL-Parameter direkt über `parseFloat`, ohne erkennbare Wertebereichsvalidierung.

### Geplante Änderung

1. Eine zentrale Konfiguration für fachliche Annahmen einführen.
2. Rentenaltersgrenze, Abschläge und Zuschläge in Berechnung, UI-Hinweisen und Erklärungstexten auf denselben Wert bringen.
3. Festlegen und dokumentieren, ob 70 eine bewusste Modellannahme oder ein Fehler ist.
4. URL-Parameter gegen dieselben Grenzen wie die Slider validieren.
5. Ungültige Kombinationen und negative Restliquidität sichtbar behandeln.
6. Prüfen, wie `maxWindows` und `maxWorldWindows` bei zu langem Horizont reagieren, bevor Runner auf leeren Datenpfaden arbeiten.
7. Die Definition von „Erfolgsquote“ und „Ausfall“ im Code und in der Anleitung exakt angleichen.

### Abnahmekriterien

- Keine widersprüchlichen Altersangaben im UI.
- Geteilte URLs können keine ungültigen oder unkontrollierten Modellparameter aktivieren.
- Unmögliche Datenfenster führen zu einer klaren UI-Meldung statt zu einem fehlerhaften Ergebnis.

## Priorität 2: Datenqualität und Modelltransparenz

### Befund

Die Anwendung enthält historische Daten direkt im Quelltext. Für Gold und Cash werden Jahresrenditen künstlich auf identische Monatsrenditen verteilt. Der Welt-Proxy ist eine feste 65/35-Kombination. Bitcoin wird in allen Modi parametrisch erzeugt. Diese Einschränkungen werden teilweise im UI erklärt, sind aber nicht maschinenlesbar versioniert.

### Geplante Änderung

1. Datenquellen, Abrufdatum, Zeitraum, Einheit und Umrechnung in einer separaten Dokumentation festhalten.
2. Datenvalidierungen ergänzen, etwa erwartete Anzahl und Zeitraum der Monatswerte.
3. Die synthetische monatliche Verteilung klar von echten Monatsdaten unterscheiden.
4. Prüfen, ob Datenaktualisierungen für 2026 und später einen definierten Prozess benötigen.
5. Modellparameter und deren Einheiten zentral zusammenführen.
6. In der Ergebnisansicht Datenbasis, reale/nominale Renditen und synthetische Bestandteile eindeutig anzeigen.
7. Die Einschränkungen des Welt-Proxys und des Bitcoin-Modells in der Nutzerhilfe beibehalten und bei Änderungen aktualisieren.

### Abnahmekriterien

- Ein Agent kann nachvollziehen, welche Werte direkt historisch sind und welche abgeleitet oder simuliert werden.
- Falsche Array-Längen oder fehlende Jahre werden beim Prüfen erkannt.
- Jede angezeigte Modellannahme stammt aus einer zentralen Konfiguration.

## Priorität 2: Performance und Benutzerreaktion

### Befund

Die Simulation und die Sensitivitätsanalyse laufen innerhalb von React-Memos, während große Datenreihen inline geladen werden. Die HTML-Version zeigt bereits einen Ladeindikator für das Debouncing, aber die eigentliche rechenintensive Arbeit läuft weiterhin im Hauptthread.

### Geplante Änderung

1. Simulationen zunächst anhand eines festen Performance-Profils messen.
2. Sensitivitätsanalyse nur bei Bedarf berechnen oder separat auslösen.
3. Prüfen, ob historische und Bootstrap-Daten wiederverwendet werden können, ohne die deterministische Seed-Logik zu verändern.
4. Bei spürbarer Blockierung die Rechenlogik in einen Web Worker verschieben.
5. Ladezustand, Abbruchverhalten und zuletzt gültiges Ergebnis sauber definieren.
6. Rechenzeit für 2.500, 5.000 und 10.000 Pfade vergleichen.

### Abnahmekriterien

- Slider-Eingaben bleiben während der Berechnung bedienbar.
- Ergebnisse zeigen klar, ob sie aktuell oder noch vom vorherigen Parametersatz stammen.
- Reproduzierbarkeit mit identischem Seed bleibt erhalten.

## Priorität 2: Browser- und Bedienbarkeit

### Befund

Die Anwendung nutzt ausschließlich Inline-Stile und einfache HTML-Controls. Tooltips laufen über das `title`-Attribut. Die Teilen-Funktion verwendet die asynchrone Clipboard-API ohne `await` oder `.catch()`, obwohl ein Fehler auftreten kann.

### Geplante Änderung

1. Clipboard-Funktion mit erfolgreichem und fehlgeschlagenem Pfad zuverlässig behandeln.
2. Eine Fallback-Anzeige oder manuelles Kopieren für Browser ohne Clipboard-Berechtigung vorsehen.
3. Buttons, Slider, Tabs und Diagramme auf Tastaturbedienung und sichtbaren Fokus prüfen.
4. Beschriftungen und Statusmeldungen für Screenreader ergänzen.
5. Mobile Darstellung mit langen deutschen Beschriftungen und vier Modus-Tabs testen.
6. Prüfen, ob externe CDN-Abhängigkeiten und Google Fonts bei Offline-Nutzung akzeptabel sind.

### Abnahmekriterien

- Teilen meldet Erfolg nur nach bestätigtem Kopiervorgang.
- Zentrale Eingaben sind per Tastatur erreichbar und verständlich beschriftet.
- Die Anwendung bleibt bei fehlenden optionalen Browser-APIs benutzbar.

## Priorität 3: Wartbarkeit und Veröffentlichungsprozess

### Befund

Die Anwendung ist monolithisch und enthält Daten, Simulation, React-UI und HTML-Ausgabe in sehr großen Dateien. Es gibt keine automatisierten Qualitätsprüfungen und keinen dokumentierten Release-Schritt außer dem manuellen Kopieren beziehungsweise Öffnen der HTML-Datei.

### Geplante Änderung

1. Nach Einführung der Tests die Struktur in Daten, Engine, UI und HTML-Einstiegspunkt aufteilen.
2. Nur dann einen Build-Schritt ergänzen, wenn er die Synchronisation messbar verbessert und die direkte Nutzung nicht unnötig erschwert.
3. Ein kleines Validierungsskript für Syntax, Synchronisation und Datenlängen einführen.
4. Eine CI-Prüfung für Tests und Validierung ergänzen, sobald ein reproduzierbarer lokaler Testlauf existiert.
5. Eine kurze CONTRIBUTING- oder Entwicklungsanleitung für Datenänderungen, Modelländerungen und Browserprüfung ergänzen.
6. Bei jeder Änderung an der Logik einen kurzen manuellen Browser-Smoke-Test durchführen.

### Abnahmekriterien

- Neue Änderungen benötigen keine manuellen Kopien an mehreren Stellen.
- Lokale und CI-Prüfungen sind mit dokumentierten Befehlen reproduzierbar.
- Ein Release-Artefakt lässt sich eindeutig aus dem Quellcode erzeugen.

## Empfohlene Reihenfolge

1. Synchronisationsabweichung zwischen JSX und HTML klären und beheben.
2. Fachliche Inkonsistenzen, insbesondere die Rentenaltersgrenze, entscheiden und korrigieren.
3. Reine Simulationslogik extrahieren und mit deterministischen Tests absichern.
4. URL-Validierung, Datenvalidierung und Grenzfallmeldungen ergänzen.
5. Daten- und Modellannahmen zentral dokumentieren und versionieren.
6. Performance messen und bei Bedarf Web Worker oder gezielte Berechnungsoptimierung einführen.
7. Clipboard, Tastaturbedienung und responsive Darstellung verbessern.
8. Erst danach Build-/CI-Unterstützung und einen stabilen Veröffentlichungsprozess einführen.

## Bewusst nicht im ersten Schritt

- Keine Änderung an Renditeannahmen ohne fachliche Entscheidung und dokumentierte Datenquelle.
- Keine Umstellung auf ein Framework oder eine umfangreiche Toolchain, bevor die Simulationslogik testbar ist.
- Keine automatische Aktualisierung externer Finanzdaten, solange die Anwendung ausdrücklich ohne API- und Datenabhängigkeiten auskommt.
