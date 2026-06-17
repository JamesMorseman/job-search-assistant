# <a name="atlas-desktop-architecture-study"></a>ATLAS Desktop Architecture Study
## <a name="executive-summary"></a>1. Executive Summary
ATLAS should evolve into a local-first desktop application by preserving the current system as the core engine and wrapping it with a desktop shell.

The recommended direction is:

**Tauri-first desktop architecture**

Electron should remain a fallback option only if Tauri blocks required functionality.

The current dashboard MVP should not be discarded. It should become the desktop UI surface. The long-term architecture should separate:

- ATLAS core engine
- local API/service layer
- desktop shell
- dashboard UI
- optional cloud services
- future Ask Atlas conversational layer

The desktop application should not become cloud-dependent. Cloud features should be additive, not foundational.

-----
## <a name="current-architecture-assumption"></a>2. Current Architecture Assumption
ATLAS currently consists of:

- ingestion
- scoring
- generation
- tracking
- analytics
- dashboard

The dashboard MVP is complete.

This means the project already has the correct intermediate architecture for desktop evolution: a browser-based interface backed by local application logic.

The next architectural transition is not a rebuild. It is a packaging and boundary-definition problem.

-----
## <a name="local-first-architecture"></a>3. Local-First Architecture
ATLAS should remain local-first.

The local machine should own:

- job database
- firm repository
- application tracking
- generated documents
- analytics history
- dashboard state
- user profile data
- audit outputs
- scoring records

Cloud should be optional for:

- backup
- sync
- external model calls
- remote access
- shared analytics
- multi-device continuity

The default model should be:

Local desktop app\
`  `-> local ATLAS service\
`  `-> local database/files\
`  `-> optional external APIs

This preserves the core identity of ATLAS as a personal career intelligence system rather than a SaaS product.

-----
## <a name="recommended-desktop-shape"></a>4. Recommended Desktop Shape
The preferred architecture is:

Tauri Shell\
`  `-> bundled dashboard UI\
`  `-> local API bridge\
`  `-> ATLAS Python backend/service\
`  `-> SQLite / local files / generated artifacts

The desktop shell should be thin.

The intelligence should remain in the existing ATLAS backend.

The UI should remain portable enough that it can still run as a normal web dashboard during development.

This avoids trapping the product inside a desktop-only framework too early.

-----
## <a name="tauri-suitability"></a>5. Tauri Suitability
Tauri is the better architectural fit for ATLAS.

Strengths:

- lightweight desktop packaging
- good fit for local-first tools
- smaller application footprint than Electron
- strong security posture
- native OS integration
- works well when the frontend is already web-based
- avoids bundling a full Chromium runtime
- aligns with a serious utility/productivity application

Tauri is especially suitable because ATLAS does not need to be a heavy web platform. It needs to feel like a focused local control center.

Risks:

- Rust boundary may add complexity
- Python backend integration needs deliberate design
- fewer examples than Electron for some desktop workflows
- packaging Python plus Tauri may require careful release discipline
- local process management must be designed cleanly

Assessment:

**Tauri is suitable and should be the preferred direction.**

-----
## <a name="electron-suitability"></a>6. Electron Suitability
Electron is viable but less aligned.

Strengths:

- mature ecosystem
- large developer base
- strong desktop-app precedent
- easier all-JavaScript workflow
- many examples for tray apps, notifications, auto-update, packaging, and IPC
- lower conceptual barrier if the dashboard stack is already JavaScript-heavy

Weaknesses:

- heavier runtime
- larger app size
- higher memory footprint
- weaker fit for a lean local-first utility
- more security responsibility around renderer/main process boundaries
- can make ATLAS feel like a wrapped website rather than a native intelligence tool

Assessment:

**Electron is acceptable but should be treated as the fallback, not the default.**

Electron becomes preferable only if Tauri creates blocking issues around packaging, Python orchestration, notifications, updates, or OS integrations.

-----
## <a name="update-strategy"></a>7. Update Strategy
The update strategy should match the local-first model.

Recommended update tiers:

1. Manual update during internal/private use
1. Signed release packages for stable desktop builds
1. Optional in-app updater once releases become regular
1. Optional cloud-backed update channel if ATLAS becomes public or commercial

Updates must avoid corrupting local user data.

The application should separate:

- application binaries
- local database
- generated documents
- user config
- model/cache data
- logs

Database migrations should be versioned and reversible where practical.

The update system should never assume that cloud sync exists.

-----
## <a name="local-ai-integration-options"></a>8. Local AI Integration Options
ATLAS should support multiple AI execution modes.

Recommended model:

AI Provider Interface\
`  `-> OpenAI / cloud provider\
`  `-> local LLM provider\
`  `-> disabled/manual mode

Local AI should be optional, not mandatory.

Potential local AI uses:

- summarizing job descriptions
- extracting requirements
- ranking opportunities
- Ask Atlas Q&A over local data
- drafting application notes
- explaining score changes
- generating follow-up suggestions

Risks:

- local models may be slower
- quality may vary
- hardware requirements may confuse users
- model storage can become large
- privacy benefits do not automatically mean better output quality

