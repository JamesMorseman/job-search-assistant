"""CLI entry point: `jsa <command>`"""

import logging

import click
from rich.console import Console
from rich.logging import RichHandler

from job_search.config import settings

console = Console()


def _setup_logging():
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        handlers=[RichHandler(rich_tracebacks=True)],
        format="%(message)s",
    )


@click.group()
def cli():
    """Job Search Assistant — civil engineering pipeline for James."""
    _setup_logging()


@cli.command()
def preflight():
    """Check that every API key, config file, and profile field is ready."""
    from job_search.preflight import run_preflight
    report = run_preflight()

    icon = {True: "[green]✓[/green]", False: "[red]✗[/red]"}
    by_sev = {"required": [], "recommended": [], "optional": []}
    for c in report.checks:
        by_sev.setdefault(c.severity, []).append(c)

    for sev in ("required", "recommended", "optional"):
        if not by_sev[sev]:
            continue
        console.print(f"\n[bold]{sev.title()}[/bold]")
        for c in by_sev[sev]:
            console.print(f"  {icon[c.ok]}  {c.name:32s}  {c.detail}")

    s = report.summary
    console.print(
        f"\n[bold]Result:[/bold] {s['required_ok']}/{s['required_total']} required · "
        f"{s['recommended_ok']}/{s['recommended_total']} recommended"
    )
    if report.all_required_ok:
        console.print("[green]Ready to run.[/green]")
    else:
        console.print("[red]Not ready — fix required items first.[/red]")


@cli.command()
def init_db():
    """Initialize the SQLite database schema."""
    from job_search.db import init_db as _init
    _init()
    console.print("[green]Database initialized.[/green]")


@cli.command()
@click.option("--dry-run", is_flag=True, default=False, help="Fetch but do not write to DB.")
def ingest(dry_run: bool):
    """Run daily job ingestion from all sources."""
    from job_search.ingestion import Ingestor
    ingestor = Ingestor(dry_run=dry_run or settings.DRY_RUN)
    ingestor.load_firms()
    stats = ingestor.run()
    console.print(stats)


@cli.command()
def report():
    """Present today's top-scored postings to the Sheet (no doc generation)."""
    from job_search.reporting import DailyReporter
    reporter = DailyReporter()
    stats = reporter.run()
    console.print(stats)


@cli.command()
@click.option("--timeout", type=int, default=None, help="Max seconds to wait for the batch to finish")
@click.option("--max-jobs", type=int, default=None, help="Cap postings graded this run")
@click.option("--dry-run", is_flag=True, help="Select + build requests; do not submit to the API")
def grade(timeout: int | None, max_jobs: int | None, dry_run: bool):
    """Grade NEW viable postings for fit via the configured LLM provider."""
    from job_search.grading import FitGrader
    grader = FitGrader()
    stats = grader.run(timeout_s=timeout, max_jobs=max_jobs, dry_run=dry_run)
    console.print(stats)


@cli.command(name="sync-sheet")
def sync_sheet():
    """Pull James's status edits from the Sheet into the DB."""
    from job_search.reporting import SelectionProcessor
    proc = SelectionProcessor()
    stats = proc.sync_from_sheet()
    console.print(stats)


@cli.command()
@click.argument("job_ids", nargs=-1)
@click.option("--force", is_flag=True, help="Regenerate even if docs already exist")
def generate(job_ids: tuple[str, ...], force: bool):
    """Generate resume + cover letter for selected jobs (LLM calls).

    With no arguments, generates docs for every job in 'selected' state
    that doesn't already have docs. Pass specific job IDs to target only those.
    """
    from job_search.reporting import SelectionProcessor
    proc = SelectionProcessor()
    stats = proc.generate_for_selected(
        job_ids=list(job_ids) if job_ids else None,
        force=force,
    )
    console.print(
        f"[bold]Generated {stats['generated']} sets of docs[/bold] "
        f"({stats['errors']} errors)"
    )
    for doc in stats["docs"]:
        console.print(
            f"  [green]{doc['title']}[/green] @ {doc['company']}\n"
            f"    Resume: {doc['resume_url']}\n"
            f"    Cover:  {doc['cover_url']}"
        )


