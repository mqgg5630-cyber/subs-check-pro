#!/usr/bin/env python3
"""v2rayn_realtest.py - test share links the way v2rayN's real-ping test does.

Windows, Python 3 standard library only. Never prints node links.

  diag --dir <v2rayN folder> [--db <guiNDB.db>] [--gui <guiNConfig.json>]
      Read-only facts: the bundled core versions, the ping URL v2rayN uses and
      the last delay results stored by v2rayN (counts per group only).

  test --links <file> --dir <v2rayN folder> --out <folder>
       [--gui <guiNConfig.json>] [--workers 8] [--startup 8]
      For every share link: start the core that v2rayN uses for that protocol
      (bin\\Xray\\xray.exe, or bin\\sing_box\\sing-box.exe for hysteria2) with one
      local SOCKS inbound, then fetch v2rayN's ping URL through it. Same rules as
      ServiceLib GetRealPingTime: two GETs inside one 5 s budget, the best time
      wins, any HTTP answer counts, a timeout or error is -1; a node that fails
      gets one more round. Writes <out>\\realtest.json (no links) and
      <out>\\passed.txt (passing links, original order), prints one JSON line.
Pass an --out folder outside the git repository: passed.txt holds node links.
"""
import argparse
import base64
import collections
import json
import os
import re
import shutil
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

DEFAULT_PING_URL = 'https://www.google.com/generate_204'  # first entry of v2rayN SpeedPingTestUrls
LOCAL_FETCH_SEC = 5.0                                     # v2rayN Global.LocalFetch
IS_WIN = os.name == 'nt'
CURL = 'curl.exe' if IS_WIN else 'curl'
PROC_KW = {'creationflags': 0x08000000} if IS_WIN else {}  # CREATE_NO_WINDOW


class Unsupported(Exception):
    pass


def emit(obj):
    sys.stdout.write(json.dumps(obj, ensure_ascii=True) + '\n')
    sys.stdout.flush()


