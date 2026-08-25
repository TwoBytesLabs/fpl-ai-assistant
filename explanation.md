# SYSTEM CONTEXT: PROJECT EXPLANATION
Hi Claude, Manus, and Perplexity. I am providing you with the complete, ground-truth state of my current project. You cannot read my local files, so this document contains everything you need to know. Treat this document as the absolute source of truth.

---

## 2. High-Level Architecture & Goal
- **App**: FPL AI Assistant v2
- **Goal**: A high-end tool that reads screenshots of a user's Fantasy Premier League (FPL) team using a custom Spatial OCR engine. It runs an ML RandomForest model to project points, calculates optimal transfers, and renders the team visually on an ultra-smooth 3D CSS pitch diorama in the browser.
- **Core Tech Stack**: 
  - Backend: Python 3.13, FastAPI (0.141.1), Uvicorn, EasyOCR, Scikit-Learn, Pandas.
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

## 5. Live Web Research Pipeline (Fully Implemented)
- **Concept**: If a player in the OCR'd team has an official FPL status flag (Doubtful, Suspended, Injured, Loaned) OR is exactly on 4 Yellow Cards (1 away from suspension), the system executes a "Live Web Search" to override the FPL API. 
- **Context Generation & Decisions**: 
  - **Doubtful/Injured**: If mock research confirms they are starting, the AI creates a `live_research` note to `KEEP` the player.
  - **4 Yellow Cards**: Generates a strict warning about the imminent 1-match suspension, but defaults to `KEEP` if their stats are strong.
  - **Red Cards/Suspended**: Confirms the appeal status (e.g. "rejected, serving full suspension") and marks as `SELL`.
- **UI Render**: This detailed web research context is appended into the `JobData` under `live_research`. The frontend conditionally renders a "Live Web Research Insights" panel displaying the scraped journalistic evidence (headline, injury details, source link) immediately below the Recommended Transfers box. The AI Summary text is also dynamically injected with a bold **"Live Research Override"** paragraph to explain the deviation from the FPL API.

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
