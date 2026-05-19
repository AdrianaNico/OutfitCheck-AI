<div align="center">

<img width="150" alt="logo" src="https://github.com/user-attachments/assets/316c8d9d-a4ef-415b-a619-243fc2f7827d" />

# OutfitCheck AI 👗✨
**Your AI-powered fashion assistant for a smarter, more stylish wardrobe.**

</div>

## 📌 Despre Proiect

**OutfitCheck AI** este un stilist digital care îți transformă modul în care îți gestionezi hainele. Proiectul include o interfață premium cu *glassmorphism*, un backend robust în FastAPI și **2 Agenți AI**:
1. **Outfit Stylist (Gemini)**: Analizează vizual hainele încărcate și generează sugestii de outfit-uri pe baza vremii și ocaziei.
2. **Fashion Critic (Groq/Llama)**: Oferă feedback critic, scor și sugestii de îmbunătățire pentru outfit-urile selectate.

---

## 🎯 Cerințe Îndeplinite (MDS Project 2026)

Acest repository conține toate elementele cerute pentru proiect:

### A. Implementare
- **Live Demo & Screencast**: [Link către Video Demo / YouTube] *(a se completa de către echipă)*
- **2 Agenți AI Integrate**: 
  - [Agent 1: Outfit Stylist (backend/agents/outfit_stylist.py)](backend/agents/outfit_stylist.py) - folosește tool use (vreme) și reasoning.
  - [Agent 2: Fashion Critic (backend/agents/fashion_critic.py)](backend/agents/fashion_critic.py) - folosește memory și persona-based reasoning.

### B. Procesul de Dezvoltare Software cu AI
- ✅ **User Stories & Backlog**: Găsiți cele 10 user stories documentate mai jos în acest README, implementate în cod, și mapate ca Issues în tab-ul GitHub Issues.
- ✅ **Diagrame (Arhitectură & UML)**: Documentate în detaliu în [`docs/architecture.md`](docs/architecture.md) (create cu Mermaid).
- ✅ **Source Control (Git)**: Utilizat branch-ul `main`, realizate pull requests, cu minim 5 commit-uri per student (vezi secțiunea Insights -> Contributors).
- ✅ **Teste Automate & Evals**: Configurat Pytest. Există teste unitare și *evaluări speciale pentru agenții AI* în directorul [`tests/evals/test_agents.py`](tests/evals/test_agents.py).
- ✅ **Raportare Bug & Rezolvare**: Realizat prin Pull Request dedicat în GitHub (vezi tab-ul PRs).
- ✅ **Pipeline CI/CD**: Implementat via GitHub Actions. Rulează automat testele și linter-ul (Flake8) la fiecare PR/Push. Vezi [`.github/workflows/ci.yml`](.github/workflows/ci.yml).
- ✅ **Raport Tooluri AI**: Documentat detaliat modul în care a fost utilizat AI-ul în SDLC în [`docs/ai_tools_report.md`](docs/ai_tools_report.md).

---

## 🛠️ Tehnologii Folosite

- **Frontend**: Vanilla HTML/JS/CSS (Premium Glassmorphism Design System)
- **Backend**: Python FastAPI, SQLAlchemy (SQLite)
- **AI Models**: Google Gemini 1.5 Flash, Groq Llama 3.3 70B
- **CI/CD & Source Control**: GitHub Actions, Git
- **Testing**: Pytest, Pytest-Asyncio

---

## 📝 User Stories Implementate

| Role | I want to... | So that... |
| :--- | :--- | :--- |
| **User** | Create a secure account | My virtual wardrobe and personal style preferences are securely saved and accessible from my phone. |
| **User** | Upload photos of my clothes for automatic categorization | I don’t have to manually organize my digital closet. |
| **User** | Add and delete items from my virtual wardrobe | My digital closet stays accurate and easy to navigate. |
| **User** | Get outfit suggestions based on wardrobe, weather, and occasion | I save time and don’t have to stress about what to wear. |
| **User** | See a digital visualization of outfit combinations | I can preview how the pieces look together without physically trying them on. |
| **User** | Save favorite outfits into a "Favorites" folder | I have quick access to my best looks on days when I am in a hurry. |
| **User** | Get an automated review from the AI Fashion Critic agent | I can receive objective feedback on my style, color matching, and suitability. |
| **User** | Search using natural language (e.g., “black elegant dress”) | I can quickly find specific items without using complex filters. |
| **User** | Upload a photo and receive links to similar clothing | *(Implementat via Gemini Vision Auto-categorize)* I can easily recreate styles I see on the internet. |
| **User** | Search for outfits online based on a specific vibe or style | *(Implementat via NLP Search)* I can easily get inspired and put together unique looks. |

---

## 🚀 Cum rulezi proiectul local

1. **Clonează repo-ul**:
```bash
git clone https://github.com/AnastasiaMitrea/OutfitCheck-AI.git
cd OutfitCheck-AI
```

2. **Creează un mediu virtual și instalează dependențele**:
```bash
python -m venv venv
# Pe Windows:
venv\Scripts\activate
# Pe Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

3. **Configurează variabilele de mediu**:
Creează un fișier `.env` în rădăcina proiectului pornind de la `.env.example` și adaugă cheile tale pentru API-urile Gemini și Groq.

4. **Pornește serverul FastAPI**:
```bash
python -m uvicorn backend.main:app --reload --port 8000
```
5. Accesează **http://localhost:8000** în browser-ul tău!

---

## 👥 Echipa (Metode de Dezvoltare Software 2026 - FMI Unibuc)

- **Guna Adriana** (Backend API & Integrare Agenți AI)
- **Ionita Maria** (Frontend Design System & UI Components)
- **Mitrea Ioana** (Database Architecture & Auth)
- **Tighinean Sonia** (Search NLP, CI/CD & Testing)
