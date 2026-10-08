#!/usr/bin/env python3
"""v2rayn_import.py - add one subscription group to a v2rayN 7.x data store.

What it does (Windows, Python 3 standard library only):
  1. backs up guiConfigs\\guiNDB.db with the sqlite backup API (consistent copy)
  2. inserts (or reuses, by group name) one row in table SubItem
  3. serves the subscription file on 127.0.0.1 while v2rayN's own scheduler
     downloads it (TaskManager runs subscription updates every minute when
     AutoUpdateInterval > 0 and UpdateTime is old)
  4. waits until v2rayN has written ProfileItem rows for the group
  5. turns auto-update back off (AutoUpdateInterval = 0)

It never restarts v2rayN, never changes the active node, never touches the
system proxy and never touches other subscription groups.
It prints ONE JSON line with counts and ids only - never node links.
Exit 0 = imported with at least one node, 2 = failed (see "error").
"""
import argparse
import json
import os
import shutil
import sqlite3
import sys
import threading
import time
import uuid
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROUTE = "/subscription.txt"


def stamp():
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def make_handler(payload):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802 (stdlib naming)
            if self.path.split("?")[0] != ROUTE:
                self.send_response(404)
                self.end_headers()
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, fmt, *args):  # keep quiet
            return

    return Handler


def serve(port, payload):
    srv = ThreadingHTTPServer(("127.0.0.1", port), make_handler(payload))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def backup_db(db, backup_dir):
    os.makedirs(backup_dir, exist_ok=True)
    dst_path = os.path.join(backup_dir, "guiNDB.before-" + stamp() + ".db")
    src = sqlite3.connect(db, timeout=30)
    dst = sqlite3.connect(dst_path)
    try:
        src.backup(dst)
    finally:
        dst.close()
        src.close()
    return dst_path


def columns(con, table):
    return [r[1] for r in con.execute("PRAGMA table_info(%s)" % table)]


def find_group(con, name):
    row = con.execute(
        "SELECT Id FROM SubItem WHERE Remarks = ? ORDER BY Sort LIMIT 1", (name,)
    ).fetchone()
    return row[0] if row else None


def next_sort(con):
    row = con.execute("SELECT COALESCE(MAX(Sort), 0) + 1 FROM SubItem").fetchone()
    return int(row[0])


def upsert_group(con, name, url, sub_id, interval_min):
    """Insert the group (or reuse one with the same name). Returns (id, reused)."""
    existing = find_group(con, name)
    if existing:
        con.execute(
            "UPDATE SubItem SET Url = ?, Enabled = 1, AutoUpdateInterval = ?, UpdateTime = 0 WHERE Id = ?",
            (url, interval_min, existing),
        )
        return existing, True
    cols = columns(con, "SubItem")
    row = {
        "Id": sub_id,
        "Remarks": name,
        "Url": url,
        "MoreUrl": "",
        "Enabled": 1,
        "UserAgent": "",
        "RequestHeaders": None,
        "Sort": next_sort(con),
        "Filter": None,
        "AutoUpdateInterval": interval_min,
        "UpdateTime": 0,
        "ConvertTarget": None,
        "PrevProfile": None,
        "NextProfile": None,
        "PreSocksPort": None,
        "Memo": "added by subs-check-pro pipeline (d2a66b2d)",
        "CustomCoreType": None,
    }
    use = [c for c in cols if c in row]
    sql = "INSERT INTO SubItem (%s) VALUES (%s)" % (
        ", ".join(use),
        ", ".join("?" for _ in use),
    )
    con.execute(sql, [row[c] for c in use])
    return sub_id, False


def group_state(db, sub_id):
    con = sqlite3.connect(db, timeout=30)
    try:
        sub = con.execute(
            "SELECT UpdateTime, AutoUpdateInterval FROM SubItem WHERE Id = ?", (sub_id,)
        ).fetchone()
        try:
            count = con.execute(
                "SELECT COUNT(*) FROM ProfileItem WHERE Subid = ?", (sub_id,)
            ).fetchone()[0]
        except sqlite3.Error:
            count = 0
        return (sub[0] if sub else None), int(count)
    finally:
        con.close()


