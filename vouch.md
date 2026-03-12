# 🚀 Vouch – The "Stripe for App-Security"

## 1. Executive Summary & Vision
**Das Ziel:** Vouch wird die unsichtbare, vollautomatische Sicherheitsinfrastruktur für das Indie-Developer-, Solo-Founder- und Creator-Segment. So wie Stripe Payments demokratisiert hat und Supabase Datenbanken vereinfacht, macht Vouch App-Security zu einem Plug-and-Play-Erlebnis.

Wir bauen keine komplexen Dashboards für Enterprise-CISO-Teams. Wir bauen eine Developer Experience (DX), die für "Vibe-Coder" (Entwickler, die massiv auf KI-Codegenerierung setzen) in 5 Minuten integrierbar ist, klare Handlungsanweisungen liefert und die gefährlichsten Fehler ("Vibe-Fails") automatisch abfängt.

## 2. Das Problem (Market Need)
* **Die Vibe-Coding-Falle:** Schnelles, AI-getriebenes Entwickeln maximiert den Output, überspringt aber klassische Security-Checks (Secure by Design). KI-Modelle generieren häufig unsicheren Code (fehlende Auth, SQLi, offene CORS, Hardcoded Secrets).
* **Der Markt-Gap:** Der Markt für Application-Security wächst, aber bestehende Tools (wie Snyk, SonarQube) sind teuer, komplex in der CI/CD-Pipeline zu konfigurieren und produzieren eine Flut an Warnungen (Alert Fatigue), die Solo-Devs ignorieren.

> **Wissenschaftliche Einordnung: Automated Security Governance**
> Im Kontext der modernen Wirtschaftsinformatik adressiert dieses Produkt die *Information Asymmetry* zwischen schnellen Code-Generatoren (LLMs) und formaler Softwaresicherheit. Es implementiert *Static Application Security Testing (SAST)* nicht als reines Analysewerkzeug, sondern als kuratierte, heuristische Filter-Schicht, die technische Schulden (Technical Debt) im Bereich Security durch automatisierte "Opinionated Defaults" in Echtzeit reduziert.

## 3. Positionierung: Vouch vs. Klassische Tools

| Metrik | Vouch (Unser Produkt) | Klassische Enterprise Tools |
| :--- | :--- | :--- |
| **Zielgruppe** | Vibe-Coder, Indie Hacker, Solo-Founder | Security-Teams, Enterprise DevOps |
| **Integration** | 5-Minuten Copy-Paste (API-Key, SDK oder GitHub App) | Komplexe CI/CD Integration, Docker-Setup |
| **Output** | Security-Score (0-100) + 3 konkrete To-Dos mit Code-Fixes | Endlose CVE-Listen, abstrakte Vulnerability Reports |
| **Fokus** | Häufigste 20% der Vibe-Fails (Auth, Injection, Secrets) | 100% Compliance, Audit-Readiness |
| **Pricing** | Freemium + günstiges Flat-Pricing pro Projekt | Komplexe Enterprise-Verträge (Sitzplatzlizenzen) |

## 4. Produkt-Architektur (The 3 Pillars)

### A. API / SaaS-Service (Das Herzstück)
* REST/GraphQL-API, die Code-Snippets, OpenAPI-Schemas oder Repositories entgegennimmt.
* **Engine:** Leichtgewichtiger SAST/SCA-Ansatz, kuratiert auf Vibe-Fails.
* **Output:** Liefert einen verständlichen Security-Score, konkrete Findings und vor allem *Copy-Paste-fertige Fix-Vorschläge*.
* **Integration:** GitHub Actions, direkte AI-Coding-Tool-Plugins (VS Code/Cursor/Antigravity Extension).

### B. Das "Security Widget" / SDK (Runtime Protection)
* Ein minimales Client/Server-SDK, das als Proxy vor der API oder der Datenbank sitzt.
* Erkennt typische Misskonfigurationen zur Laufzeit (z. B. Rate-Limits fehlen, unsicheres Storage-Handling).
* **Opinionated Defaults:** Liefert "Secure-by-default"-Templates für gängige Stacks (Next.js + Supabase + Stripe).

### C. No-Code Dashboard
* Web-UI: App-URL oder GitHub-Link einwerfen -> "Scan" klicken.
* Ausgabe: Ampelsystem (Score 0-100), Top-Risiken in einfacher Sprache.
* Optional: "One-Click-Fix" (z.B. automatisches Härten von HTTP-Headern).

## 5. Das MVP (Minimum Viable Product) – Aktueller Fokus
Wir bauen nicht alles auf einmal. Das MVP ist extrem spitz und fokussiert sich auf den "Developer Flow":

1. **GitHub-App:** Scannt Repos (Fokus JS/TS/Python) mit einem minimalen, aber tödlich präzisen Regelsatz.
2. **AI-Translation Layer:** Die rohen Scanner-Daten (JSON) werden durch ein LLM in einfache, menschliche Sprache und konkrete Code-Fixes übersetzt.
3. **User-Feedback:** Der Output erfolgt direkt als GitHub-Kommentar bei jedem Push + Generierung eines "Security Score Badges" für die README.md.
4. **Das Dashboard:** Eine rudumentäre Web-Oberfläche, die diesen Score und die 3 wichtigsten To-Dos visualisiert.

## 6. AI System Directives (Für den Code-Assistenten)
*Wenn du (die KI) in diesem Projekt Code generierst, halte dich an folgende Regeln:*
* **Simplicity First:** Baue keine komplexen Enterprise-Pattern, wenn eine simple API-Route reicht.
* **DX Focus:** Fehlermeldungen der API müssen für Anfänger verständlich sein.
* **Modularität:** Trenne die Scanner-Engine (Semgrep etc.) sauber von der API-Logik, damit wir später leicht andere Scanner anbinden können.
