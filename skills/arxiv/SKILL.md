---
name: arxiv
description: "Search AI papers, get personalized recommendations, and trigger daily digests from the local arxiv-sanity-lite instance. Triggers on: arxiv, papers, research papers, paper search."
---

# Arxiv: AI Paper Discovery

Query the local arxiv-sanity-lite instance for paper search, recommendations, and digest management.

## Trigger

User runs `/arxiv` with a search query, `--recommend`, or `--digest`.

## Commands

### Search Papers

```
/arxiv "transformer architecture improvements"
/arxiv "RLHF reward modeling"
/arxiv "mixture of experts scaling"
```

### Get Recommendations

```
/arxiv --recommend
```

### Trigger Daily Digest

```
/arxiv --digest
```

## Process

### Step 1: Determine Action

Parse the user input:
- If a quoted string or bare text follows `/arxiv` -> **search**
- If `--recommend` flag -> **recommend**
- If `--digest` flag -> **digest**

### Step 2: Execute Query

**For search:**

```bash
# Query the arxiv-sanity-lite API
curl -s "http://CONTAINER_HOST_IP:5002/search" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"query": "<search_terms>"}'
```

If the API does not expose a JSON endpoint, fall back to scraping the search page:

```bash
curl -s "http://CONTAINER_HOST_IP:5002/?q=<url_encoded_query>"
```

Parse the response and extract paper entries.

**For recommendations:**

```bash
curl -s "http://CONTAINER_HOST_IP:5002/recommend"
```

Returns papers ranked by similarity to the user's saved/liked papers.

**For digest:**

```bash
# Trigger a manual digest run on the NAS
ssh claude@CONTAINER_HOST_IP "cd ~/brain-and-co && docker compose -f deploy/docker-compose.arxiv.yml exec arxiv-sanity python send_digest.py"
```

### Step 3: Format Results

Present results in a structured table:

```
=== Arxiv Search: "<query>" ===

| # | Title | Authors | Score |
|---|-------|---------|-------|
| 1 | [Paper Title](https://arxiv.org/abs/XXXX.XXXXX) | Author et al. | 0.95 |
| 2 | ... | ... | ... |

Top result abstract:
> [First paragraph of the highest-ranked paper's abstract]

Found N papers. Say "save 1,3" to bookmark papers for better recommendations.
```

### Step 4: Save Papers (Optional)

If the user says "save 1,3" or similar:

```bash
# Add papers to the user's saved list for recommendation training
curl -s "http://CONTAINER_HOST_IP:5002/save" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"paper_ids": ["XXXX.XXXXX", "YYYY.YYYYY"]}'
```

Confirm what was saved:

```
Saved 2 papers. Your recommendations will improve over time.
```

### Step 5: Persist to Memento (Optional)

For saved papers, also store in cross-agent memory:

```
Use Memento MCP `remember` tool:
- topic: "arxiv-papers"
- type: "fact"
- content: "[Paper Title] by [Authors] (arxiv:XXXX.XXXXX) - [one-line summary]"
- importance: 0.6
- scope: "permanent"
```

## Rules

- ALWAYS try the HTTP API first before falling back to SSH commands
- If the arxiv-sanity instance is unreachable, tell the user and suggest checking the deployment
- Present no more than 10 results per query to keep output manageable
- Include arxiv.org links so users can read the full paper
- Memento persistence is best-effort; do not fail the skill if Memento is unreachable
- If `--digest` is used and SMTP is not configured, warn the user

## Infrastructure

- **Endpoint**: `http://CONTAINER_HOST_IP:5002`
- **Deploy config**: `deploy/docker-compose.arxiv.yml`
- **Data volume**: `arxiv_data` (SQLite database + computed features)
- **Cron schedule**: Daily at 06:00 UTC (fetch), 06:30 UTC (features), 07:00 UTC (digest)
