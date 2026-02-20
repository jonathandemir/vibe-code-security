import re
import sys
import os

def scan_file(file_path):
    """
    Liest eine Datei ein und prüft sie auf harte API-Keys und Passwörter.
    """
    # Überprüfen, ob die Datei existiert
    if not os.path.exists(file_path):
        print(f"Fehler: Die Datei '{file_path}' wurde nicht gefunden.")
        sys.exit(1)

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except Exception as e:
        print(f"Fehler beim Lesen der Datei: {e}")
        sys.exit(1)

    # Regex für OpenAI-ähnliche API-Keys (sk- gefolgt von mindestens 20 alphanumerischen Zeichen)
    api_key_pattern = r'sk-[a-zA-Z0-9]{20,}'
    
    # Suche nach dem Muster 'password ='
    # Wir nutzen Regex, um auch Leerzeichen-Variationen abzufangen (z.B. password=)
    password_pattern = r'password\s*='

    found_security_issues = False

    # Suche nach API-Keys
    if re.search(api_key_pattern, content):
        print("WARNUNG: Ein potenzieller API-Key wurde im Code gefunden!")
        found_security_issues = True

    # Suche nach 'password ='
    if re.search(password_pattern, content):
        print("WARNUNG: Hardcodiertes Passwort ('password =') wurde im Code gefunden!")
        found_security_issues = True

    # Abschlussprüfung
    if found_security_issues:
        sys.exit(1)
    else:
        print("Alles sicher")
        sys.exit(0)

if __name__ == "__main__":
    # In diesem Fall scannen wir fest die 'dummy_app.py' wie angefordert
    target_file = "dummy_app.py"
    scan_file(target_file)
