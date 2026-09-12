# Thea / Audit

Audit records the co-project's git flow, data-flow checks, sync observations,
and verification results. It is the witness project, not a second source of
truth.

## Write boundary

- `checks/` contains executable checks and their small reports.
- `runs/` contains dated audit outputs with the commit they inspected.
- `manifests/` contains SHA-256 pins and source metadata.
- Audit may report another project; it does not edit that project's files.

## First run

Run the root audit command and record its output with the inspected workspace
state and the machine presence records.