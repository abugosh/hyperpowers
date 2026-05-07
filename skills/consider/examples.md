# Consider Examples

Worked conversation examples for the consider skill. Read these only when you need a concrete reference — the SKILL.md file has the full process.

<examples>

<example>
<scenario>User explores a caching idea — Claude investigates, shares findings, user commits to building</scenario>

<conversation>
User: "I'm thinking about adding some kind of caching layer but I'm not sure if it's worth it."

Consider: Dispatches codebase-investigator to understand current data access patterns, API response paths, and any existing caching.

Consider: "I looked at the dashboard API. The main endpoint hits `StatsRepository.get_dashboard_data()` which runs 4 separate queries against the stats tables — no caching anywhere in the path. The queries aggregate over time windows so the data only changes every few minutes, but you're paying the full query cost on every request. Given the read-heavy pattern here, a cache with even a 60-second TTL would eliminate most of the redundant work."

Consider (via AskUserQuestion): "Do you know roughly how many concurrent users hit the dashboard? That determines whether this is 'nice to have' or 'your DB is doing 100x the work it needs to.'"

User: "Maybe 50-100 at peak. Yeah, let's add Redis for that endpoint."

Consider: "Sounds like you're ready to build — want to run /hyperpowers:brainstorm?"
</conversation>
</example>

<example>
<scenario>User explores refactoring — Claude investigates and helps conclude it isn't worth doing</scenario>

<conversation>
User: "Should we refactor the auth module?"

Consider: Dispatches codebase-investigator to examine the auth module structure, recent change frequency, and any pain points visible in the code.

Consider: "I looked at the auth module. It's about 400 lines across 3 files. The structure is a bit sprawling — `authenticate()`, `authorize()`, and session management are all in one file — but git log shows it's only been touched twice in the last 3 months, both minor fixes. No test failures related to it. It's not pretty, but it's stable and low-churn."

Consider (via AskUserQuestion): "Is something specific making you want to refactor it, or is it more of a 'this bothers me when I read it' feeling?"

User: "Just bothers me when I read it. Nothing is actually broken."

Consider: "I'd leave it. The code is stable, rarely touched, and not blocking anything. Refactoring low-churn code that works is almost never worth the risk, especially before a release. If it starts causing real friction — bugs, slow feature work, onboarding confusion — that's when it earns a rewrite."
</conversation>

The session ends without a handoff. Clean exit with a clear opinion.
</example>

<example>
<scenario>User's uncertainty reveals structural friction — Claude investigates and routes to /intuition</scenario>

<conversation>
User: "I want to add rate limiting but I can't figure out where it should live."

Consider: Dispatches codebase-investigator to examine the API gateway layer, service layer, and how auth context flows between them.

Consider: "I looked at both candidate locations. The API gateway is a thin proxy — it has access to the request but not auth context. Getting per-user limits there would mean either duplicating the auth lookup or passing user context through headers, which adds coupling. The service layer already has auth context, but `ServiceBase` is already doing business logic, validation, and error handling — rate limiting there would be a fourth concern in an already-busy class. Neither placement is clean, which suggests this isn't a 'where do I put it' problem — it's a design problem."

Consider (via AskUserQuestion): "Both placements create coupling that doesn't exist yet. Does the rate limiting need per-user awareness, or could it be IP-based at the gateway?"

User: "It needs to be per-user. Some users have higher limits."

Consider: "That confirms it — the rate limiting needs auth context, but the layer that has auth context is already overloaded. This is structural friction. The real question is whether rate limiting deserves its own layer or whether the service layer needs to be decomposed so adding concerns doesn't make things worse. Want to run /hyperpowers:intuition to examine this properly?"
</conversation>
</example>

</examples>
