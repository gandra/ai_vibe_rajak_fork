# MCP (Model Context Protocol) - Session 7 Dokumentacija

> Sveobuhvatni vodič za pokretanje i razumevanje MCP sistema u session7/

---

## Sadržaj

1. [Pregled Fajlova](#1-pregled-fajlova)
2. [Arhitektura Sistema](#2-arhitektura-sistema)
3. [Prerequisiti i Instalacija](#3-prerequisiti-i-instalacija)
4. [Pokretanje MCP Sistema](#4-pokretanje-mcp-sistema)
5. [Detaljni Opis Komponenti](#5-detaljni-opis-komponenti)
6. [Pristupi Pokretanju - Komparacija](#6-pristupi-pokretanju---komparacija)
7. [Flow Dijagrami](#7-flow-dijagrami)
8. [Troubleshooting](#8-troubleshooting)
9. [Sledeći Koraci](#9-sledeći-koraci)

---

## 1. Pregled Fajlova

| Fajl | Tip | Opis | Uloga u sistemu |
|------|-----|------|-----------------|
| `weather-and-air-quality.py` | MCP Server | Pruža dva alata: `get_weather` i `get_air_quality` | Backend - izvor podataka |
| `mcp_cli.py` | MCP Client + Orchestrator | CLI aplikacija sa LLM routing-om | Frontend - korisnički interfejs |
| `index.html` | Dokumentacija | Vizuelne study notes o MCP konceptima | Edukativni materijal |

### Odnos između fajlova

```
┌─────────────────────────────────────────────────────────────────────┐
│                          MCP HOST (tvoj računar)                    │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                     mcp_cli.py (Client + Orchestrator)       │   │
│  │                                                              │   │
│  │   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │   │
│  │   │ Router LLM   │───▶│  Chat LLM    │───▶│ Answer LLM   │  │   │
│  │   │ (temp=0.0)   │    │  (temp=0.4)  │    │  (temp=0.2)  │  │   │
│  │   └──────────────┘    └──────────────┘    └──────────────┘  │   │
│  │           │                                      ▲           │   │
│  │           ▼                                      │           │   │
│  │   ┌─────────────────────────────────────────────┴──────┐    │   │
│  │   │              MCP Client Session                    │    │   │
│  │   │         (stdio_client → ClientSession)             │    │   │
│  │   └────────────────────────┬───────────────────────────┘    │   │
│  └────────────────────────────│────────────────────────────────┘   │
│                               │ stdio (stdin/stdout)               │
│  ┌────────────────────────────▼────────────────────────────────┐   │
│  │              weather-and-air-quality.py (Server)             │   │
│  │                                                              │   │
│  │   ┌──────────────────┐    ┌──────────────────┐              │   │
│  │   │   get_weather    │    │  get_air_quality │              │   │
│  │   │   @mcp.tool()    │    │   @mcp.tool()    │              │   │
│  │   └────────┬─────────┘    └────────┬─────────┘              │   │
│  │            │                       │                         │   │
│  └────────────│───────────────────────│─────────────────────────┘   │
│               │                       │                             │
└───────────────│───────────────────────│─────────────────────────────┘
                │                       │
                ▼                       ▼
        ┌───────────────┐       ┌───────────────┐
        │  Open-Meteo   │       │  Open-Meteo   │
        │  Weather API  │       │ Air Quality   │
        │  (besplatno)  │       │     API       │
        └───────────────┘       └───────────────┘
```

---

## 2. Arhitektura Sistema

### 2.1 MCP Troslojna Arhitektura

```
┌─────────────────────────────────────────────────────────────┐
│                       MCP HOST                              │
│            (računar/VM/container gde sve radi)              │
├─────────────────────────────────────────────────────────────┤
│                       MCP CLIENT                            │
│       (koordinira komunikaciju, govori MCP protokol)        │
├─────────────────────────────────────────────────────────────┤
│                       MCP SERVER                            │
│    (domenski gateway - izlaže alate kroz standard interface)│
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Three-Model Orchestration Pattern

Ovaj sistem koristi **tri specijalizovana LLM-a** umesto jednog:

| Model | Temperature | Uloga | Zašto |
|-------|-------------|-------|-------|
| **Router LLM** | 0.0 | Parsira intent i ekstrahuje parametre | Deterministički, konzistentan output |
| **Chat LLM** | 0.4 | Odgovara na pitanja nevezana za alate | Prirodniji, konverzacijski ton |
| **Answer LLM** | 0.2 | Formatira JSON rezultate u human-readable odgovor | Balans između preciznosti i čitljivosti |

**Zašto tri modela?**
- Router mora biti **100% predvidiv** → `temperature=0`
- Chat treba biti **prirodan** → viša temperatura
- Answer mora biti **tačan ali čitljiv** → srednja temperatura

---

## 3. Prerequisiti i Instalacija

### 3.1 Sistemski zahtevi

| Komponenta | Verzija | Napomena |
|------------|---------|----------|
| Python | ≥3.10, <3.14 | Testirano sa 3.11 |
| Ollama | latest | Lokalni LLM runtime |
| RAM | ≥8GB | Za gemma3:4b model |
| Internet | Da | Za Open-Meteo API pozive |

### 3.2 Python Dependencies

```bash
# Kreiraj virtualno okruženje
cd /workspace/session7
uv init mcp-project
cd mcp-project

# Ili bez uv init (ako koristiš postojeći folder):
uv venv
source .venv/bin/activate  # Linux/macOS
```

**Potrebni paketi:**

```bash
uv add mcp                    # MCP protokol
uv add httpx                  # Async HTTP client
uv add langchain-ollama       # LangChain Ollama integration
uv add langchain-core         # LangChain core (prompts, parsers)
uv add pydantic               # Data validation
```

Ili jednom komandom:
```bash
uv add mcp httpx langchain-ollama langchain-core pydantic
```

### 3.3 Ollama Setup

```bash
# 1. Instaliraj Ollama (ako nemaš)
curl -fsSL https://ollama.com/install.sh | sh

# 2. Pokreni Ollama server
ollama serve

# 3. Preuzmi model (u novom terminalu)
ollama pull gemma3:4b

# Alternativni modeli:
# ollama pull llama3.2:3b      # Manji, brži
# ollama pull mistral:7b       # Veći, kvalitetniji
# ollama pull qwen2.5:7b       # Dobar balans
```

Napomena (macOS: address already in use):

Ako pri `ollama serve` dobiješ:

```
Error: listen tcp 127.0.0.1:11434: bind: address already in use
```

to znači da je Ollama već pokrenut. U tom slučaju:

- Ne pokreći ponovo server — samo koristi postojeći (podrazumevano je na `http://127.0.0.1:11434`).
- Proveri stanje: `ollama ps` ili `curl http://127.0.0.1:11434/api/tags`.
- Ako želiš paralelni server na drugom portu: `OLLAMA_HOST=127.0.0.1:11435 ollama serve` i u klijentu postavi `export OLLAMA_HOST="http://127.0.0.1:11435"`.
- Ako treba da zaustaviš servisni proces: `brew services stop ollama` (ako je pokrenut kao Homebrew servis) ili proveri port `lsof -nP -i :11434`.

---

## 4. Pokretanje MCP Sistema

### 4.1 Brzi Start (Preporučeno)

Napomena: Ako je Ollama već pokrenuta (vidi 3.3), preskoči `ollama serve` i pređi direktno na CLI korak.

```bash
# Terminal 1: Pokreni Ollama
ollama serve

# Terminal 2: Pokreni CLI
cd /workspace/session7
python mcp_cli.py
```

**Očekivani output:**
```
Using OLLAMA_HOST = http://127.0.0.1:11434
Using OLLAMA_MODEL = gemma3:4b

Natural language weather+AQI CLI (Ollama + MCP + LangChain routing)
Type: 'weather in Granada' or 'air quality in Delhi' or 'both in Tokyo'
Type 'quit' to exit.

>
```

### 4.2 Testiranje

```bash
> weather in Belgrade
# Output: Current weather for Belgrade, Serbia...

> air quality in Delhi
# Output: Air quality information for Delhi...

> both in Tokyo
# Output: Weather AND air quality for Tokyo...

> hello
# Output: General chat response (no tools used)

> quit
```

### 4.3 Custom Konfiguracija

```bash
# Promeni Ollama host/model
export OLLAMA_HOST="http://192.168.1.100:11434"
export OLLAMA_MODEL="mistral:7b"
python mcp_cli.py
```

---

## 5. Detaljni Opis Komponenti

### 5.1 MCP Server: `weather-and-air-quality.py`

#### Struktura

```python
from mcp.server.fastmcp import FastMCP

# Kreiranje servera
mcp = FastMCP("weather-and-air-quality")

# Definisanje alata sa @mcp.tool() dekoratorom
@mcp.tool()
async def get_weather(city: str) -> str:
    """Get current weather for a city"""
    # ... implementacija ...

@mcp.tool()
async def get_air_quality(city: str) -> str:
    """Get current air quality for a city"""
    # ... implementacija ...

# Pokretanje servera
if __name__ == "__main__":
    mcp.run()  # Stdio mode
```

#### Dostupni Alati

| Alat | Parametar | Return | Eksterni API |
|------|-----------|--------|--------------|
| `get_weather` | `city: str` | JSON string | Open-Meteo Forecast |
| `get_air_quality` | `city: str` | JSON string | Open-Meteo Air Quality |

#### Weather Response Schema

```json
{
  "tool": "get_weather",
  "source": "open-meteo.com",
  "location": {
    "name": "Belgrade",
    "admin1": "Central Serbia",
    "country": "Serbia",
    "latitude": 44.8125,
    "longitude": 20.4612
  },
  "current": {
    "time": "2024-01-15T14:00",
    "temperature_c": 5.2,
    "apparent_temperature_c": 2.1,
    "wind_speed_kmh": 12.5,
    "weather_code": 3,
    "condition": "Overcast"
  }
}
```

#### Air Quality Response Schema

```json
{
  "tool": "get_air_quality",
  "source": "open-meteo.com (air-quality)",
  "location": { ... },
  "current": {
    "time": "2024-01-15T14:00",
    "us_aqi": 45,
    "us_aqi_category": "Good",
    "pm10_ug_m3": 22.5,
    "pm2_5_ug_m3": 12.3,
    "ozone_ug_m3": 45.0,
    "nitrogen_dioxide_ug_m3": 15.2,
    "sulphur_dioxide_ug_m3": 5.1,
    "carbon_monoxide_ug_m3": 250.0
  }
}
```

#### WMO Weather Codes

Server mapira WMO kodove u human-readable opise:

| Code | Condition | Code | Condition |
|------|-----------|------|-----------|
| 0 | Clear sky | 61 | Slight rain |
| 1 | Mainly clear | 63 | Moderate rain |
| 2 | Partly cloudy | 65 | Heavy rain |
| 3 | Overcast | 71-75 | Snow (slight→heavy) |
| 45 | Fog | 95 | Thunderstorm |

#### US AQI Categories

```
 0-50   → Good
51-100  → Moderate
101-150 → Unhealthy for Sensitive Groups
151-200 → Unhealthy
201-300 → Very Unhealthy
301+    → Hazardous
```

---

### 5.2 MCP Client: `mcp_cli.py`

#### Arhitektura Komponenti

```
┌────────────────────────────────────────────────────────────────┐
│                         mcp_cli.py                             │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    RoutePlan (Pydantic)                 │  │
│  │  - action: weather | air_quality | both | clarify | none│  │
│  │  - city: string                                         │  │
│  │  - question: string (samo za clarify)                   │  │
│  └─────────────────────────────────────────────────────────┘  │
│                              │                                 │
│                              ▼                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              route_chain (LangChain LCEL)               │  │
│  │       route_prompt | router_llm | route_parser          │  │
│  └─────────────────────────────────────────────────────────┘  │
│                              │                                 │
│              ┌───────────────┼───────────────┐                │
│              ▼               ▼               ▼                │
│         ┌────────┐     ┌──────────┐    ┌──────────┐          │
│         │ weather│     │air_quality│   │  both   │           │
│         └───┬────┘     └────┬─────┘    └────┬────┘           │
│             │               │               │                  │
│             └───────────────┼───────────────┘                  │
│                             ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              call_mcp_tool(session, name, args)         │  │
│  │                    ↓ MCP Protocol ↓                     │  │
│  └─────────────────────────────────────────────────────────┘  │
│                             │                                  │
│                             ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    answer_chain                          │  │
│  │           answer_prompt | answer_llm                     │  │
│  │         (konvertuje JSON → natural language)             │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

#### Routing Logic Flow

```
User Input: "What's the weather in Paris?"
                    │
                    ▼
            ┌───────────────┐
            │  Router LLM   │
            │  (temp=0.0)   │
            └───────┬───────┘
                    │
                    ▼
        ┌───────────────────────┐
        │ RoutePlan:            │
        │   action: "weather"   │
        │   city: "Paris"       │
        │   question: ""        │
        └───────────┬───────────┘
                    │
        ┌───────────┴───────────┐
        │   Action Decision     │
        └───────────┬───────────┘
                    │
    ┌───────┬───────┼───────┬───────┐
    ▼       ▼       ▼       ▼       ▼
 weather  air_q   both   clarify  none
    │       │       │       │       │
    │       │       │       │       └──▶ general_answer()
    │       │       │       └──────────▶ print(question)
    │       │       └──────────────────▶ call both tools
    │       └──────────────────────────▶ call get_air_quality
    └──────────────────────────────────▶ call get_weather
                    │
                    ▼
            ┌───────────────┐
            │  Answer LLM   │
            │  (temp=0.2)   │
            └───────┬───────┘
                    │
                    ▼
            Natural Language Response
```

---

## 6. Pristupi Pokretanju - Komparacija

### 6.1 Pristup A: Stdio Mode (Trenutna Implementacija)

**Kako radi:** Client pokreće server kao subprocess, komunikacija preko stdin/stdout.

```python
server = StdioServerParameters(
    command=sys.executable,
    args=["weather-and-air-quality.py"]
)
async with stdio_client(server) as (read, write):
    # ...
```

| Aspekt | Ocena | Objašnjenje |
|--------|-------|-------------|
| Jednostavnost | ★★★★★ | Jedan fajl pokreće sve |
| Development | ★★★★★ | Brza iteracija, nema deploy-a |
| Skalabilnost | ★★☆☆☆ | Jedan client = jedan server proces |
| Production-ready | ★★☆☆☆ | Nije za multi-tenant scenarije |
| Debugging | ★★★★☆ | Lokalno, lako se prati |

**Prednosti:**
- Zero configuration
- Nema network overhead-a
- Server se automatski pokreće/gasi

**Mane:**
- Server živi samo dok client radi
- Nema deljenja servera između više klijenata
- Teško za monitoring u produkciji

---

### 6.2 Pristup B: SSE Mode (Remote Server)

**Kako radi:** Server radi kao samostalan long-running proces, client se konektuje preko HTTP/SSE.

```python
# Server (weather-and-air-quality.py) - modifikovan
mcp.run(transport="sse", host="0.0.0.0", port=8000)

# Client - konektuje se na URL
from mcp.client.sse import sse_client
async with sse_client("http://localhost:8000") as (read, write):
    # ...
```

| Aspekt | Ocena | Objašnjenje |
|--------|-------|-------------|
| Jednostavnost | ★★★☆☆ | Dva procesa, network config |
| Development | ★★★☆☆ | Treba upravljati serverom |
| Skalabilnost | ★★★★★ | Jedan server, mnogo klijenata |
| Production-ready | ★★★★☆ | Load balancing, monitoring |
| Debugging | ★★★☆☆ | Network layer kompleksnost |

**Prednosti:**
- Deljenje servera između klijenata
- Centralizovano upravljanje credentials-ima
- Lakši monitoring i logging
- Horizontalno skaliranje

**Mane:**
- Network latency
- Potreban deployment proces
- Kompleksnija konfiguracija

---

### 6.3 Pristup C: Hybrid (Development + Production)

**Kako radi:** Environment variable određuje mode.

```python
import os

MODE = os.environ.get("MCP_MODE", "stdio")

if MODE == "sse":
    mcp.run(transport="sse", host="0.0.0.0", port=8000)
else:
    mcp.run()  # stdio
```

| Aspekt | Ocena | Objašnjenje |
|--------|-------|-------------|
| Jednostavnost | ★★★★☆ | Jedan codebase, dva moda |
| Development | ★★★★★ | Lokalno = stdio, brzo |
| Skalabilnost | ★★★★★ | Production = SSE |
| Production-ready | ★★★★★ | Fleksibilno |
| Debugging | ★★★★☆ | Best of both worlds |

---

### 6.4 Preporuka

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   ★ PREPORUČENO: Pristup C (Hybrid)                            │
│                                                                 │
│   Razlog: Omogućava brzi development sa stdio modom,           │
│   a production deployment sa SSE modom - bez promene koda.     │
│                                                                 │
│   Za UČENJE i EKSPERIMENTISANJE: Koristi trenutni stdio mode   │
│   (Pristup A) - najjednostavnije za razumevanje koncepta.      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. Flow Dijagrami

### 7.1 Kompletan Request Flow

```
┌──────────┐
│   User   │
│  "weather│
│  in NYC" │
└────┬─────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│                      mcp_cli.py                             │
│                                                             │
│  1. Input parsing                                           │
│     └─▶ user_text = "weather in NYC"                       │
│                                                             │
│  2. plan_tool_call(user_text)                              │
│     └─▶ Router LLM (temp=0.0)                              │
│         └─▶ Returns: {action:"weather", city:"NYC"}        │
│                                                             │
│  3. Action dispatch                                         │
│     └─▶ action == "weather"                                │
│         └─▶ call_mcp_tool(session, "get_weather", {city})  │
│                                                             │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          │ MCP Protocol (stdio)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              weather-and-air-quality.py                     │
│                                                             │
│  4. get_weather("NYC")                                      │
│     ├─▶ geocode_city("NYC")                                │
│     │   └─▶ Open-Meteo Geocoding API                       │
│     │       └─▶ {lat: 40.7128, lon: -74.0060}             │
│     │                                                       │
│     └─▶ fetch_weather(lat, lon)                            │
│         └─▶ Open-Meteo Forecast API                        │
│             └─▶ {temp: 5°C, condition: "Cloudy"}          │
│                                                             │
│  5. Return JSON string                                      │
│                                                             │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          │ JSON response
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      mcp_cli.py                             │
│                                                             │
│  6. answer_with_llm(user_text, weather_data, None)         │
│     └─▶ Answer LLM (temp=0.2)                              │
│         └─▶ "The current weather in New York City is       │
│              5°C with cloudy conditions and wind at        │
│              12 km/h."                                      │
│                                                             │
│  7. print(response)                                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 Error Handling Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Error Scenarios                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  User: "weather in asdfghjkl"                              │
│                       │                                     │
│                       ▼                                     │
│              ┌─────────────────┐                           │
│              │  Router parses  │                           │
│              │  city="asdfghjkl"│                          │
│              └────────┬────────┘                           │
│                       │                                     │
│                       ▼                                     │
│              ┌─────────────────┐                           │
│              │  geocode_city() │                           │
│              │  raises error   │───▶ "Could not find       │
│              └─────────────────┘     location for city"    │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  User: "weather"  (no city)                                │
│                       │                                     │
│                       ▼                                     │
│              ┌─────────────────┐                           │
│              │  Router detects │                           │
│              │  missing city   │───▶ action="clarify"      │
│              └────────┬────────┘     question="Which city?"│
│                       │                                     │
│                       ▼                                     │
│              print("Which city should I use?")             │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Ollama not running                                         │
│                       │                                     │
│                       ▼                                     │
│              ┌─────────────────┐                           │
│              │  Connection     │                           │
│              │  refused        │───▶ "Routing error...     │
│              └─────────────────┘     Try: ollama serve"    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 8. Troubleshooting

### 8.1 Česti Problemi

| Problem | Uzrok | Rešenje |
|---------|-------|---------|
| `Connection refused` | Ollama nije pokrenut | `ollama serve` |
| `Model not found` | Model nije preuzet | `ollama pull gemma3:4b` |
| `Could not find location` | Nepostojeći grad | Proveri spelling grada |
| `Routing error` | LLM timeout/error | Restart Ollama, proveri RAM |
| `ModuleNotFoundError: mcp` | Paketi nisu instalirani | `uv add mcp httpx ...` |

### 8.2 Debug Mode

```python
# Dodaj u mcp_cli.py za debug
import logging
logging.basicConfig(level=logging.DEBUG)

# Ili printuj routing plan
plan = await plan_tool_call(user_text)
print(f"DEBUG: plan = {plan}")  # Vidi šta router vraća
```

### 8.3 Testiranje Servera Samostalno

```bash
# Testiraj da li server radi direktno
cd /workspace/session7
echo '{"method": "tools/list"}' | python weather-and-air-quality.py
```

---

## 9. Sledeći Koraci

### Implementirani Features ✅

| Feature | Status | Lokacija |
|---------|--------|----------|
| MCP Server sa dva alata | ✅ 100% | `weather-and-air-quality.py` |
| Three-model orchestration | ✅ 100% | `mcp_cli.py` |
| Pydantic routing schema | ✅ 100% | `mcp_cli.py:RoutePlan` |
| Geocoding integracija | ✅ 100% | `weather-and-air-quality.py:geocode_city` |
| AQI kategorije | ✅ 100% | `weather-and-air-quality.py:aqi_category_us` |
| WMO weather codes | ✅ 100% | `weather-and-air-quality.py:WMO_WEATHER_CODES` |

### Predloženi Sledeći Koraci

#### Prioritet 1: Proširenje Funkcionalnosti

| Korak | Opis | Kompleksnost | Vrednost |
|-------|------|--------------|----------|
| **Dodaj forecast alat** | 7-dnevna prognoza umesto samo current | Srednja | Visoka |
| **Dodaj alerts alat** | Upozorenja za ekstremne uslove | Srednja | Visoka |
| **Multi-city podrška** | "Compare weather in Paris and London" | Srednja | Srednja |

#### Prioritet 2: Production Readiness

| Korak | Opis | Kompleksnost | Vrednost |
|-------|------|--------------|----------|
| **SSE mode** | Implementiraj remote server opciju | Niska | Visoka |
| **Config file** | `config.yaml` za modele i URL-ove | Niska | Srednja |
| **Logging** | Strukturirani logovi za debugging | Niska | Srednja |
| **Rate limiting** | Zaštita od previše API poziva | Srednja | Srednja |

#### Prioritet 3: Napredne Feature

| Korak | Opis | Kompleksnost | Vrednost |
|-------|------|--------------|----------|
| **Caching** | Redis/memory cache za geocoding | Srednja | Visoka |
| **History** | Pamti prethodne upite | Srednja | Srednja |
| **Web UI** | Streamlit/Gradio interfejs | Srednja | Srednja |
| **Više API-ja** | OpenWeatherMap, WeatherAPI fallback | Visoka | Srednja |

### Git Commit Poruka (za ovu dokumentaciju)

```
docs(session7): add comprehensive MCP documentation

- Document all files in session7/ with architecture diagrams
- Explain stdio vs SSE connection modes with trade-offs
- Add three-model orchestration pattern explanation
- Include troubleshooting guide and next steps
- Add flow diagrams for request handling and error cases
```

---

## Reference

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Open-Meteo API](https://open-meteo.com/en/docs)
- [LangChain Ollama](https://python.langchain.com/docs/integrations/llms/ollama)
- [Session 7 Study Notes](./index.html)
