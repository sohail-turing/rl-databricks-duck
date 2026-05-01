# Ablation

This folder is reserved for future apply/undo scripts used in full statistical claim verification.

## Current milestone status

The first 10-task milestone still uses manual anchors and distractors.

That means this folder is currently a placeholder, not an active part of the delivery path.

## Expected later layout

```text
ablation/
  T-XXX/
    D-3/
      apply.sh
      undo.sh
      manifest.yaml
    A-2/
      apply.sh
      undo.sh
      manifest.yaml
```

## Later QA contract

When the full ablation flow is active, each pair should:

1. apply a reversible change
2. record what changed in `manifest.yaml`
3. restore the workspace cleanly on `undo.sh`

For now, keep this folder empty unless the team explicitly starts the later verification phase.
