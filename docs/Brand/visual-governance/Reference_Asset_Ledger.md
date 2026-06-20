# Reference Asset Ledger

## Purpose

Track authoritative visual reference assets - status, ownership, scope, known conflicts,
and retirement - so future packages stop re-discovering or re-litigating which reference
images are canonical. See `VISUAL_GOVERNANCE_V1.md` for governing direction.

This ledger does not duplicate the hash-level Radar/SignalCard reference verification
already performed in `docs/Brand/Radar_Reference_Annotation_Ledger.md` Section 1 - it
points to that ledger for Radar-specific assets and covers the wider asset set named
across the supplied governance/research sources.

## Entry Template

```text
Filename:
Type:            workspace reference | object reference | composite reference
Status:          accepted | candidate | draft | superseded | conflicted
Owner:
Known conflicts:
Retirement condition:
Notes:
```

## Ledger

| Filename | Type | Status | Owner | Known conflicts | Notes |
|---|---|---|---|---|---|
| `artifacts/png/workspaces/Radar Workspace Reference v1.png` (REF-RADAR-A, committed) | workspace reference | accepted | Sara | none (see Known Resolved Item below) | Hash-verified in `Radar_Reference_Annotation_Ledger.md` Section 1; primary Radar authority |
| `Reference Images/Radar Reference.png` (REF-RADAR-B, local-only/untracked) | workspace reference | candidate | Sara | none | Secondary copy, same composition as REF-RADAR-A per P7P5I; not independently committed |
| `artifacts/png/objects/Opportunity Signal Card v1.png` (REF-CARD-A, committed) | object reference | accepted | Sara | none | Hash-verified in `Radar_Reference_Annotation_Ledger.md` Section 1; primary SignalCard authority |
| `Reference Images/Opportunity Singal Card Refernce.png` (local-only/untracked) | object reference | candidate | Sara | on-disk filename typo ("Singal"/"Refernce") | Secondary local copy; do not "fix" the on-disk filename in this package |
| `Pipeline Reference.png` / `artifacts/png/workspaces/Pipeline Workspace Reference v1.png` (committed) | workspace reference | candidate | Sara | previously suspected (incorrectly) to duplicate the Radar reference | No full Pipeline surface spec exists yet - see Open Gaps below |
| `artifacts/png/workspaces/Command Center Workspace Reference v1.png` (committed) | workspace reference | candidate | Sara | none known | No Command Center surface spec exists yet - see Open Gaps below |
| `artifacts/png/workspaces/Opportunity Detail Surface v1.png` (committed) | workspace reference | candidate | Sara | none known | Surface reference draft exists (`ATLAS_Opportunity_Detail_Surface_v1_Visual_Reference.md`) |
| `artifacts/png/workspaces/Ask Atlas Workspace v1.png` (committed) | workspace reference | candidate | Sara | none known | Surface reference draft exists (`ATLAS_Ask_Atlas_Workspace_v1_Visual_Reference.md`) |
| `artifacts/png/objects/Recommendation Card v1.png` (committed) | object reference | candidate | Sara | local-only copy filename typo ("Recomendation"/"Refernce") | Production-candidate draft exists (`ATLAS Recommendation Card v1.0 Production Candidate..md`) |
| `Reference Image suite.png` (local-only/untracked) | composite reference | candidate | Sara | none known | Overview only; not a substitute for per-surface references |

## Known Resolved Item

The Deep Research Knowledge Base (`deep-research-report (7).md`,
`visual_spec_gap_audit.duplicate_assets`) flagged: "Radar Reference.png and Pipeline
Reference.png appear identical (possibly misfiled)." **This is resolved and closed.**
P7P5I (2026-06-19) computed SHA256 hashes for both images and confirmed they are
distinct files. See `docs/Brand/Radar_Reference_Annotation_Ledger.md` Section 1 for the
hash values. Do not re-open this as a gap in future packages.

## Open Gaps (carried forward from Deep Research Knowledge Base gap audit, normalization: CANDIDATE)

```text
Command Center: workspace spec gap (ActionQueue, SystemHealth, ContextTips modules undefined)
Pipeline: full surface spec gap (overview layout undefined)
Sidebar/navigation: no final approved spec
Run Sweep / Scan: no object reference image or detailed spec (future feature)
```

These are carried forward as CANDIDATE/open per the Deep Research Knowledge Base; they
are not validated against repo state in this package and require their own spec package
before being treated as governance.

## Asset Handling Rules

```text
Reference images remain local-only / uncommitted in this package unless already
  committed elsewhere in the repo (Radar and SignalCard references are already
  committed under artifacts/png/ per P7P5I - this ledger does not change that).
This package adds no new image assets.
This package does not rename, move, or "correct" any on-disk reference filename.
```
