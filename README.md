# kharcha

A small Streamlit app for exploring personal spend — HDFC credit card + Google
Pay / UPI transactions, categorised and modelled in BigQuery.

This repo is **only the front-end**. Statements, parsing, category rules and the
BigQuery loader live in a separate private repo; nothing here contains
transaction data or personal names — the app reads aggregates from BigQuery at
run time.

## Pages

- **Overview** — headline KPIs, monthly spend trend (by category), spend by type
  (day-to-day / committed / cost-of-credit / discretionary), payment mix.
- _Explore_ and _Hidden costs_ pages are planned.

## Layout

| Path | Role |
|---|---|
| `streamlit_app.py` | Overview page + entry point |
| `lib/bq.py` | Cached BigQuery client + `run_query()` |
| `lib/queries.py` | One function per view → a DataFrame |
| `lib/charts.py` | Altair chart helpers |
| `lib/theme.py` | Palette + fixed category → colour map |

## Run locally

```bash
pip install -r requirements.txt
```

Create `.streamlit/secrets.toml` (git-ignored):

```toml
[bigquery]
project = "your-gcp-project"
dataset = "expenses"

[gcp_service_account]
# a service-account key with BigQuery Data Viewer + Job User, as TOML
type = "service_account"
project_id = "your-gcp-project"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "...@your-gcp-project.iam.gserviceaccount.com"
# ...remaining key fields
```

With no `[gcp_service_account]` block the client falls back to local
application-default credentials (`gcloud auth application-default login`).

```bash
streamlit run streamlit_app.py
```

## Deploy (Streamlit Community Cloud)

New app → this repo, branch `main`, main file `streamlit_app.py`. Paste the
`[bigquery]` and `[gcp_service_account]` blocks into the app's **Secrets**.

## Data model

The app expects these views in `<project>.<dataset>`:

- `transactions` — one row per transaction, with `net_amount` (debits positive,
  credits negative), `is_debit`, `in_common_window`, `category_group`.
- `monthly_category_spend` — `txn_month` × `category` aggregate.
- `counterparties` — per-counterparty rollup (used by the planned pages).