def sanitize(text):
    """Strip IPs, UUIDs and host names so that a message can be logged safely."""
    s = str(text)
    s = re.sub(r'\b\d{1,3}(?:\.\d{1,3}){3}\b', '<ip>', s)
    s = re.sub(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', '<uuid>', s)
    s = re.sub(r'[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}', '<host>', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s[:160]


# ------------------------------------------------------------ share link parsing

def b64_text(s):
    s = (s or '').strip()
    s += '=' * (-len(s) % 4)
    for fn in (base64.b64decode, base64.urlsafe_b64decode):
        try:
            return fn(s).decode('utf-8')
        except Exception:
            pass
    return None


def truthy(v):
    return str(v or '').strip().lower() in ('1', 'true', 'yes', 'on')


def split_link(link):
    scheme, rest = link.split('://', 1)
    name = ''
    if '#' in rest:
        rest, name = rest.split('#', 1)
    return scheme.lower(), rest, urllib.parse.unquote(name)


def parse_hostport(hp):
    if hp.startswith('['):
        host, _, tail = hp[1:].partition(']')
        return host, int(tail.lstrip(':'))
    host, sep, port = hp.rpartition(':')
    if not sep or not host:
        raise ValueError('no port in share link')
    return host, int(port)


def split_userhost(rest):
    main, _, query = rest.partition('?')
    main = main.rstrip('/')
    userinfo, hp = '', main
    if '@' in main:
        userinfo, hp = main.rsplit('@', 1)
    host, port = parse_hostport(hp)
    return userinfo, host, port, query


def qdict(query):
    # keep '+' as a plus sign (parse_qsl would turn it into a space)
    d = {}
    for k, v in urllib.parse.parse_qsl(query.replace('+', '%2B'), keep_blank_values=True):
        d.setdefault(k, v)
    return d


def xray_stream(q, host, default_security='none'):
    net = (q.get('type') or 'tcp').strip().lower()
    if net == 'raw':
        net = 'tcp'
    if net == 'h2':
        net = 'http'
    if net not in ('tcp', 'ws', 'grpc', 'httpupgrade', 'http'):
        raise Unsupported('transport ' + net)
    path = q.get('path') or ''
    hdr_host = q.get('host') or ''
    st = {'network': net}
    if net == 'tcp' and (q.get('headerType') or '').lower() == 'http':
        req = {'path': [path or '/']}
        if hdr_host:
            req['headers'] = {'Host': [hdr_host]}
        st['tcpSettings'] = {'header': {'type': 'http', 'request': req}}
    elif net == 'ws':
        ws = {'path': path or '/'}
        if hdr_host:
            ws['headers'] = {'Host': hdr_host}
        st['wsSettings'] = ws
    elif net == 'grpc':
        st['grpcSettings'] = {'serviceName': q.get('serviceName') or path.lstrip('/'),
                              'multiMode': (q.get('mode') or '').lower() == 'multi'}
    elif net == 'httpupgrade':
        st['httpupgradeSettings'] = {'path': path or '/', 'host': hdr_host or host}
    elif net == 'http':
        st['httpSettings'] = {'path': path or '/', 'host': [hdr_host or host]}
    sec = (q.get('security') or default_security).strip().lower()
    if sec == 'tls':
        tls = {'serverName': q.get('sni') or hdr_host or host}
        if q.get('fp'):
            tls['fingerprint'] = q['fp']
        if q.get('alpn'):
            tls['alpn'] = [x for x in q['alpn'].split(',') if x]
        if truthy(q.get('allowInsecure')) or truthy(q.get('insecure')):
            tls['allowInsecure'] = True
        st['security'] = 'tls'
        st['tlsSettings'] = tls
    elif sec == 'reality':
        st['security'] = 'reality'
        st['realitySettings'] = {'serverName': q.get('sni') or host, 'fingerprint': q.get('fp') or 'chrome',
                                 'publicKey': q.get('pbk') or '', 'shortId': q.get('sid') or '',
                                 'spiderX': q.get('spx') or ''}
    else:
        st['security'] = 'none'
    return st


def xray_vless(link):
    _, rest, _ = split_link(link)
    userinfo, host, port, query = split_userhost(rest)
    q = qdict(query)
    user = {'id': urllib.parse.unquote(userinfo), 'encryption': q.get('encryption') or 'none'}
    if q.get('flow'):
        user['flow'] = q['flow']
    return {'protocol': 'vless',
            'settings': {'vnext': [{'address': host, 'port': port, 'users': [user]}]},
            'streamSettings': xray_stream(q, host)}


def xray_vmess(link):
    body = link.split('://', 1)[1].split('#', 1)[0]
    txt = b64_text(body)
    if not txt:
        raise ValueError('vmess body')
    j = json.loads(txt)
    host = str(j.get('add') or '')
    port = int(j.get('port'))
    q = {'type': j.get('net') or 'tcp', 'path': j.get('path') or '', 'host': j.get('host') or '',
         'headerType': j.get('type') or '', 'security': 'tls' if str(j.get('tls') or '') == 'tls' else 'none',
         'sni': j.get('sni') or '', 'fp': j.get('fp') or '', 'alpn': j.get('alpn') or ''}
    user = {'id': str(j.get('id') or ''), 'alterId': int(j.get('aid') or 0), 'security': j.get('scy') or 'auto'}
    return {'protocol': 'vmess',
            'settings': {'vnext': [{'address': host, 'port': port, 'users': [user]}]},
            'streamSettings': xray_stream(q, host)}


def xray_trojan(link):
    _, rest, _ = split_link(link)
    userinfo, host, port, query = split_userhost(rest)
    q = qdict(query)
    return {'protocol': 'trojan',
            'settings': {'servers': [{'address': host, 'port': port, 'password': urllib.parse.unquote(userinfo)}]},
            'streamSettings': xray_stream(q, host, default_security='tls')}


def xray_socks(link):
    _, rest, _ = split_link(link)
    userinfo, host, port, _ = split_userhost(rest)
    user, pw = '', ''
    raw = urllib.parse.unquote(userinfo)
    if raw:
        dec = b64_text(raw) if re.fullmatch(r'[A-Za-z0-9+/_=-]+', raw) else None
        text = dec if (dec is not None and ':' in dec) else raw
        user, _, pw = text.partition(':')
    server = {'address': host, 'port': port}
    if user or pw:
        server['users'] = [{'user': user, 'pass': pw}]
    return {'protocol': 'socks', 'settings': {'servers': [server]}}


def xray_ss(link):
    _, rest, _ = split_link(link)
    userinfo, host, port, query = split_userhost(rest)
    if qdict(query).get('plugin'):
        raise Unsupported('shadowsocks plugin')
    raw = urllib.parse.unquote(userinfo)
    if ':' in raw:
        method, _, pw = raw.partition(':')
    else:
        dec = b64_text(raw)
        if not dec or ':' not in dec:
            raise ValueError('ss userinfo')
        method, _, pw = dec.partition(':')
    return {'protocol': 'shadowsocks',
            'settings': {'servers': [{'address': host, 'port': port, 'method': method, 'password': pw}]}}


def sb_hysteria2(link):
    _, rest, _ = split_link(link)
    pw, host, port, query = split_userhost(rest)
    q = qdict(query)
    tls = {'enabled': True, 'server_name': q.get('sni') or host,
           'insecure': truthy(q.get('insecure')) or truthy(q.get('allowInsecure'))}
    if q.get('alpn'):
        tls['alpn'] = [x for x in q['alpn'].split(',') if x]
    ob = {'type': 'hysteria2', 'tag': 'proxy', 'server': host, 'server_port': port,
          'password': urllib.parse.unquote(pw), 'tls': tls}
    if q.get('obfs'):
        ob['obfs'] = {'type': q['obfs'], 'password': q.get('obfs-password') or ''}
    return ob


def build(link):
    scheme = link.split('://', 1)[0].lower()
    if scheme == 'vless':
        return 'xray', xray_vless(link)
    if scheme == 'vmess':
        return 'xray', xray_vmess(link)
    if scheme == 'trojan':
        return 'xray', xray_trojan(link)
    if scheme in ('socks', 'socks5'):
        return 'xray', xray_socks(link)
    if scheme == 'ss':
        return 'xray', xray_ss(link)
    if scheme in ('hysteria2', 'hy2'):
        return 'sing_box', sb_hysteria2(link)
    raise Unsupported('scheme ' + scheme)


def xray_config(outbound, port):
    ob = dict(outbound)
    ob['tag'] = 'proxy'
    return {'log': {'loglevel': 'warning'},
            'inbounds': [{'tag': 'socks-in', 'listen': '127.0.0.1', 'port': port, 'protocol': 'socks',
                          'settings': {'auth': 'noauth', 'udp': False}}],
            'outbounds': [ob]}


def singbox_config(outbound, port):
    return {'log': {'level': 'warn'},
            'inbounds': [{'type': 'socks', 'tag': 'socks-in', 'listen': '127.0.0.1', 'listen_port': port}],
            'outbounds': [outbound]}


# ------------------------------------------------------------ running cores and testing

def free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]
    finally:
        s.close()


def curl_ms(url, port, budget):
    """One GET through the local SOCKS port. Milliseconds, or -1 when no HTTP answer."""
    if budget <= 0.2:
        return -1
    cmd = [CURL, '-s', '-o', os.devnull, '-w', '%{http_code} %{time_total}',
           '--max-time', '%.2f' % budget, '--connect-timeout', '%.2f' % budget,
           '-x', 'socks5h://127.0.0.1:%d' % port, url]
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                           timeout=budget + 5, **PROC_KW)
        parts = p.stdout.decode('ascii', 'replace').split()
        if len(parts) < 2 or parts[0] == '000':
            return -1
        return max(1, int(float(parts[1]) * 1000))
    except Exception:
        return -1