Recommendation:

Keep the AI provider abstraction independent from the desktop shell.

The desktop app should not care whether intelligence comes from OpenAI, a local model, or deterministic scoring.

-----
## <a name="notification-architecture"></a>9. Notification Architecture
Notifications should be local-first and event-driven.

Notification sources:

- new high-quality opportunity found
- application follow-up due
- saved job changed status
- firm priority changed
- dashboard needs review
- generation failed
- ingestion failed
- weekly analytics summary ready
- Ask Atlas has a recommendation

Recommended notification model:

ATLAS event\
`  `-> local event queue\
`  `-> notification policy\
`  `-> desktop notification\
`  `-> dashboard record

Notifications should be auditable. Every notification should correspond to a record in the dashboard or event log.

The system should avoid noisy notifications. ATLAS should notify only when there is a meaningful state change.

-----
## <a name="dashboard-to-desktop-transition"></a>10. Dashboard-to-Desktop Transition
The existing dashboard should become the primary desktop surface.

Do not replace the dashboard with a separate native UI.

Recommended evolution:

Current dashboard MVP\
`  `-> packaged inside desktop shell\
`  `-> local service startup/shutdown handled by shell\
`  `-> desktop navigation added gradually\
`  `-> tray/menu/notifications added later

The dashboard should retain browser compatibility during development.

This preserves velocity and prevents the desktop transition from becoming a rewrite.

-----
## <a name="offline-capability"></a>11. Offline Capability
ATLAS should function meaningfully offline.

Offline-capable features:

- view saved jobs
- view firm repository
- view application tracker
- view analytics history
- review generated resumes/letters
- inspect scoring explanations
- update manual statuses
- use local Ask Atlas if local AI is configured

Online-required features:

- new job ingestion
- external API enrichment
- cloud model calls
- email/Drive/Sheets integrations
- external sync
- remote update checks

The UI should clearly distinguish between unavailable online features and broken local features.

Offline mode should be treated as a first-class state, not an error condition.

-----
## <a name="future-ask-atlas-integration"></a>12. Future Ask Atlas Integration
Ask Atlas should not be bolted directly onto the UI.

It should sit above the same local data and event architecture used by the dashboard.

Recommended conceptual model:

Ask Atlas\
`  `-> query router\
`  `-> local data access layer\
`  `-> scoring/explanation layer\
`  `-> AI provider interface\
`  `-> response/audit log

Ask Atlas should be able to answer:

- What changed?
- What should I apply to next?
- Which firms matter most?
- Why did this job score highly?
- What follow-ups are due?
- What is the best next action?
- Which resume evidence should be emphasized?

Ask Atlas should not become an uncontrolled chatbot. It should be constrained by ATLAS data, scoring logic, and auditability.

-----
## <a name="architectural-risks"></a>13. Architectural Risks
### <a name="risk-1-desktop-rewrite-spiral"></a>Risk 1: Desktop rewrite spiral
The largest risk is treating desktop as a rebuild.

Mitigation:

Preserve dashboard and backend boundaries.
### <a name="risk-2-python-packaging-complexity"></a>Risk 2: Python packaging complexity
ATLAS likely has meaningful Python logic. Packaging that cleanly with a desktop shell may become non-trivial.

Mitigation:

Keep backend service boundaries explicit.
### <a name="risk-3-local-data-corruption"></a>Risk 3: Local data corruption
Desktop updates can damage user data if storage is not isolated.

Mitigation:

Separate app files from user data and version migrations carefully.
### <a name="risk-4-notification-noise"></a>Risk 4: Notification noise
Too many notifications would weaken the product.

Mitigation:

Use event severity and user-configurable notification policy.
### <a name="risk-5-ask-atlas-overreach"></a>Risk 5: Ask Atlas overreach
Conversational UI can create false confidence.

Mitigation:

Ground Ask Atlas in local data, citations, score explanations, and auditable records.
### <a name="risk-6-cloud-creep"></a>Risk 6: Cloud creep
Convenient cloud features could slowly make ATLAS dependent on external services.

Mitigation:

Make cloud optional by architecture, not just by preference.

-----
## <a name="recommendation"></a>14. Recommendation
ATLAS should proceed toward a Tauri-based desktop application with the current dashboard as the UI foundation and the existing ATLAS backend preserved as the intelligence engine.

The recommended long-term architecture is:

Local-first ATLAS core\
`  `+ dashboard UI\
`  `+ Tauri desktop shell\
`  `+ local database/files\
`  `+ optional AI providers\
`  `+ optional cloud integrations\
`  `+ future Ask Atlas layer

Electron should remain a contingency option.

The desktop transition should be framed as product containment and operating-system integration, not as a new product rebuild.

-----
## <a name="final-position"></a>15. Final Position
ATLAS is architecturally ready to move toward desktop if the project preserves its current separation of concerns.

The correct path is:

**dashboard becomes desktop surface, backend remains core engine, Tauri becomes shell, cloud remains optional, Ask Atlas becomes an auditable intelligence layer.**
