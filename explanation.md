# SYSTEM CONTEXT: PROJECT EXPLANATION
Hi Claude, Manus, and Perplexity. I am providing you with the complete, ground-truth state of my current project. You cannot read my local files, so this document contains everything you need to know. Treat this document as the absolute source of truth.

---

## 2. High-Level Architecture & Goal
- **App**: FPL AI Assistant v2
- **Goal**: A high-end tool that reads screenshots of a user's Fantasy Premier League (FPL) team using a custom Spatial OCR engine. It runs an ML RandomForest model to project points, calculates optimal transfers, and renders the team visually on an ultra-smooth 3D CSS pitch diorama in the browser.
- **Core Tech Stack**: 
  - Backend: Python 3.13, FastAPI (0.141.1), Uvicorn, EasyOCR, Scikit-Learn, Pandas.
  - Web Scraping: `duckduckgo-search` (DDGS) for real-time live internet access.
  - Frontend: React 19.2.8, Vite 8.2.0.

---

## 3. Infrastructure & Networking (CRITICAL)
- **Ports**: Frontend: 5173, Backend: 3001.
- **Deployment**: Backend targets Render (controlled via `render.yaml`). Frontend targets Vercel.
- **Network Flow**: REST API calls (`fetch`) from React to FastAPI. Backend hits `https://fantasy.premierleague.com/api/` natively without API keys.

---

## 4. Key UI & Visual Implementations
- **Detailed Action Blueprint (`.action-sketch`)**: During the 9-second cinematic intro, an SVG precisely wireframes and "sketches" the Transfers Dropdown and Action Button. It uses a muted color (`rgba(120, 130, 120, 0.7)`) to reduce eye strain and **does not fade out**. Instead, at the 9s mark, the actual HTML inputs fade in precisely *on top* of the sketch, masking it with solid backgrounds.
- **Deep Analytics Radar**: The 5-point radar chart calculates normalized percentages using the true FPL API season totals, effectively scaling against typical season maximums (e.g. `xG / 20.0`, `xGI / 30.0`).
- **Fixtures Pagination**: The fixtures panel receives all 380 PL fixtures. The React UI paginates through them. It natively calculates bounds, explicitly restricting scrolling to `currentGameweek - 2` (past) and `currentGameweek + 3` (future).
- **Player Status Board**: Renders `110x140` player CDN images. The backend strictly alphabetizes names inside severity groups (Red, Yellow, Gray).

---

## 5. Live Web Research Pipeline (Fully Implemented & Real-Time)
- **Concept**: If a player in the OCR'd team has an official FPL status flag (Doubtful, Suspended, Injured, Loaned) OR is exactly on 4 Yellow Cards, the system executes an ACTUAL "Live Web Search" using DuckDuckGo (`duckduckgo-search`). 
- **Context Generation & AI Decisions**: 
  - The Python backend dynamically searches queries like `"{Player Name} injury news premier league"`.
  - It reads the first breaking news article's headline and snippet, running naive sentiment analysis to detect if the player is confirmed "fit", "sidelined", or "ruled out".
  - It generates real working URLs linking directly to search queries for journalism sources (The Athletic, Sky Sports, BBC).
  - The AI Heuristics engine explicitly intercepts these results: if the news confirms the player is fit, their transfer score is artificially boosted by +999.0 to forcefully block the AI from transferring them out. Conversely, if confirmed injured, they get a -999.0 penalty to force a transfer.
- **UI Render**: 
  - The detailed web research context is appended into the `JobData` under `live_research`.
  - The UI layout is strictly ordered: `Recommended Transfers` -> `Live Web Research Insights` -> `AI Summary` -> `Gameweek Fixtures`.
  - The vertical border of each research card maps directly to the FPL flag severity using hex colors sent from the backend: `#10b981` (Green/Fit), `#eab308` (Yellow/Doubtful), `#ef4444` (Red/Injured), `#9ca3af` (Grey/Unavailable).

---

## 6. Current Backend JobData Schema (Pydantic Models)
```python
class JobData(BaseModel):
    # ... standard fields ...
    gameweek_fixtures: Optional[List[Dict[str, Any]]] = None
    budget: Optional[BudgetStatus] = None
    global_injuries: Optional[List[InjuryAlert]] = None
    live_research: Optional[List[Dict[str, Any]]] = None # Powers the Live Research Pipeline
    ai_summary: Optional[str] = None
    team_stats: Optional[List[Dict[str, Any]]] = None
```

---

## 7. Roadmap: Future UI Segment Ideas
The following are highly analytical features brainstormed for future implementation into the dashboard:

1. **The Captaincy Matrix (©️)**: The AI scans the user's 15 players, picks the top 3 best captaincy options, and creates a dedicated comparison panel utilizing the Live Web Scraper to analyze opponent defensive weaknesses.
2. **Market Watch (Price Predictor) (📉)**: A sleek, ticker-style panel that flags players in the squad who are dangerously close to dropping in price tonight, or transfer targets who are about to rise. 
3. **Fixture Swing Heatmap (FDR) (🔥)**: A color-coded grid (Dark Green to Dark Red) showing the next 5 gameweeks—but *only* for the players currently in the user's squad. Highlights structural weaknesses in the current defense or attack.
4. **The "Differential" Scout (🎯)**: A neon-styled panel that recommends exactly one player with under 10% global ownership who has a massive projected score for the next 3 weeks to act as a rank-booster.
5. **Set-Piece Threat Board (👟)**: Scans the OCR team against FPL API data to highlight the user's set-piece takers (Penalties, Free Kicks, Corners), analyzing their potential for random haul points.
6. **Budget Restructure Analyzer (💰)**: A mini-chart displaying team value distribution compared to the current global meta (e.g. highlighting if the user is spending too much on defense when premium midfielders are scoring more points).
