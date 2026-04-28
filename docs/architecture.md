# Arhitectură și Diagrame

Mai jos sunt diagramele care descriu arhitectura aplicației **OutfitCheck AI**, fluxurile de lucru (workflows) și modelele de date, realizate cu Mermaid.

## 1. Arhitectura Componentelor (C4 Model - Container Level)

```mermaid
graph TD
    User([User / Browser])
    
    subgraph Frontend [Vanilla JS + HTML/CSS]
        UI[User Interface]
        FetchAPI[JS Fetch Layer]
    end
    
    subgraph Backend [FastAPI Application]
        Auth[Auth Router & JWT]
        Wardrobe[Wardrobe Router CRUD]
        Outfits[Outfits Router]
        
        subgraph AI Agents
            Agent1[Outfit Stylist Agent \n Gemini 1.5]
            Agent2[Fashion Critic Agent \n Groq Llama 3.3]
        end
        
        Services[Weather & Image Services]
    end
    
    subgraph External APIs
        Gemini((Google Gemini API))
        Groq((Groq API))
        Weather((OpenWeatherMap))
    end
    
    DB[(SQLite DB)]
    Storage[(Local File System \n Images)]
    
    User <--> UI
    UI <--> FetchAPI
    FetchAPI <--> Auth
    FetchAPI <--> Wardrobe
    FetchAPI <--> Outfits
    
    Auth --> DB
    Wardrobe --> DB
    Wardrobe --> Storage
    Outfits --> DB
    
    Wardrobe --> Agent1
    Outfits --> Agent1
    Outfits --> Agent2
    
    Agent1 --> Gemini
    Agent1 --> Services
    Services --> Weather
    
    Agent2 --> Groq
```

## 2. Diagrama UML a Bazei de Date (Entități și Relații)

```mermaid
erDiagram
    USER {
        string id PK
        string email UK
        string username UK
        string hashed_password
        datetime created_at
    }
    
    GARMENT {
        string id PK
        string user_id FK
        string name
        string category
        string color
        string season
        string occasion
        string image_url
        json ai_tags
    }
    
    OUTFIT {
        string id PK
        string user_id FK
        string name
        json garment_ids
        string occasion
        boolean is_favorite
        float ai_score
        json ai_feedback
    }
    
    AI_FEEDBACK_HISTORY {
        string id PK
        string user_id FK
        string outfit_id FK
        string agent_type
        json input_data
        json output_data
    }
    
    USER ||--o{ GARMENT : owns
    USER ||--o{ OUTFIT : creates
    USER ||--o{ AI_FEEDBACK_HISTORY : has
    OUTFIT ||--o{ AI_FEEDBACK_HISTORY : receives
```

## 3. Workflow: Agent 1 - Outfit Stylist (Upload & Generate)

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant Backend
    participant GeminiAPI
    participant WeatherAPI
    
    User->>Frontend: Upload garment image
    Frontend->>Backend: POST /wardrobe (image + auto-categorize)
    Backend->>GeminiAPI: analyze_image(base64)
    GeminiAPI-->>Backend: JSON(category, color, etc.)
    Backend-->>Frontend: Garment saved
    
    User->>Frontend: Click "Generate Outfits"
    Frontend->>Backend: POST /outfits/suggest (occasion, city)
    Backend->>WeatherAPI: get_weather(city)
    WeatherAPI-->>Backend: weather data
    Backend->>Backend: get_user_wardrobe()
    Backend->>GeminiAPI: prompt(wardrobe + weather + occasion)
    GeminiAPI-->>Backend: 3 suggested outfits (JSON)
    Backend-->>Frontend: Display outfits to User
```

## 4. Workflow: Agent 2 - Fashion Critic

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant Backend
    participant GroqAPI
    participant DB
    
    User->>Frontend: Select items + Click "Get Critique"
    Frontend->>Backend: POST /outfits/critique (garment_ids)
    Backend->>DB: get_garment_details(garment_ids)
    DB-->>Backend: items metadata
    Backend->>DB: get_previous_feedback(user_id)
    DB-->>Backend: user feedback history
    Backend->>GroqAPI: prompt(items + occasion + history)
    Note over GroqAPI: Act as Fashion Critic Persona
    GroqAPI-->>Backend: Scores & Improvements (JSON)
    Backend->>DB: save_feedback_history()
    Backend-->>Frontend: Display Score & Suggestions
```
