# Consider Examples

Worked conversation examples for the consider skill. Read these only when you need a concrete reference — the SKILL.md file has the full process.

<examples>

<example>
<scenario>User explores a caching idea and commits to building</scenario>

<conversation>
User: "I'm thinking about adding some kind of caching layer but I'm not sure if it's worth it."

Consider (via AskUserQuestion): "What problem are you trying to solve with caching?"

User: "API response times — users complain about the dashboard being slow."

Consider (via AskUserQuestion): "How volatile is the data on the dashboard? Does it change per request or could it be stale for a few seconds?"

User: "Most of it is aggregated stats that only update every few minutes."

Consider (via AskUserQuestion): "Is the slowness from the query itself, or from downstream services the API calls?"

User: "The main query hits several tables. I've seen 800ms responses."

Consider (via AskUserQuestion): "Do you have a sense of how many users hit the dashboard concurrently?"

User: "Maybe 50-100 at peak. Okay I think I want to add a Redis cache for the dashboard endpoint."

Consider: "Sounds like you're ready to build — want to run /hyperpowers:brainstorm?"
</conversation>
</example>

<example>
<scenario>User explores refactoring and concludes it isn't worth doing</scenario>

<conversation>
User: "Should we refactor the auth module?"

Consider (via AskUserQuestion): "What would change if you did?"

User: "Mostly cleaner code. The current structure is a bit hard to follow."

Consider (via AskUserQuestion): "Is the difficulty causing actual problems — bugs, slow feature work, onboarding friction?"

User: "Not really. It's just not pretty."

Consider (via AskUserQuestion): "What's the cost of not refactoring right now?"

User: "Nothing is broken. The team is tight on time before the release."

Consider: "You explored refactoring auth — the value is cleanup, but nothing is broken and timing is poor. Status quo is acceptable. Let me know if the friction becomes a real problem."
</conversation>

The session ends without a handoff. Clean exit.
</example>

<example>
<scenario>User's uncertainty reveals structural friction — routed to /intuition</scenario>

<conversation>
User: "I want to add rate limiting but I can't figure out where it should live."

Consider (via AskUserQuestion): "What are the candidates you're considering?"

User: "Either the API gateway layer or inside the service itself. Both feel awkward."

Consider (via AskUserQuestion): "What makes the API gateway placement awkward?"

User: "It would need to know about per-user limits, which means it needs auth context — that feels like it's pulling in too much."

Consider (via AskUserQuestion): "And the service placement?"

User: "The service layer is already tangled with business logic. Adding rate limiting there feels like complection."

Consider: "Sounds like structural friction — both placements have coupling concerns, which suggests the design needs examination before committing. Want to run /hyperpowers:intuition?"
</conversation>
</example>

</examples>
