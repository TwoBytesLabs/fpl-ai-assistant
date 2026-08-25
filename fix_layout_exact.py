import re

with open('frontend/src/App.jsx', 'r') as f:
    app_jsx = f.read()

# I will find the exact blocks using string splits since I know the exact comments
part1 = app_jsx.split("{/* AI Summary moved to Center Column */}")[0]
rest1 = app_jsx.split("{/* AI Summary moved to Center Column */}")[1]

ai_summary_block = "{/* AI Summary moved to Center Column */}" + rest1.split("{/* Live Web Research Panel */}")[0]
rest2 = rest1.split("{/* Live Web Research Panel */}")[1]

live_research_block = "{/* Live Web Research Panel */}" + rest2.split("{/* Gameweek Fixtures Board */}")[0]
part3 = "{/* Gameweek Fixtures Board */}" + rest2.split("{/* Gameweek Fixtures Board */}")[1]

# Now let's fix the colors in live_research_block
old_border = "borderLeft: `4px solid ${res.decision === 'keep' ? '#10b981' : '#ef4444'}`"
new_border = "borderLeft: `4px solid ${res.color || (res.decision === 'keep' ? '#10b981' : '#ef4444')}`"
live_research_block = live_research_block.replace(old_border, new_border)

# Now put it together in the right order (Part 1 -> Live Research -> AI Summary -> Part 3)
new_app_jsx = part1 + live_research_block + ai_summary_block + part3

with open('frontend/src/App.jsx', 'w') as f:
    f.write(new_app_jsx)

print("Frontend layout explicitly reordered and colors fixed!")
