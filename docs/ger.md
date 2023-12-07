# Fahrdaten-Manager

Fahrdaten-Manager ist ein auf Python basierendes Tool zum Importieren und Verarbeiten von Fahrzeugfahrtdaten, die im CSV-Format gespeichert sind. Es verwaltet diese Daten in einer SQLite-Datenbank und exportiert sie in eine XLSX-Datei für weitere Analysen.

## Funktionen

- Daten aus CSV-Dateien laden.
- Erstellen und Aktualisieren von SQLite-Tabellen für jedes Fahrzeug.
- Überprüfen auf vorhandene Einträge und ggf. Aktualisieren der Datensätze.
- Exportieren von Daten in das XLSX-Format, mit individuellen Blättern pro Fahrzeug.

## Voraussetzungen

- Python 3.10.0
- pandas
- sqlite3
- PyInquirer
- re (Modul für reguläre Ausdrücke)

## Installation

1. Stellen Sie sicher, dass Python 3.10.0 auf Ihrem System installiert ist.
2. Klonen Sie das Repository oder laden Sie den Quellcode herunter.
3. Navigieren Sie zum Projektverzeichnis.

## Einrichten einer virtuellen Umgebung

Es wird empfohlen, eine virtuelle Umgebung einzurichten, um Konflikte mit anderen Paketen und Versionen zu vermeiden. Um eine virtuelle Umgebung einzurichten und zu aktivieren:

Für **Unix/macOS**-Systeme:

```sh
python3 -m venv venv
source venv/bin/activate
```

Für **Windows**-Systeme:

```bat
python -m venv venv
.\venv\Scripts\activate
```

Nachdem die virtuelle Umgebung aktiviert ist, installieren Sie die erforderlichen Pakete:

```sh
pip install -r requirements.txt
```

## Nutzung

Um das Programm auszuführen, verwenden Sie das bereitgestellte Shell-Skript für Unix/macOS oder die Batch-Datei für Windows:

Für **Unix/macOS**:

```sh
./run.sh
```

Für **Windows**:

```bat
.\run.bat
```

## Nutzung mit GUI

Fahrdaten-Manager verfügt über eine grafische Benutzeroberfläche (GUI) für eine einfache Bedienung. Um mit dem Programm zu interagieren, folgen Sie diesen Schritten:

1. Starten Sie das Programm, indem Sie das `run.sh` oder `run.bat` Skript ausführen, abhängig von Ihrem Betriebssystem.
2. Verwenden Sie die GUI, um:
   - Wählen Sie Ihre CSV-Datei aus, indem Sie auf den "CSV"-Knopf klicken.
   - Wählen Sie Ihre Datenbankdatei aus, indem Sie auf den "Datenbank"-Knopf klicken.
   - Nach der Auswahl wird Ihnen die Möglichkeit gegeben, eine XLSX-Datei auszuwählen.
   - Wenn eine neue Datenbankdatei erstellt wird, wird automatisch eine XLSX-Datei mit dem gleichen Namen erstellt.

Sobald die Dateien ausgewählt sind, zeigt das Programm die Pfade zu den gewählten Dateien in der Oberfläche an.

3. Klicken Sie auf den "Verarbeitung"-Knopf, um mit der Datenverarbeitung zu beginnen. Die GUI gibt Rückmeldung über den Fortschritt der Operationen.

![Beispiel_gui](/data/Example.gif)

Nach der Verarbeitung wird die SQLite-Datenbank aktualisiert und eine XLSX-Datei wird am angegebenen Ort mit den verarbeiteten Daten erstellt.

## Funktionsweise

Das Skript führt mehrere Schlüsselfunktionen aus:
- Stellt eine Verbindung zu einer SQLite-Datenbank her.
- Erstellt Tabellen für jeden einzigartigen Fahrzeugnamen, der in den CSV-Daten gefunden wird.
- Füllt diese Tabellen mit den Fahrtendaten und stellt sicher, dass die neuesten Fahrtendzeiten erfasst werden.
- Generiert eine XLSX-Datei mit einem Blatt für jedes Fahrzeug, das die Fahrtendaten enthält.

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert - siehe die Datei LICENSE.md für Details.