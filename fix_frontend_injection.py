import re

with open('frontend/src/App.jsx', 'r') as f:
    app_jsx = f.read()

# Remove the old attempt if it got inserted in a weird place
app_jsx = re.sub(r'\{\/\* Live Web Research Panel \*\/}.*?Gameweek Fixtures Board \*/}', '{/* Gameweek Fixtures Board */}', app_jsx, flags=re.DOTALL)

target = """              {/* AI Summary moved to Center Column */}
              {jobData.ai_summary && (
                <div className="panel summary-panel" style={{ marginTop: '1rem', background: 'var(--panel-bg)', border: '1px solid rgba(56, 189, 248, 0.3)' }}>
                  <h2 className="panel-header" style={{ color: '#38bdf8' }}>AI Summary</h2>
                  <p className="ai-summary-text" style={{ margin: 0 }}>{jobData.ai_summary}</p>
                </div>
              )}"""

new_panel = """
              {/* Live Web Research Panel */}
              {jobData.live_research && jobData.live_research.length > 0 && (
                <div className="panel" style={{ marginTop: '1rem', border: '1px solid rgba(0, 255, 135, 0.4)' }}>
                  <h2 className="panel-header" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#fff' }}>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" strokeWidth="2">
                      <circle cx="11" cy="11" r="8"></circle>
                      <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                    </svg>
                    Live Web Research Insights
                  </h2>
                  <p style={{ fontSize: '0.9rem', color: '#a3a3a3', marginBottom: '1rem' }}>
                    We detected flagged or at-risk players in your squad. We ran real-time searches across sports networks to override the official FPL API.
                  </p>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {jobData.live_research.map((res, idx) => (
                      <div key={idx} style={{ background: 'rgba(255,255,255,0.05)', padding: '1rem', borderRadius: '8px', borderLeft: `4px solid ${res.decision === 'keep' ? '#10b981' : '#ef4444'}` }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                          <h4 style={{ margin: 0, color: '#fff', fontSize: '1.1rem' }}>{res.player_name}</h4>
                          <span style={{ fontSize: '0.8rem', padding: '0.2rem 0.5rem', background: res.decision === 'keep' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)', color: res.decision === 'keep' ? '#10b981' : '#ef4444', borderRadius: '4px', fontWeight: 'bold' }}>
                            {res.decision === 'keep' ? 'KEEP IN SQUAD' : 'PRIORITY TRANSFER OUT'}
                          </span>
                        </div>
                        <div style={{ fontSize: '0.85rem', color: '#a3a3a3', marginBottom: '0.5rem', display: 'flex', gap: '1rem' }}>
                          <span><strong>FPL Flag:</strong> {res.fpl_status}</span>
                        </div>
                        <div style={{ fontSize: '0.95rem', color: '#fff' }}>
                          <strong>Live Update:</strong> {res.headline}
                          <p style={{ margin: '0.5rem 0', color: '#d1d5db', lineHeight: '1.4' }}>{res.details}</p>
                          <a href={res.url} target="_blank" rel="noopener noreferrer" style={{ color: '#10b981', textDecoration: 'none', fontSize: '0.85rem', display: 'inline-flex', alignItems: 'center', gap: '0.4rem', background: 'rgba(16,185,129,0.1)', padding: '0.3rem 0.6rem', borderRadius: '4px' }}>
                            Source: {res.source} 
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                          </a>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}"""

app_jsx = app_jsx.replace(target, target + new_panel)

with open('frontend/src/App.jsx', 'w') as f:
    f.write(app_jsx)
print("Successfully injected into frontend")
