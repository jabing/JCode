Task: Remove AgentManager usage from jcode_start.py
- Replaced dynamic agent loading with a direct static list of agents.
- Verification: grep -n "AgentManager" jcode_start.py should return no matches.
- Rationale: Decouples startup from core module, simplifying startup and reducing runtime dependencies.
