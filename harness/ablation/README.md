# Ablation scripts

Per-claim apply/undo scripts used for **non-asset** ablations (a single tag, a comment substring, a single SQL line — anything that can't be turned off via permission flips alone).

## Layout

```
ablation/
  T-XXX/
    D-3/
      apply.sh           # mutate the workspace
      undo.sh            # restore the workspace
      manifest.yaml      # what was changed; used by QA to diff
    A-2/
      apply.sh
      undo.sh
      manifest.yaml
```

## QA contract

For every pair, QA runs:
1. `apply.sh` → capture state hash of affected assets
2. `undo.sh`  → capture state hash of affected assets
3. Assert post-`undo` hash equals pre-`apply` hash.

A failing pair must be fixed before the claim can be verified.

## Asset-level ablations

When the claim is a whole asset, no scripts are needed — the harness flips workspace permissions to hide the asset from the eval principal.
