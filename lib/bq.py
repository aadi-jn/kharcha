"""BigQuery connection layer.

One cached client, one cached query function. The client uses a service-account
key from st.secrets when deployed (Streamlit Community Cloud), and falls back to
local application-default credentials for `streamlit run` on a dev machine — the
same code path both ways.
"""

from __future__ import annotations

import decimal
import os

import pandas as pd
import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account


def _cfg(key: str, default: str = "") -> str:
    try:
        return st.secrets["bigquery"][key]
    except (KeyError, FileNotFoundError):
        return os.environ.get(f"BQ_{key.upper()}", default)


# Project / dataset come from secrets (or BQ_PROJECT / BQ_DATASET env vars for
# local dev), so nothing environment-specific is hard-coded in the repo.
PROJECT = _cfg("project")
DATASET = _cfg("dataset", "expenses")


@st.cache_resource
def get_client() -> bigquery.Client:
    try:
        info = st.secrets["gcp_service_account"]
    except (KeyError, FileNotFoundError):
        info = None
    project = PROJECT or None
    if info:
        creds = service_account.Credentials.from_service_account_info(dict(info))
        return bigquery.Client(project=project, credentials=creds)
    return bigquery.Client(project=project)


@st.cache_data(ttl=3600, show_spinner=False)
def run_query(sql: str) -> pd.DataFrame:
    # create_bqstorage_client=False: the result sets here are tiny, and the
    # Storage API needs an extra permission (bigquery.readsessions.create) we
    # don't want to depend on. Plain REST is fine.
    df = get_client().query(sql).to_dataframe(create_bqstorage_client=False)
    # BigQuery NUMERIC lands as object-dtype Decimal, which Altair can't type.
    for col in df.columns:
        if df[col].map(lambda v: isinstance(v, decimal.Decimal)).any():
            df[col] = df[col].astype(float)
    return df


def table(name: str) -> str:
    """Fully-qualified table/view name for use in an f-string query."""
    return f"`{PROJECT}.{DATASET}.{name}`"
