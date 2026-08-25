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
- **Detailed Action Blueprint (`.action-sketch`)**: During the 9-second cinematic intro, an SVG precisely wireframes and "sketches" the Transfers Dropdown and Action Button using `stroke-dashoffset`. It uses a muted color (`rgba(120, 130, 120, 0.7)`) to reduce eye strain and **does not fade out**. Instead, at the 9s mark, the actual HTML inputs (`.minimal-actions`) fade in precisely *on top* of the sketch, masking it with solid backgrounds to create the illusion of color filling in.
- **Deep Analytics Radar**: The 5-point radar chart calculates normalized percentages using the true FPL API season totals, effectively scaling against typical season maximums (e.g. `xG / 20.0`, `xGI / 30.0`).
- **Fixtures Pagination**: The fixtures panel receives all 380 PL fixtures. The React UI paginates through them. It natively calculates bounds, explicitly restricting scrolling to `currentGameweek - 2` (past) and `currentGameweek + 3` (future).
- **Player Status Board**: Renders `110x140` player CDN images. The backend strictly alphabetizes names inside severity groups (Red, Yellow, Gray).

---

## 5. Live Web Research Pipeline (Upcoming/Planned Feature)
- **Concept**: The user heavily depends on injury news. If a player in the OCR'd team has an official FPL status of 'd' (Doubtful), 's' (Suspended), 'i' (Injured), or 'u' (Loaned), the system cannot blindly trust the FPL "chance of playing" percentage.
- **Implementation**: The backend must execute a simulated (or real, via SerpAPI) "Live Web Search" to override the FPL API. 
- **Context Generation**: If the search confirms a doubtful player is starting (e.g., confirmed via press conference), the AI creates a `live_research` contextual note to `KEEP` the player. If it confirms the injury/suspension, it changes to `SELL`.
- **UI Render**: This detailed web research context is appended into the `JobData` under `live_research`. The frontend conditionally renders a "Live Web Research Insights" panel displaying the mocked/scraped journalistic evidence (headline, details, source) immediately below the Recommended Transfers box, ONLY if the user actually has flagged players.

---

## 6. Current Backend JobData Schema (Pydantic Models)
```python
class JobData(BaseModel):
    # ... standard fields ...
    gameweek_fixtures: Optional[List[Dict[str, Any]]] = None # Contains ALL fixtures
    budget: Optional[BudgetStatus] = None
    global_injuries: Optional[List[InjuryAlert]] = None
    live_research: Optional[List[Dict[str, Any]]] = None # Crucial for the Live Research Pipeline
    ai_summary: Optional[str] = None
    team_stats: Optional[List[Dict[str, Any]]] = None # Used to pass current_event ID
```
