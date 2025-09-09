# PowerShell Command Workarounds

## Commands that STALL in PowerShell:
- `mkdir` - stalls terminal
- `cd ..` - stalls terminal

## Working Alternatives:
- Instead of `mkdir`: Use `write` tool to create files directly (creates parent directories automatically)
- Instead of `cd ..`: Use `Set-Location ..` or `Set-Location -Path ..`

## Memory Rule:
Always use PowerShell-native commands and avoid bash-style commands that cause terminal stalling.