@cli.command()
@click.argument("job_id")
def apply(job_id: str):
    """Mark a job as 'selected' and generate docs immediately."""
    from job_search.db import get_db
    from job_search.reporting import SelectionProcessor
    from job_search.tracking import advance_state

    with get_db() as db:
        ok = advance_state(db, job_id, "selected", note="jsa apply CLI")
        if not ok:
            console.print(f"[red]Could not advance {job_id} to 'selected' — invalid transition[/red]")
            return

    proc = SelectionProcessor()
    stats = proc.generate_for_selected(job_ids=[job_id])
    if stats["generated"] > 0:
        doc = stats["docs"][0]
        console.print(f"[green]Docs ready:[/green]\n  Resume: {doc['resume_url']}\n  Cover:  {doc['cover_url']}")
    else:
        console.print("[red]Doc generation failed — see logs[/red]")


@cli.command()
def followup():
    """Surface overdue follow-up actions."""
    from job_search.tracking import FollowUpEngine
    engine = FollowUpEngine()
    actions = engine.run()
    if not actions:
        console.print("[green]No follow-up actions due today.[/green]")
    else:
        for action in actions:
            console.print(f"[yellow]{action['action_type']}[/yellow] — {action['company']} / {action['title']} (due {action['due_date']})")


@cli.command(name="run")
@click.option("--dry-run", is_flag=True, default=False, help="Execute without writing any database records.")
@click.option(
    "--run-type",
    default="full",
    show_default=True,
    help="full | ingest | grade | report | generate | followup",
)
def run_pipeline(dry_run: bool, run_type: str):
    """Run the local pipeline: ingest -> grade -> report -> generate -> follow-up."""
    from job_search.pipeline import PipelineRunner

    result = PipelineRunner().run(run_type=run_type, dry_run=dry_run, trigger="cli")
    console.print(f"[bold]Run type:[/bold] {result.run_type}  [bold]Status:[/bold] {result.status}")
    if result.run_id is not None:
        console.print(f"[bold]Run ID:[/bold] {result.run_id}")
    for step in result.steps:
        color = {"ok": "green", "error": "red", "skipped": "yellow"}[step.status]
        console.print(f"  [{color}]{step.name}: {step.status}[/{color}]")
        if step.error:
            console.print(f"    {step.error}")


@cli.command()
@click.argument("firm_name")
@click.argument("website")
def discover_firm(firm_name: str, website: str):
    """Fingerprint a single firm and add it to the registry."""
    from job_search.discovery import RegistryBuilder
    builder = RegistryBuilder()
    config = builder.fingerprint_firm(firm_name, website)
    if config:
        valid = builder.validate(config)
        console.print(f"ATS: {config.ats_type.value} / Tier: {config.ats_tier.value} / Valid: {valid}")
        if valid:
            builder.upsert_to_config(config)
            console.print(f"[green]{firm_name} added to registry.[/green]")
    else:
        console.print(f"[red]Could not fingerprint {firm_name}[/red]")


@cli.command()
@click.argument("canonical_job_id")
@click.argument("new_state")
@click.option("--note", default=None)
def update_state(canonical_job_id: str, new_state: str, note: str | None):
    """Manually transition a job's application state."""
    from job_search.db import get_db
    from job_search.tracking import advance_state
    with get_db() as db:
        ok = advance_state(db, canonical_job_id, new_state, note)
        if ok:
            console.print(f"[green]{canonical_job_id} → {new_state}[/green]")
        else:
            console.print(f"[red]Invalid transition to '{new_state}' for {canonical_job_id}[/red]")


@cli.command(name="score-location")
@click.argument("city")
@click.option("--state", default=None, help="2-letter state code (helps disambiguate)")
@click.option("--scheme", default=None, help="balanced | fit_first | career_first | career_relax | career_only")
def score_location(city: str, state: str | None, scheme: str | None):
    """Score a single location against the 50-metro framework."""
    from job_search.location import LocationScorer
    s = LocationScorer(scheme=scheme or "balanced")
    result = s.score(city, state)
    console.print(f"\n[bold]Location:[/bold] {city}{', ' + state if state else ''}")
    console.print(f"[bold]Scheme:[/bold] {result.scheme}")
    if result.metro_id:
        console.print(f"[bold]Matched metro:[/bold] {result.metro_name} ({result.metro_id})")
        console.print(f"[bold]Match kind:[/bold] {result.match_kind} (confidence {result.confidence:.2f})")
        d = result.dimensions
        console.print(
            f"[bold]Dimensions[/bold] — CE:{d.ce:.1f} COL:{d.col:.1f} "
            f"Home:{d.home:.1f} MJ:{d.mj:.1f} Dating:{d.dating:.1f}"
        )
    else:
        console.print(f"[yellow]No ranked metro matched[/yellow] (kind={result.match_kind})")
    console.print(f"[bold cyan]Composite:[/bold cyan] {result.composite:.1f}/100  → normalized {result.normalized:.3f}")