def wait_for_v2rayn(db, sub_id, wait_sec, poll_sec=5):
    deadline = time.time() + wait_sec
    upd, count = None, 0
    while time.time() < deadline:
        upd, count = group_state(db, sub_id)
        if upd and upd > 0:  # v2rayN writes UpdateTime after the import step
            return {"updated": True, "profiles": count}
        time.sleep(poll_sec)
    return {"updated": False, "profiles": count}


def set_interval(db, sub_id, minutes):
    con = sqlite3.connect(db, timeout=30)
    try:
        con.execute("UPDATE SubItem SET AutoUpdateInterval = ? WHERE Id = ?", (minutes, sub_id))
        con.commit()
    finally:
        con.close()


def remove_group(db, sub_id):
    con = sqlite3.connect(db, timeout=30)
    try:
        con.execute("DELETE FROM ProfileItem WHERE Subid = ?", (sub_id,))
        con.execute("DELETE FROM SubItem WHERE Id = ?", (sub_id,))
        con.commit()
    finally:
        con.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--db", required=True, help="path to guiConfigs\\guiNDB.db")
    ap.add_argument("--group", required=True, help="group (subscription remarks) name")
    ap.add_argument("--file", required=True, help="base64 subscription file to serve")
    ap.add_argument("--port", type=int, required=True, help="free 127.0.0.1 port")
    ap.add_argument("--backup-dir", required=True)
    ap.add_argument("--wait", type=int, default=240)
    ap.add_argument("--v2rayn-running", type=int, default=0)
    a = ap.parse_args()

    res = {"ok": False, "group": a.group, "stamp": stamp(), "stage": "start"}

    def done(code):
        print(json.dumps(res, ensure_ascii=True))
        sys.stdout.flush()
        return code

    if not os.path.isfile(a.db):
        res["error"] = "database not found"
        return done(2)
    if not a.v2rayn_running:
        res["error"] = "v2rayN is not running; start it and re-run the import"
        res["stage"] = "v2rayn_not_running"
        return done(2)

    try:
        res["backup"] = os.path.basename(backup_db(a.db, a.backup_dir))
    except Exception as ex:  # noqa: BLE001
        res["error"] = "backup failed: %s" % type(ex).__name__
        return done(2)

    with open(a.file, "rb") as fh:
        payload = fh.read()
    if not payload.strip():
        res["error"] = "subscription file is empty"
        return done(2)
    res["bytes"] = len(payload)

    url = "http://127.0.0.1:%d%s" % (a.port, ROUTE)
    sub_id = str(uuid.uuid4())
    created = False
    srv = serve(a.port, payload)
    try:
        con = sqlite3.connect(a.db, timeout=30)
        try:
            sub_id, reused = upsert_group(con, a.group, url, sub_id, 1440)
            con.commit()
            res["subitem_columns"] = columns(con, "SubItem")  # names only, for the receipt
        finally:
            con.close()
        created = not reused
        res.update({"stage": "group_written", "sub_id": sub_id[:8], "reused_group": reused})

        waited = wait_for_v2rayn(a.db, sub_id, a.wait)
        res["stage"] = "waited"
        res["profiles"] = waited["profiles"]
        res["v2rayn_updated"] = waited["updated"]

        if waited["updated"] and waited["profiles"] > 0:
            set_interval(a.db, sub_id, 0)
            res.update({"ok": True, "stage": "imported", "auto_update": "off"})
        else:
            set_interval(a.db, sub_id, 0)
            res["error"] = "v2rayN did not import any node for the group"
            if created:
                remove_group(a.db, sub_id)
                res["rolled_back"] = True
    except Exception as ex:  # noqa: BLE001
        res["error"] = "import failed: %s" % type(ex).__name__
        if created:
            try:
                remove_group(a.db, sub_id)
                res["rolled_back"] = True
            except Exception:  # noqa: BLE001
                res["rolled_back"] = False
    finally:
        srv.shutdown()
        srv.server_close()
    return done(0 if res["ok"] else 2)


if __name__ == "__main__":
    sys.exit(main())
