import re

with open('frontend/src/App.jsx', 'r') as f:
    app_jsx = f.read()

# Replace the borderLeft style
old_border = "borderLeft: `4px solid ${res.decision === 'keep' ? '#10b981' : '#ef4444'}`"
new_border = "borderLeft: `4px solid ${res.color || (res.decision === 'keep' ? '#10b981' : '#ef4444')}`"
app_jsx = app_jsx.replace(old_border, new_border)

# Let's completely enforce the UI ordering:
# 1. Recommended Transfers
# 2. Live Web Research Panel
# 3. AI Summary
# 4. Gameweek Fixtures

# Strip them all out temporarily
transfers_match = re.search(r'(\{\/\* Recommended Transfers.*?</div>\n                \)\}\n              </div>)', app_jsx, re.DOTALL)
if not transfers_match:
    # Let's just use simple text replacement for the whole chunk
    pass

# Actually, earlier I ordered it:
# 1. <div className="results-section main-column"> ... Recommended transfers ... </div>
# 2. {/* AI Summary moved to Center Column */}
# 3. {/* Live Web Research Panel */}

# I want:
# 1. <div className="results-section main-column"> ... Recommended transfers ... </div>
# 2. {/* Live Web Research Panel */}
# 3. {/* AI Summary moved to Center Column */}

ai_block_regex = r'(              \{\/\* AI Summary moved to Center Column \*\/}.*?</div>\n              \}\))\n'
live_block_regex = r'(              \{\/\* Live Web Research Panel \*\/}.*?</div>\n              \}\))\n'

ai_match = re.search(ai_block_regex, app_jsx, re.DOTALL)
live_match = re.search(live_block_regex, app_jsx, re.DOTALL)

if ai_match and live_match:
    ai_text = ai_match.group(1) + '\n'
    live_text = live_match.group(1) + '\n'
    
    # Remove them
    app_jsx = app_jsx.replace(ai_text, '')
    app_jsx = app_jsx.replace(live_text, '')
    
    # Find insertion point (right before Gameweek Fixtures Board)
    insertion_target = "              {/* Gameweek Fixtures Board */}"
    
    # Insert in correct order: Live Research first, then AI Summary
    correct_order = f"{live_text}{ai_text}{insertion_target}"
    app_jsx = app_jsx.replace(insertion_target, correct_order)
    
    with open('frontend/src/App.jsx', 'w') as f:
        f.write(app_jsx)
    print("Frontend updated with color logic and correct order.")
else:
    print("Regex failed to find blocks.")