@cli.command()
def stats():
    """Print funnel statistics: where applications are, which sources convert."""
    from rich.table import Table

    from job_search.reporting.funnel import FUNNEL_STAGES, FunnelReporter

    stats = FunnelReporter().compute()
    console.print(f"\n[bold]Total jobs in DB:[/bold] {stats.total_jobs}\n")

    # ── Funnel ─────────────────────────────────────────────────────────────
    console.print("[bold]Funnel (current state)[/bold]")
    t = Table(show_header=True, header_style="bold")
    t.add_column("State")
    t.add_column("Count", justify="right")
    t.add_column("Avg match", justify="right")
    for stage in FUNNEL_STAGES + ["rejected", "ghosted"]:
        n = stats.by_state.get(stage, 0)
        if n == 0:
            continue
        avg = stats.avg_match_by_state.get(stage, 0)
        t.add_row(stage, str(n), f"{avg:.3f}")
    console.print(t)

    # ── By source ──────────────────────────────────────────────────────────
    if stats.by_source:
        console.print("\n[bold]By source[/bold]")
        t = Table(show_header=True, header_style="bold")
        t.add_column("Source")
        for col in ("discovered", "presented", "selected", "applied", "rejected"):
            t.add_column(col, justify="right")
        for src, states in sorted(stats.by_source.items()):
            t.add_row(src, *(str(states.get(c, 0)) for c in ("discovered", "presented", "selected", "applied", "rejected")))
        console.print(t)

    # ── Response rates ─────────────────────────────────────────────────────
    if stats.response_rate_by_source:
        console.print("\n[bold]Response rates by source[/bold] (applied → got any response)")
        t = Table(show_header=True, header_style="bold")
        t.add_column("Source")
        t.add_column("Applied", justify="right")
        t.add_column("Responded", justify="right")
        t.add_column("Response %", justify="right")
        t.add_column("Screen %", justify="right")
        t.add_column("Interview %", justify="right")
        for src, r in sorted(stats.response_rate_by_source.items(),
                              key=lambda kv: -kv[1]["response_rate"]):
            t.add_row(
                src,
                str(r["applied"]),
                str(r["responded"]),
                f"{r['response_rate']:.1%}",
                f"{r['screen_rate']:.1%}",
                f"{r['interview_rate']:.1%}",
            )
        console.print(t)

    # ── Stretch breakdown ──────────────────────────────────────────────────
    if stats.by_stretch:
        console.print("\n[bold]Stretch category × outcome[/bold]")
        t = Table(show_header=True, header_style="bold")
        t.add_column("Stretch")
        for col in ("presented", "selected", "applied", "rejected", "ghosted"):
            t.add_column(col, justify="right")
        for stretch, states in sorted(stats.by_stretch.items()):
            t.add_row(stretch, *(str(states.get(c, 0)) for c in ("presented", "selected", "applied", "rejected", "ghosted")))
        console.print(t)

    # ── Median timing ──────────────────────────────────────────────────────
    if any(v is not None for v in stats.median_days.values()):
        console.print("\n[bold]Median days (state transition)[/bold]")
        for label, days in stats.median_days.items():
            if days is not None:
                console.print(f"  {label:25s} {days:.1f} days")


# ── Firm repository commands ───────────────────────────────────────────────────

@cli.group()
def firms():
    """Firm intelligence repository — discover, draft, review, and approve firm profiles."""
    pass


