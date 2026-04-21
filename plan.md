# 📄 Progetto Sito Statico con Archivio Documenti

## 🎯 Obiettivo

Realizzare un sito statico con:

- archivio documenti (PDF)
- gestione contenuti tramite interfaccia per utenti non tecnici
- zero backend custom
- costi nulli o trascurabili
- massima semplicità operativa

---

## 🧱 Stack Tecnologico

### Frontend
- **Astro (SSG)**
  - Generazione statica
  - Performance elevate
  - Routing file-based
  - Content Collections

### CMS
- **Decap CMS**
  - CMS Git-based
  - UI web per utenti non tecnici
  - Salva contenuti direttamente su repository Git
  - Supporta upload file e media drag & drop

### Hosting
- **GitHub Pages** (oppure Cloudflare / Netlify / Vercel)
  - Hosting statico gratuito
  - Deploy automatico da Git

### Storage documenti (fase iniziale)
- **GitHub repository**
  - I PDF sono salvati in `/public/docs`
  - Nessuna infrastruttura aggiuntiva

### Storage futuro (opzionale)
- Cloudflare R2 / S3 (quando necessario)

---

## 🧠 Architettura

```plaintext
Editor (Decap CMS UI)
↓
GitHub Repository (contenuti + PDF)
↓
Astro build (SSG)
↓
Hosting statico (Cloudflare Pages)
↓
Utenti finali
```

👉 Decap CMS funziona come interfaccia sopra Git, permettendo agli utenti di modificare contenuti senza usare Git direttamente

---

## 📁 Struttura progetto

```plaintext
/
├── public/
│   ├── docs/              # PDF
│   └── admin/             # Decap CMS
│       ├── index.html
│       └── config.yml
│
├── src/
│   ├── content/
│   │   └── documents/     # markdown documenti
│   │
│   ├── pages/
│   │   ├── index.astro
│   │   └── archivio.astro
│   │
│   └── components/
│
├── astro.config.mjs
└── package.json

```

---

## 📄 Modello dati (Documenti)

Ogni documento è un file Markdown:

```markdown
---
title: "Titolo documento"
description: "Descrizione breve"
date: "2026-01-01"
file: "/docs/nome-file.pdf"
category: "Categoria"
---
```

---

## ⚙️ Configurazione Decap CMS

File: `/public/admin/config.yml`

```yaml
backend:
  name: github
  repo: "USERNAME/REPO"
  branch: main

media_folder: "public/docs"
public_folder: "/docs"

collections:
  - name: "documents"
    label: "Documenti"
    folder: "src/content/documents"
    create: true
    slug: "{{slug}}"
    fields:
      - { label: "Titolo", name: "title", widget: "string" }
      - { label: "Descrizione", name: "description", widget: "text" }
      - { label: "Data", name: "date", widget: "datetime" }
      - { label: "Categoria", name: "category", widget: "string" }
      - { label: "File PDF", name: "file", widget: "file" }
```

---

## 🖥️ Admin CMS

* URL: `/admin`
* Decap CMS è una web app React integrata nel sito
* Permette:

  * creazione contenuti
  * upload file
  * modifica contenuti
  * pubblicazione (commit Git automatico)

---

## 🔁 Flusso di aggiornamento contenuti

1. Admin accede a `/admin`
2. Crea/modifica documento
3. Upload PDF
4. Click su "Publish"
5. Decap crea commit su GitHub
6. Hosting triggera build automatica
7. Sito aggiornato

---

## 📚 Pagina Archivio Documenti

Funzionalità:

* lista documenti
* ordinamento per data
* filtro per categoria (opzionale)
* link download PDF

---

## 💡 Best practice

* usare slug leggibili
* evitare nomi file ambigui
* mantenere categorie coerenti
* evitare PDF troppo pesanti (>5-10MB)

---

## 🚫 Cosa NON fare

* ❌ backend custom per upload
* ❌ database separato
* ❌ storage esterni non necessari (Drive, ecc.)
* ❌ CMS complessi (overkill)

---

## 🔮 Evoluzioni future

Quando necessario:

* migrare PDF su R2/S3
* aggiungere ricerca client-side (Fuse.js)
* tagging avanzato
* preview contenuti
* autenticazione editor più avanzata

---

## 🚀 Setup iniziale

```bash
npm create astro@latest
npm install
```

Aggiungere Decap CMS:

```html
<!-- public/admin/index.html -->
<script src="https://unpkg.com/decap-cms@latest/dist/decap-cms.js"></script>
```

👉 Decap richiede solo pochi file per funzionare

---

## 🧠 Linee guida sviluppo

* mantenere codice semplice
* evitare astrazioni premature
* privilegiare leggibilità
* progettare per contenuti, non per features

---

## ✅ Deliverable

* sito statico funzionante
* CMS accessibile da `/admin`
* archivio documenti navigabile
* flusso editor semplice

---

## 🧾 Note finali

Questo progetto segue un approccio **Jamstack**:

- contenuti su Git
- frontend statico
- nessun backend runtime

👉 risultato:

- performance elevate
- costi nulli
- manutenzione minima