def real_ping(url, port):
    """v2rayN GetRealPingTime: two GETs inside one 5 s budget; a failed GET makes it -1."""
    deadline = time.monotonic() + LOCAL_FETCH_SEC
    times = []
    for _ in range(2):
        ms = curl_ms(url, port, deadline - time.monotonic())
        if ms <= 0:
            return -1
        times.append(ms)
        time.sleep(0.1)
    return min(times)


def ping_with_retry(url, port):
    """v2rayN GetRealPingTimeInfo: one more round when the first round failed."""
    ms = -1
    for _ in range(2):
        ms = real_ping(url, port)
        if ms > 0:
            break
    return ms


def start_core(exe, cfg_path, log_path):
    logf = open(log_path, 'wb')
    try:
        return subprocess.Popen([exe, 'run', '-c', cfg_path], stdout=logf, stderr=subprocess.STDOUT,
                                cwd=os.path.dirname(exe), **PROC_KW)
    finally:
        logf.close()


def wait_listen(port, proc, wait_sec):
    end = time.monotonic() + wait_sec
    while time.monotonic() < end:
        if proc.poll() is not None:
            return False
        try:
            with socket.create_connection(('127.0.0.1', port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.25)
    return False


def stop_core(proc):
    if proc is None:
        return
    try:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)
    except Exception:
        pass


