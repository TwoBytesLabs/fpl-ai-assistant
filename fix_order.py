import re

with open('frontend/src/App.jsx', 'r') as f:
    app_jsx = f.read()

# Extract blocks
ai_summary_block = """              {/* AI Summary moved to Center Column */}
              {jobData.ai_summary && (
                <div className="panel summary-panel" style={{ marginTop: '1rem', background: 'var(--panel-bg)', border: '1px solid rgba(56, 189, 248, 0.3)' }}>
                  <h2 className="panel-header" style={{ color: '#38bdf8' }}>AI Summary</h2>
                  <p className="ai-summary-text" style={{ margin: 0 }}>{jobData.ai_summary}</p>
                </div>
              )}"""

live_research_block_match = re.search(r'(              \{\/\* Live Web Research Panel \*\/}.*?</div>\n              \}\))', app_jsx, re.DOTALL)
if live_research_block_match:
    live_research_block = live_research_block_match.group(1)
    
    # Remove both
    app_jsx = app_jsx.replace(ai_summary_block, '')
    app_jsx = app_jsx.replace(live_research_block, '')
    
    target = """                  </div>
                )}
              </div>"""
              
    new_insertion = f"{target}\n\n{live_research_block}\n\n{ai_summary_block}"
    app_jsx = app_jsx.replace(target, new_insertion)
    
    with open('frontend/src/App.jsx', 'w') as f:
        f.write(app_jsx)
    print("Successfully swapped UI order!")
else:
    print("Could not find live research block")
