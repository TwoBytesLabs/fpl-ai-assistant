# CLAUDE HANDOFF: FPL AI ASSISTANT V2

Hello Claude. This document contains the absolute ground-truth, granular details of the FPL AI Assistant v2 project. You are taking over development, and the user expects you to understand every single detail, modification, and architectural decision that led to this point, as well as the exact fixes required moving forward.

## 1. Project Overview & Architecture
This is a highly advanced, full-stack application that analyzes screenshots of a Fantasy Premier League (FPL) team, runs spatial computer vision to detect the squad, uses a custom TinyML model to project points, scrapes the live internet for breaking news, and provides optimal transfer recommendations on a futuristic 3D React dashboard.

*   **Backend**: Python 3.13, FastAPI, Uvicorn, EasyOCR, Scikit-Learn (RandomForest), DuckDuckGo-Search, RapidFuzz.
*   **Frontend**: React 19, Vite, raw CSS (for 3D transforms and SVG animations).
*   **Start Mechanism**: Handled via `start_all.py` triggered by `npm run dev` at the root folder, which concurrently starts FastAPI and Vite.

---

## 2. The Spatial OCR Engine (`backend/services/ocr.py`)
We do not just blindly read text from the image. We built a heavily modified, spatially-aware OCR engine using `easyocr` and `OpenCV`.
*   **How it's smarter**: FPL pitch screenshots follow a strict top-to-bottom layout. The engine groups detected text bounding boxes by their **Y-coordinates** to explicitly segment the pitch into rows: 
    *   Row 0: GK
    *   Row 1: DEF
    *   Row 2: MID
    *   Row 3: FWD
    *   Row 4: Bench
*   **Dynamic Formation Detection**: By counting the bounding boxes in each Y-cluster, it deduces the exact formation (e.g., 3-4-3, 4-4-2) natively, rather than relying on the FPL API's registered position for the player.
*   **Fuzzy Matching**: Uses `rapidfuzz` to match the OCR output against the official FPL `bootstrap-static` element names, correcting typos from low-resolution screenshots.

---

## 3. The TinyML Engine (`backend/services/ml_engine.py`)
We are using a lightweight `RandomForestRegressor` from `scikit-learn` trained on the fly.
*   **How we modified it**: Instead of just predicting points based on the FPL API's `ep_next` (Expected Points Next), we built a proprietary **"True Value"** training target.
*   **The Math**: `Target = (Form * 0.2) + (ICT_Index / 10.0 * 0.3) + (Points_Per_Game * 0.5)`. 
*   **Why?** This penalizes players who are on a lucky 1-2 gameweek "form" streak but have poor underlying ICT (Influence, Creativity, Threat) stats, ensuring the AI favors long-term statistical assets.

---

## 4. Super-Small UI/UX Layout Details
The frontend is built to feel cinematic, analytical, and highly polished.
*   **The SVG Blueprint Loader (`.action-sketch`)**: During the 9-second initial app load, an SVG perfectly traces the physical outline of the UI text and borders. It does *not* fade out; instead, at 9 seconds, the actual HTML elements fade in directly on top of the sketch to "color it in."
*   **The 3D CSS Pitch**: The squad isn't rendered flat. The CSS applies deep `perspective`, `rotateX`, and `translateZ` transforms to render the pitch as a diorama.
*   **Deep Analytics Radar**: Maps 5 stats (xG, xA, Form, Threat, ICT). We specifically normalized these against typical season highs (e.g., dividing xG by 20.0) so the charts aren't blown out to 1000% early in the season.
*   **Strict Panel Hierarchy**: 
    1.  `Recommended Transfers` (Calculated by the heuristic engine).
    2.  `Live Web Research Insights` (Conditionally rendered if flags are detected).
    3.  `AI Summary` (Includes a specific note if the AI overrode a decision based on web research).
    4.  `Gameweek Fixtures` (Paginated, mathematically bounded to `current_gw - 2` and `current_gw + 3`).

---

## 5. The Live Web Research Pipeline (AND WHAT YOU NEED TO FIX)
If the FPL API flags a player as injured (`i`), doubtful (`d`), suspended (`s`), or on 4 yellow cards, the backend (`analytics.py` -> `run_live_research`) actively queries DuckDuckGo (`duckduckgo-search`).
*   **How it integrates**: It passes a `color` prop to the frontend mapping to the severity: `#10b981` (Green/Fit), `#eab308` (Yellow), `#ef4444` (Red), `#9ca3af` (Grey/Loaned). It also passes a `decision` (keep/sell) which massively boosts (+999) or tanks (-999) the player's score in the transfer algorithm to force the AI's hand.

### 🔴 THE PROBLEM (YOUR IMMEDIATE TASKS)
The user requires a major upgrade to the "analyzing power" of this specific DuckDuckGo web scraping pipeline. Right now, it has the following flaws that **you must fix**:

1.  **Worthless Links**: Currently, the links provided in the UI are just generic search queries (e.g., `https://www.skysports.com/search?q=...`). **Fix**: You must extract the EXACT article URL from the DDG search results that actually *proves* the point.
2.  **Transferred/Loaned Players**: The system entirely misses players who have permanently left for another team. **Fix**: Implement logic to detect "permanent transfer" or "loaned out" news and accurately reflect this in the UI.
3.  **Nuanced Sentiment Analysis**: The current keyword matching is too naive. You need to implement deeper text analysis to perfectly categorize and display the following scenarios in the UI descriptions:
    *   The player is FPL-flagged as injured, but the article proves **he CAN play**.
    *   The player is FPL-flagged as injured, and the article proves **he CANNOT play**.
    *   The player has a Red Card vs. 4 Yellow Cards (imminent suspension).
    *   The player has permanently left the club.

Do not alter the overarching system architecture. Focus entirely on massively enhancing the NLP/analyzing power of `run_live_research` in `analytics.py` to achieve these precise goals.
