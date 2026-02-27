MCP Tool: implement - Code implementation
MCP Architecture
- Tool Call Flow
- 1. Context: Prepare input_data with TASKS and analysis for the MCP tool.
- 2. MCP call: Use MCP client to invoke, mode full.
- 3. MCP response: Receive results with code artifacts, diffs, logs.
- 4. Implementer consumes output: generate code; update files.
- 5. Verification: Run diagnostics and build.
- 6. Audit: log the operation.