@firms.command(name="discover")
@click.option("--min-jobs", default=1, show_default=True, type=int, help="Minimum job count to surface a candidate.")
@click.option("--source", default=None, metavar="SOURCE", help="Filter candidates by ingestion source name.")
@click.option("--out", default=None, type=click.Path(), help="Write TSV output to this file path.")
@click.option("--config", "config_path", default="config/firms.yaml", show_default=True, help="Path to approved firms YAML.")
def firms_discover(min_jobs: int, source: str | None, out: str | None, config_path: str):
    """List companies in the job DB that do not have an approved firm profile.

    \b
    NOTE — Alias limitation (MVP):
    Comparison is against approved firm_id slugs only. Firms already approved
    under a different name or alias may still appear as candidates. Alias-aware
    filtering is planned for a later step.
    """
    from pathlib import Path as _Path

    from job_search.firms.discovery import discover_missing_firms

    candidates = discover_missing_firms(
        min_jobs=min_jobs,
        source_filter=source,
        config_path=config_path,
    )

    if not candidates:
        console.print("[green]No missing firms found — all discovered companies match an approved profile.[/green]")
        return

    from rich.table import Table
    t = Table(
        show_header=True,
        header_style="bold",
        title=f"Missing firm candidates ({len(candidates)})",
    )
    t.add_column("Company", no_wrap=True)
    t.add_column("Suggested firm_id")
    t.add_column("Jobs", justify="right")
    t.add_column("Sources")
    t.add_column("Sample URL", max_width=60)

    tsv_rows = ["company\tsuggested_firm_id\tjob_count\tsources\tsample_url"]
    for c in candidates:
        sample_url = c.sample_urls[0] if c.sample_urls else ""
        sources_str = ", ".join(c.sources)
        t.add_row(c.company, c.suggested_firm_id, str(c.job_count), sources_str, sample_url)
        tsv_rows.append(f"{c.company}\t{c.suggested_firm_id}\t{c.job_count}\t{sources_str}\t{sample_url}")

    console.print(t)
    console.print(
        "\n[dim]Alias limitation (MVP): comparison is against approved firm_id slugs only. "
        "Use [bold]jsa firms draft <firm_id>[/bold] to generate a draft profile.[/dim]"
    )

    if out:
        _Path(out).write_text("\n".join(tsv_rows), encoding="utf-8")
        console.print(f"[green]Wrote {len(candidates)} candidates to {out}[/green]")


