#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time

import pandas as pd

os.system(f"{sys.executable} -m pip install feedparser")
os.system(f"{sys.executable} -m pip install -U pytd==0.8.0 td-client")

import pytd
import tdclient
import feedparser


TD_APIKEY = os.environ.get("td_apikey")
TD_ENDPOINT = os.environ.get("td_endpoint")


def rss_import(dest_db: str, dest_table: str, rss_url_list):
    df = pd.DataFrame(columns=["title", "description", "link"])
    ts = str(int(time.time()))
    for rss_url in rss_url_list:
        d = feedparser.parse(rss_url)
        for entry in d.entries:
            tmp_se = pd.Series(
                [entry.title, entry.description, entry.link], index=df.columns
            )
            df = df.append(tmp_se, ignore_index=True)

    client = pytd.Client(
        apikey=TD_APIKEY,
        endpoint=TD_ENDPOINT,
        database=dest_db,
        default_engine="presto",
    )
    try:
        client.api_client.create_database(dest_db)
        print(f"Create database: {dest_db}")
    except tdclient.errors.AlreadyExistsError:
        pass
    client.load_table_from_dataframe(df, dest_table, if_exists="append")
