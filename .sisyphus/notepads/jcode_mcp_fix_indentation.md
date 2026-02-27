Fix: Indentation error in jcode_mcp/server.py line 238.
- Changed: Indented 'from jcode_mcp.jcode_server import create_server' to be inside the 'try:' block.
- Indentation now matches the expected state:
  - Before:  no indentation on the import line inside try
  - After:   12 spaces before 'from' inside try

Verification plan:
- Run server with: 
  cd C:/dev_projects/jcode
  set PYTHONPATH=C:/dev_projects/jcode
  python -m jcode_mcp.server --port 8080 &
  sleep 5
  curl -s -X POST http://localhost:8080/mcp -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
- Expect: JSON with a 'tools' array of 6 tools