@firms.command(name="review")
@click.argument("firm_id", required=False, default=None)
@click.option("--drafts-dir", default=None, type=click.Path(), help="Override default draft directory.")
@click.option("--all-statuses", is_flag=True, default=False, help="Show all drafts, not just pending_review.")
def firms_review(firm_id: str | None, drafts_dir: str | None, all_statuses: bool):
    """Review pending draft firm profiles.

    \b
    Without FIRM_ID: lists all pending drafts (or all drafts with --all-statuses).
    With FIRM_ID:    shows a detailed panel for that draft.
    """
    from pathlib import Path as _Path
    from rich.table import Table
    from rich.panel import Panel

    from job_search.firms.repository import (
        DraftNotFoundError,
        list_drafts,
        read_draft,
    )
    from job_search.models import DraftStatus

    if firm_id:
        # ── Single-firm detail view ─────────────────────────────────────────
        try:
            draft = read_draft(firm_id, drafts_dir=drafts_dir)
        except DraftNotFoundError as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise SystemExit(1)

        status_color = {
            "pending_review": "yellow",
            "rejected": "red",
            "approved": "green",
        }.get(draft.draft_status.value, "white")

        lines = [
            f"[bold]firm_id:[/bold]     {draft.firm_id}",
            f"[bold]name:[/bold]        {draft.name}",
            f"[bold]status:[/bold]      [{status_color}]{draft.draft_status.value}[/{status_color}]",
            f"[bold]generated_at:[/bold] {draft.generated_at or '—'}",
            f"[bold]website:[/bold]     {draft.website or '—'}",
            f"[bold]careers_url:[/bold] {draft.careers_url or '—'}",
            f"[bold]aliases:[/bold]     {', '.join(draft.aliases) or '—'}",
            f"[bold]priority:[/bold]    {draft.manual_priority.value}",
        ]

        if draft.profile.enr_rank or draft.profile.employee_count or draft.profile.disciplines:
            lines += [
                "",
                "[bold]Profile[/bold]",
                f"  enr_rank:      {draft.profile.enr_rank or '—'}",
                f"  employee_count:{draft.profile.employee_count or '—'}",
                f"  disciplines:   {', '.join(draft.profile.disciplines) or '—'}",
                f"  markets:       {', '.join(draft.profile.markets) or '—'}",
            ]

        if draft.benefits:
            lines += ["", "[bold]Benefits[/bold]"]
            for key, b in draft.benefits.items():
                lines.append(
                    f"  {key:<35s} {b.status.value:<12s} conf={b.confidence:.2f}"
                    + (f"  [{b.source_type.value}]" if b.source_url else "")
                )

        if draft.trajectory:
            lines += ["", "[bold]Career Trajectory[/bold]"]
            for key, t in draft.trajectory.items():
                lines.append(
                    f"  {key:<35s} {t.status.value:<12s} conf={t.confidence:.2f}"
                    + (f"  rating={t.rating}" if t.rating else "")
                )

        if draft.evidence_summary.source_urls:
            lines += ["", "[bold]Evidence URLs[/bold]"]
            for url in draft.evidence_summary.source_urls:
                lines.append(f"  {url}")

        if draft.evidence_summary.extraction_notes:
            lines += ["", "[bold]Extraction Notes[/bold]"]
            for note in draft.evidence_summary.extraction_notes:
                lines.append(f"  • {note}")

        if draft.notes.reputation:
            lines += ["", f"[bold]Reputation:[/bold] {draft.notes.reputation}"]

        if draft.review.reviewer_notes:
            lines += ["", "[bold]Reviewer Notes[/bold]"]
            for note in draft.review.reviewer_notes:
                lines.append(f"  • {note}")

        console.print(Panel("\n".join(lines), title=f"Draft Review — {firm_id}", expand=False))
        console.print(
            "\n[dim]To approve:  [bold]jsa firms approve "
            + firm_id
            + " --approved-by <name>[/bold][/dim]"
        )
        console.print(
            f"[dim]To reject:   [bold]jsa firms reject {firm_id}[/bold][/dim]"
        )
        return

    # ── List view ──────────────────────────────────────────────────────────
    all_ids = list_drafts(drafts_dir=drafts_dir)
    if not all_ids:
        console.print("[green]No draft firm profiles found.[/green]")
        return

    rows = []
    for fid in all_ids:
        try:
            d = read_draft(fid, drafts_dir=drafts_dir)
        except Exception:
            continue
        if not all_statuses and d.draft_status.value != "pending_review":
            continue
        rows.append(d)

    if not rows:
        console.print("[green]No pending draft firm profiles. Use --all-statuses to see all.[/green]")
        return

    t = Table(show_header=True, header_style="bold", title=f"Draft Firm Profiles ({len(rows)})")
    t.add_column("firm_id", no_wrap=True)
    t.add_column("Name")
    t.add_column("Status")
    t.add_column("Benefits")
    t.add_column("Trajectory")
    t.add_column("Generated")

    status_color = {"pending_review": "yellow", "rejected": "red", "approved": "green"}
    for d in rows:
        sc = status_color.get(d.draft_status.value, "white")
        t.add_row(
            d.firm_id,
            d.name,
            f"[{sc}]{d.draft_status.value}[/{sc}]",
            str(len(d.benefits)),
            str(len(d.trajectory)),
            d.generated_at or "—",
        )

    console.print(t)
    console.print(
        "\n[dim]Run [bold]jsa firms review <firm_id>[/bold] for a detailed view, "
        "or [bold]jsa firms approve <firm_id>[/bold] to promote.[/dim]"
    )