def core_error(log_path):
    try:
        with open(log_path, 'rb') as f:
            lines = f.read().decode('utf-8', 'replace').splitlines()
    except Exception:
        return ''
    for ln in lines:
        low = ln.lower()
        if 'error' in low or 'failed' in low or 'fatal' in low or 'panic' in low:
            return sanitize(ln)
    return sanitize(lines[-1]) if lines else ''


def test_one(idx, link, ctx):
    scheme = link.split('://', 1)[0].lower() if '://' in link else '?'
    rec = {'index': idx, 'scheme': scheme, 'ok': False, 'ms': -1, 'reason': ''}
    try:
        core, outbound = build(link)
    except Unsupported as e:
        rec['reason'] = 'unsupported: ' + sanitize(e)
        return rec
    except Exception:
        rec['reason'] = 'parse_error'
        return rec
    exe = ctx['xray'] if core == 'xray' else ctx['singbox']
    if not exe:
        rec['reason'] = 'no_core: ' + core
        return rec
    port = free_port()
    cfg = xray_config(outbound, port) if core == 'xray' else singbox_config(outbound, port)
    cfg_path = os.path.join(ctx['work'], 'cfg_%d.json' % idx)
    log_path = os.path.join(ctx['work'], 'core_%d.log' % idx)
    proc = None
    try:
        with open(cfg_path, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(cfg, f, ensure_ascii=False)
        proc = start_core(exe, cfg_path, log_path)
        if not wait_listen(port, proc, ctx['startup']):
            rec['reason'] = 'core_exited' if proc.poll() is not None else 'core_no_listen'
            rec['core_error'] = core_error(log_path)
            return rec
        ms = ping_with_retry(ctx['url'], port)
        if ms > 0:
            rec['ok'] = True
            rec['ms'] = ms
            rec['reason'] = 'ok'
        else:
            rec['reason'] = 'no_response'
            rec['core_error'] = core_error(log_path)
    except Exception as e:
        rec['reason'] = 'harness_error: ' + type(e).__name__
    finally:
        stop_core(proc)
        for p in (cfg_path, log_path):
            try:
                os.remove(p)
            except OSError:
                pass
    return rec


def run_tests(links, ctx, workers):
    out = [None] * len(links)
    with ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
        futs = [ex.submit(test_one, i, link, ctx) for i, link in enumerate(links)]
        for i, f in enumerate(futs):
            try:
                out[i] = f.result()
            except Exception as e:
                out[i] = {'index': i, 'scheme': '?', 'ok': False, 'ms': -1,
                          'reason': 'harness_error: ' + type(e).__name__}
    return out


def find_core(base, candidates):
    for rel in candidates:
        p = os.path.join(base, *rel)
        if os.path.isfile(p):
            return p
    return None


def find_key(obj, wanted):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if str(k).lower() == wanted and isinstance(v, str) and v.strip():
                return v.strip()
            hit = find_key(v, wanted)
            if hit:
                return hit
    elif isinstance(obj, list):
        for v in obj:
            hit = find_key(v, wanted)
            if hit:
                return hit
    return None


def ping_url(gui_path):
    if gui_path and os.path.isfile(gui_path):
        try:
            with open(gui_path, 'r', encoding='utf-8-sig') as f:
                hit = find_key(json.load(f), 'speedpingtesturl')
            if hit and hit.startswith('http'):
                return hit, 'guiNConfig'
        except Exception:
            pass
    return DEFAULT_PING_URL, 'default'


def load_links(path):
    seen, out, skipped = set(), [], 0
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        for raw in f:
            s = raw.strip().lstrip('\ufeff').strip()
            if not s:
                continue
            if '://' not in s or s.lower().startswith(('http://', 'https://')):
                skipped += 1
                continue
            if s in seen:
                continue
            seen.add(s)
            out.append(s)
    return out, skipped


def cmd_test(a):
    t0 = time.time()
    links, skipped = load_links(a.links)
    xray = find_core(a.dir, [('bin', 'Xray', 'xray.exe'), ('bin', 'xray', 'xray.exe')])
    singbox = find_core(a.dir, [('bin', 'sing_box', 'sing-box.exe'), ('bin', 'sing-box', 'sing-box.exe')])
    url, url_src = ping_url(a.gui)
    os.makedirs(a.out, exist_ok=True)
    summary = {'mode': 'test', 'label': a.label, 'links': len(links), 'skipped_lines': skipped,
               'ping_url': url, 'ping_url_source': url_src,
               'cores': {'xray': bool(xray), 'sing_box': bool(singbox)}}
    if not links:
        summary.update(tested=0, passed=0, error='no share links in the input file')
        emit(summary)
        return 2
    work = tempfile.mkdtemp(prefix='v2rn_rt_')
    try:
        ctx = {'xray': xray, 'singbox': singbox, 'url': url, 'work': work, 'startup': a.startup}
        results = run_tests(links, ctx, a.workers)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    passed_links = [links[r['index']] for r in results if r['ok']]
    with open(os.path.join(a.out, 'passed.txt'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(''.join(x + '\n' for x in passed_links))
    by_reason = collections.Counter(r['reason'].split(':')[0] for r in results)
    by_scheme = collections.Counter(r['scheme'] for r in results)
    by_scheme_ok = collections.Counter(r['scheme'] for r in results if r['ok'])
    report = {'summary': summary, 'results': results}
    with open(os.path.join(a.out, 'realtest.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(report, f, ensure_ascii=True, indent=1)
    summary.update(tested=len(links), passed=len(passed_links), seconds=int(time.time() - t0),
                   by_reason=dict(by_reason), by_scheme=dict(by_scheme), by_scheme_passed=dict(by_scheme_ok))
    emit(summary)
    return 0


# ------------------------------------------------------------ read-only facts

def core_version(exe):
    if not exe:
        return None
    try:
        p = subprocess.run([exe, 'version'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           timeout=20, cwd=os.path.dirname(exe), **PROC_KW)
        lines = p.stdout.decode('utf-8', 'replace').strip().splitlines()
        return sanitize(lines[0]) if lines else ''
    except Exception as e:
        return 'error: ' + type(e).__name__


def db_facts(db, hint='subs-check-pro'):
    out = {}
    uri = 'file:' + db.replace('\\', '/') + '?mode=ro'
    con = sqlite3.connect(uri, uri=True, timeout=5)
    try:
        tables = sorted(r[0] for r in con.execute("select name from sqlite_master where type='table'"))
        out['tables'] = tables

        def cols(t):
            return [r[1] for r in con.execute('pragma table_info("%s")' % t)]
        if 'ProfileItem' in tables:
            out['profile_rows'] = con.execute('select count(*) from ProfileItem').fetchone()[0]
        if 'ProfileExItem' in tables:
            rows = con.execute('select Delay, Message from ProfileExItem').fetchall()
            out['profileex_rows'] = len(rows)
            out['delay'] = {'minus1': sum(1 for d, _ in rows if d == -1),
                            'positive': sum(1 for d, _ in rows if d and d > 0),
                            'zero_or_null': sum(1 for d, _ in rows if not d)}
            msgs = collections.Counter(sanitize(m) for _, m in rows if m)
            out['messages_top'] = [[k, v] for k, v in msgs.most_common(6)]
        if {'ProfileItem', 'SubItem', 'ProfileExItem'} <= set(tables):
            pc, sc = cols('ProfileItem'), cols('SubItem')
            if 'Subid' in pc and 'Remarks' in sc and 'Id' in sc:
                q = ('select s.Remarks, e.Delay from ProfileItem p '
                     'left join SubItem s on s.Id = p.Subid '
                     'left join ProfileExItem e on e.IndexId = p.IndexId')
                groups = collections.OrderedDict()
                for rem, d in con.execute(q):
                    name = rem or '(no group)'
                    g = groups.setdefault(name, {'profiles': 0, 'minus1': 0, 'positive': 0, 'zero_or_null': 0})
                    g['profiles'] += 1
                    if d == -1:
                        g['minus1'] += 1
                    elif d and d > 0:
                        g['positive'] += 1
                    else:
                        g['zero_or_null'] += 1
                labelled = {}
                for i, (name, g) in enumerate(groups.items()):
                    label = name if hint in name else 'group_%d' % (i + 1)
                    labelled[label] = g
                out['groups'] = labelled
    finally:
        con.close()
    return out


def cmd_diag(a):
    res = {'mode': 'diag'}
    xray = find_core(a.dir, [('bin', 'Xray', 'xray.exe'), ('bin', 'xray', 'xray.exe')])
    singbox = find_core(a.dir, [('bin', 'sing_box', 'sing-box.exe'), ('bin', 'sing-box', 'sing-box.exe')])
    res['cores'] = {'xray': core_version(xray) if xray else None,
                    'sing_box': core_version(singbox) if singbox else None}
    url, src = ping_url(a.gui)
    res['ping_url'] = url
    res['ping_url_source'] = src
    if a.db and os.path.isfile(a.db):
        try:
            res['db'] = db_facts(a.db)
        except Exception as e:
            res['db_error'] = type(e).__name__
    else:
        res['db'] = None
    emit(res)
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description='v2rayN-style real ping test for share links')
    sub = ap.add_subparsers(dest='cmd', required=True)
    d = sub.add_parser('diag')
    d.add_argument('--dir', required=True)
    d.add_argument('--db', default='')
    d.add_argument('--gui', default='')
    t = sub.add_parser('test')
    t.add_argument('--links', required=True)
    t.add_argument('--dir', required=True)
    t.add_argument('--out', required=True)
    t.add_argument('--gui', default='')
    t.add_argument('--workers', type=int, default=8)
    t.add_argument('--startup', type=float, default=8.0)
    t.add_argument('--label', default='test')
    a = ap.parse_args(argv)
    if a.cmd == 'diag':
        return cmd_diag(a)
    return cmd_test(a)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
