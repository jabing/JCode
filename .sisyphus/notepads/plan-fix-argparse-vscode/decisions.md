# Decisions
- Adopt long flag rename: --global-config with dest=global_config to avoid Python reserved keyword conflicts while preserving -g shorthand.
- Keep -g alias intact to avoid breaking existing scripts; update internal references to use global_config for logic checks.
