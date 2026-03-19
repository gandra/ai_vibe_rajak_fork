# Ollama na macOS

---

## Rad sa Ollamom (Homebrew instalacija)

### Pokretanje i zaustavljanje

```bash
# Pokreni Ollama kao background servis (automatski se pokreće i posle restarta)
brew services start ollama

# Zaustavi servis
brew services stop ollama

# Restartuj servis
brew services restart ollama

# Proveri status servisa
brew services info ollama

# Jednokratno pokretanje (bez background servisa, radi dok ne zatvoriš terminal)
ollama serve
```

> **Port:** Ollama podrazumevano sluša na `http://127.0.0.1:11434`. Promeni sa `OLLAMA_HOST=0.0.0.0:11434 ollama serve` ako treba da bude dostupan sa mreže.

### Upravljanje modelima

```bash
# Preuzmi model
ollama pull gemma3:4b
ollama pull llama3.2:3b
ollama pull nomic-embed-text      # Embedding model

# Lista svih preuzetih modela (na disku)
ollama list

# Koji modeli su trenutno učitani u memoriju (aktivni)
ollama ps

# Pokreni model interaktivno (chat u terminalu)
ollama run gemma3:4b

# Obriši model sa diska
ollama rm gemma3:4b

# Prikaži info o modelu (parametri, veličina, template)
ollama show gemma3:4b
```

### Provera da li servis radi

```bash
# Brz health check
curl http://localhost:11434

# Trebalo bi da vrati: "Ollama is running"

# Lista aktivnih modela preko API-ja
curl http://localhost:11434/api/tags
```

### Korisne environment varijable

```bash
export OLLAMA_HOST="http://127.0.0.1:11434"   # URL servera
export OLLAMA_MODEL="gemma3:4b"                # Default model za skriptove u ovom projektu
```

---

## Kako utvrditi na koji način je Ollama instalirana

Na macOS-u Ollama može biti instalirana na dva načina: preko **Homebrew** ili preko **desktop aplikacije** (.dmg / .app). Bitno je znati koji način koristiš jer se razlikuje način pokretanja i zaustavljanja.

### Provera: Homebrew

```bash
brew list | grep ollama
```

Ako vrati `ollama` — instalirana je preko Homebrew-a.

```bash
# Dodatna potvrda — putanja do binarnog fajla
which ollama
# Homebrew: /opt/homebrew/bin/ollama (Apple Silicon) ili /usr/local/bin/ollama (Intel)
```

### Provera: Desktop aplikacija (.app)

```bash
ls /Applications/Ollama.app
```

Ako folder postoji — instalirana je kao desktop aplikacija (preuzeta sa ollama.com kao .dmg).

```bash
# Binarka desktop verzije je unutar .app bundle-a
# /Applications/Ollama.app/Contents/MacOS/Ollama

# Ako which ollama i dalje vraća putanju, desktop app registruje CLI helper:
which ollama
# Desktop app: /usr/local/bin/ollama (symlink koji kreira .app prilikom prvog pokretanja)
```

### Razlike u praksi

| | Homebrew | Desktop App (.dmg) |
|--|---------|-------------------|
| Instalacija | `brew install ollama` | Preuzmi .dmg sa ollama.com |
| Binarka | `/opt/homebrew/bin/ollama` | `/Applications/Ollama.app/...` |
| Pokretanje servisa | `brew services start ollama` | Otvori Ollama.app (ikonica u menu bar-u) |
| Zaustavljanje | `brew services stop ollama` | Quit iz menu bar-a |
| Auto-start | `brew services start` (launchd) | System Settings → Login Items |
| Ažuriranje | `brew upgrade ollama` | App se ažurira automatski |
| Deinstalacija | `brew uninstall ollama` | Obriši iz /Applications |

### Obe su instalirane?

```bash
brew list | grep ollama && echo "--- Homebrew: DA" || echo "--- Homebrew: NE"
ls /Applications/Ollama.app &>/dev/null && echo "--- Desktop app: DA" || echo "--- Desktop app: NE"
```

Ako su obe prisutne, može doći do konflikta (dva servisa na istom portu). Preporuka je da koristiš samo jednu. Za ovaj projekat Homebrew je dovoljno — nema potrebe za desktop aplikacijom.

### Uklanjanje desktop app-a (ako koristiš Homebrew)

```bash
# Zatvori app ako radi
osascript -e 'quit app "Ollama"'

# Obriši
rm -rf /Applications/Ollama.app
rm -rf ~/.ollama                    # Ovo briše i SVE modele — preskoči ako ih želiš zadržati
```

### Uklanjanje Homebrew verzije (ako koristiš desktop app)

```bash
brew services stop ollama
brew uninstall ollama
```