@firms.command(name="approve")
@click.argument("firm_id")
@click.option("--approved-by", required=True, prompt="Approved by", help="Name or identifier of the approver.")
@click.option("--last-verified", default=None, help="ISO date of last manual verification (defaults to today).")
@click.option("--drafts-dir", default=None, type=click.Path(), help="Override default draft directory.")
@click.option("--config", "config_path", default="config/firms.yaml", show_default=True, help="Path to approved firms YAML.")
def firms_approve(firm_id: str, approved_by: str, last_verified: str | None,
                  drafts_dir: str | None, config_path: str):
    """Approve a pending draft and promote it to config/firms.yaml.

    \b
    The draft is validated, converted to an approved FirmProfile, written into
    config/firms.yaml, and synced to SQLite.  The draft file is preserved with
    status 'approved' for audit purposes.
    """
    from job_search.db.connection import get_db
    from job_search.firms.repository import (
        DraftNotFoundError,
        DraftStatusError,
        approve_draft,
    )

    try:
        with get_db() as db:
            profile = approve_draft(
                firm_id,
                approved_by=approved_by,
                last_verified=last_verified,
                drafts_dir=drafts_dir,
                config_path=config_path,
                db=db,
            )
    except DraftNotFoundError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise SystemExit(1)
    except DraftStatusError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise SystemExit(1)
    except ValueError as exc:
        console.print(f"[red]Validation error:[/red] {exc}")
        raise SystemExit(1)

    console.print(
        f"[green]✓ {profile.name} ({firm_id}) approved by {approved_by}.[/green]\n"
        f"  Written to [bold]{config_path}[/bold] and synced to SQLite."
    )


@firms.command(name="reject")
@click.argument("firm_id")
@click.option("--notes", default="", help="Reviewer notes to record on the draft.")
@click.option("--drafts-dir", default=None, type=click.Path(), help="Override default draft directory.")
def firms_reject(firm_id: str, notes: str, drafts_dir: str | None):
    """Reject a pending draft firm profile.

    \b
    The draft YAML is preserved with status 'rejected' and the notes recorded.
    Evidence is never deleted.  A rejected draft can be re-reviewed or deleted
    manually.
    """
    from job_search.firms.repository import (
        DraftNotFoundError,
        DraftStatusError,
        reject_draft,
    )

    try:
        draft = reject_draft(firm_id, reviewer_notes=notes, drafts_dir=drafts_dir)
    except DraftNotFoundError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise SystemExit(1)
    except DraftStatusError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise SystemExit(1)

    console.print(
        f"[yellow]✗ {draft.name} ({firm_id}) marked as rejected.[/yellow]\n"
        "  Draft preserved with evidence intact."
    )


@firms.command(name="draft")
@click.argument("company_name")
@click.option("--firm-id", default=None, metavar="SLUG",
              help="Override the auto-generated firm_id slug.")
@click.option("--website", default=None, help="Company website URL.")
@click.option("--careers-url", default=None, help="Direct careers/jobs page URL.")
@click.option("--force", is_flag=True, default=False,
              help="Overwrite an existing draft for the same firm_id.")
@click.option("--drafts-dir", default=None, type=click.Path(),
              help="Override default draft directory (data/firm_drafts/).")
def firms_draft(company_name: str, firm_id: str | None, website: str | None,
                careers_url: str | None, force: bool, drafts_dir: str | None):
    """Generate a skeleton draft firm profile for COMPANY_NAME.

    \b
    Creates data/firm_drafts/<firm_id>.yaml with status pending_review.
    Benefits and trajectory are left empty for manual or LLM-assisted fill-in.
    Use --firm-id to override the auto-generated slug.
    Use --force to overwrite an existing draft for the same firm.

    \b
    Next steps:
      jsa firms review <firm_id>    — inspect the draft
      jsa firms approve <firm_id>   — promote to config/firms.yaml
    """
    from job_search.firms.repository import (
        DraftExistsError,
        _company_to_firm_id,
        create_draft,
    )

    # Show the slug that will be used before any I/O so the user can abort.
    resolved_id = firm_id or _company_to_firm_id(company_name)

    try:
        draft, path = create_draft(
            company_name,
            firm_id=firm_id,
            website=website,
            careers_url=careers_url,
            drafts_dir=drafts_dir,
            force=force,
        )
    except DraftExistsError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise SystemExit(1)
    except ValueError as exc:
        console.print(f"[red]Validation error:[/red] {exc}")
        raise SystemExit(1)

    console.print(
        f"[green]✓ Skeleton draft created:[/green] [bold]{draft.firm_id}[/bold] → {path}\n"
        f"  Name:      {draft.name}\n"
        f"  Generated: {draft.generated_at}\n"
        f"  Status:    {draft.draft_status.value}"
    )
    if website or careers_url:
        console.print(
            f"  Website:   {draft.website or '—'}\n"
            f"  Careers:   {draft.careers_url or '—'}"
        )
    console.print(
        f"\n[dim]Review with: [bold]jsa firms review {draft.firm_id}[/bold][/dim]"
    )
