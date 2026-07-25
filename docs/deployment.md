# Deploying the signal runner

The runner (`runner.py`) fetches the Mission Control watchlist, computes each
strategy's latest signal, and POSTs it back. Mission Control detects new
crossovers and sends notifications. It needs two env vars:

| Variable | Value |
|---|---|
| `VESPERA_API_URL` | Mission Control base URL, e.g. `https://vespera.systems` |
| `VESPERA_API_KEY` | Must match `VESPERA_LAB_API_KEY` on Mission Control |

Pick **one** scheduler — the code is identical everywhere.

## Option A: GitHub Actions (free, running today)

`.github/workflows/daily-signals.yml` runs weekdays at 21:30 UTC (after US
close) and supports manual "Run workflow" from the Actions tab.

Setup: repo → Settings → Secrets and variables → Actions → add
`VESPERA_API_URL` and `VESPERA_API_KEY`. Done.

## Option B: Azure Container Apps Job (when Azure credits land)

Cheapest proper-cloud option; scale-to-zero, you pay seconds per day.

```bash
az group create -n vespera-lab -l westeurope
az acr create -n vesperalab -g vespera-lab --sku Basic --admin-enabled true
az acr build -r vesperalab -t vespera-runner:latest .

az containerapp env create -n vespera-env -g vespera-lab -l westeurope

az containerapp job create \
  -n vespera-signals -g vespera-lab --environment vespera-env \
  --trigger-type Schedule --cron-expression "30 21 * * 1-5" \
  --image vesperalab.azurecr.io/vespera-runner:latest \
  --registry-server vesperalab.azurecr.io \
  --cpu 0.25 --memory 0.5Gi \
  --secrets api-key=<VESPERA_API_KEY> \
  --env-vars VESPERA_API_URL=https://vespera.systems VESPERA_API_KEY=secretref:api-key

# manual "run now":
az containerapp job start -n vespera-signals -g vespera-lab
```

(Azure ML scheduled jobs also work if you want to learn that platform —
same container, `az ml schedule create` — but Container Apps is simpler
and cheaper for a CPU cron.)

## Option C: Nebius VM cron (if Nebius credits land instead)

Nebius is GPU-first; for this CPU job just use a small VM:

```bash
docker build -t vespera-runner .
# on the VM's crontab:
30 21 * * 1-5 docker run --rm -e VESPERA_API_URL=... -e VESPERA_API_KEY=... vespera-runner
```

Save Nebius for what it's good at: AI Studio LLM inference behind Mission
Control, and GPU training when strategies get ML-heavy.

## Managing the watchlist

```bash
curl -X POST $VESPERA_API_URL/api/watchlist \
  -H "x-vespera-api-key: $VESPERA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "SPY", "strategy": "moving-average-crossover"}'
```

## Notifications

Set on Mission Control (Vercel env vars):

- `RESEND_API_KEY` — from https://resend.com (free tier is plenty)
- `SIGNAL_NOTIFY_EMAIL` — where to send trade-moment alerts
- `SIGNAL_FROM_EMAIL` — a verified sender (optional)

Without these, new signals are still stored and visible in `/lab`;
they're just not emailed.
