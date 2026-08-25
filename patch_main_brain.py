import re

with open('backend/main.py', 'r') as f:
    main_py = f.read()

# Current logic in main.py:
# t_cards = get_best_transfers(starters, bench, ...)
# job.live_research = run_live_research(starters + bench)

# I need to swap them and pass job.live_research into get_best_transfers

old_logic = """        # Stage 7: Heuristics
        job.stage = "Calculating optimal transfers"
        job.progress = 70
        job_manager.save(job)
        
        used_ids = {p['id'] for p in starters + bench}
        
        starters, bench, t_cards = get_best_transfers(
            starters, bench, 
            fpl_data.get('elements', []), 
            used_ids, transfers, 
            strategy,
            bank_balance
        )
        
        # Determine global issues
        job.stage = "Fetching news and injuries"
        job.progress = 85
        job_manager.save(job)
        
        job.live_research = run_live_research(starters + bench)"""

new_logic = """        # Stage 7: Heuristics & Live Research
        job.stage = "Running Live Web Research & Transfer Heuristics"
        job.progress = 70
        job_manager.save(job)
        
        # Must run live research FIRST so the transfer AI knows who to keep/sell
        job.live_research = run_live_research(starters + bench)
        
        used_ids = {p['id'] for p in starters + bench}
        
        starters, bench, t_cards = get_best_transfers(
            starters, bench, 
            fpl_data.get('elements', []), 
            used_ids, transfers, 
            strategy,
            bank_balance,
            job.live_research
        )
        
        # Determine global issues
        job.stage = "Fetching news and injuries"
        job.progress = 85
        job_manager.save(job)"""

if "run_live_research(starters + bench)" in main_py and new_logic not in main_py:
    main_py = main_py.replace(old_logic, new_logic)
    with open('backend/main.py', 'w') as f:
        f.write(main_py)
    print("main.py patched")
else:
    print("main.py pattern not found or already patched")
