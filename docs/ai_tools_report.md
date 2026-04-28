# Raport: Utilizarea Tool-urilor AI în Dezvoltarea Software

Pentru proiectul **OutfitCheck AI**, am integrat multiple tool-uri AI de-a lungul întregului proces de dezvoltare software, respectând cerințele (B. Procesul de dezvoltare software cu AI).

## 1. Planificare & Arhitectură (Faza Inițială)
- **Tool**: Google Gemini 1.5 Pro, Antigravity AI (DeepMind)
- **Mod de utilizare**: Am generat structura documentului de arhitectură, diagrama de workflow și user story-urile. Am folosit AI-ul ca pe un *sounding board* pentru a alege stack-ul tehnologic (Next.js/FastAPI vs Vanilla JS/FastAPI), optimizând pentru gratuitate și rapiditate în execuție.

## 2. Generare Cod & Dezvoltare (Implementare)
- **Tool**: Antigravity AI, GitHub Copilot
- **Mod de utilizare**: 
  - Generarea boilerplate-ului pentru FastAPI (models, schemas, routers, auth).
  - Generarea design system-ului CSS (`style.css`), creând un UI premium "glassmorphism" fără a scrie manual sute de linii de CSS.
  - Scrierea logicii agenților (integrarea SDK-urilor Gemini și Groq).

## 3. Testare Automată & Evals
- **Tool**: Antigravity AI (LLM-assisted test generation)
- **Mod de utilizare**: Am generat testele unitare și structura pentru `pytest`. Mai mult, am creat *AI Evals* (teste de evaluare a comportamentului agenților AI), de exemplu verificând dacă "Fashion Critic" respectă strict formatul JSON, indiferent de halucinațiile modelului LLM din spate.

## 4. Debugging & CI/CD
- **Tool**: Antigravity AI
- **Mod de utilizare**: Când am întâmpinat erori la execuția `npm` în mediul local (Node.js nefiind instalat), asistentul AI a pivotat arhitectura automat, adaptând frontend-ul din Next.js în Vanilla JS + Jinja2 (servit direct din FastAPI) fără a pierde calitatea vizuală. De asemenea, a generat fișierul `.github/workflows/ci.yml`.

## 5. Cei doi Agenți AI integrați în aplicație
- **Agent 1 (Outfit Stylist - Gemini 1.5 Flash)**: Folosește *tool use* pentru a citi vremea de pe un API extern, analizează JSON-ul cu garderoba și returnează sugestii structurate. De asemenea, folosește *Vision* pentru categorizarea automată a hainelor urcate.
- **Agent 2 (Fashion Critic - Groq Llama 3.3 70B)**: Un agent bazat pe o *persona* specifică (critic de modă) care primește un context complex, aplică un scor obiectiv și dă feedback aplicabil. 

**Concluzie**: Utilizarea AI-ului a crescut viteza de dezvoltare de la săptămâni la zile, reducând semnificativ "boilerplate code-ul" și permițând echipei să se concentreze pe logica de business și arhitectura agenților.
