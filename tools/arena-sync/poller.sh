#!/usr/bin/env bash
# tools/arena-sync/poller.sh
# Sandbox-side automatic pull/push polling for the session branch.
#
# Every INTERVAL seconds (default 120) it:
#   1. fetches origin/<branch>
#   2. commits + pushes local changes, but ONLY inside the whitelisted paths
#      (deliverable/, results/v2ray_subs/, code/, tools/) and only after the
#      repo gate (code/check_all.sh) passes
#   3. rebases onto origin/<branch> when the remote has newer commits
#   4. logs what the local watcher answered (handshake) and whether a receipt exists
#
# It never switches branches, never kills other processes, and never touches
# the handshake file while an agent-handsfree.sh round is running.
#
# Usage:  bash tools/arena-sync/poller.sh            (loop)
#         bash tools/arena-sync/poller.sh --once     (one tick, for debugging)
# Pause:  touch ~/.arena-sync/PAUSE      Resume: rm ~/.arena-sync/PAUSE
set -u

REPO="${REPO:-/home/user/subs-check-pro}"
BRANCH="${BRANCH:-arena/d2a66b2d-subs-check-pro}"
REMOTE="${REMOTE:-origin}"
INTERVAL="${INTERVAL:-120}"
STATE_DIR="${STATE_DIR:-/home/user/.arena-sync}"
LOG="$STATE_DIR/poller.log"
PAUSE_FILE="$STATE_DIR/PAUSE"
ALLOW_PATHS=(deliverable results/v2ray_subs code tools)
NEVER_PUSH=(results/status/handshake.json)

export GIT_TERMINAL_PROMPT=0
mkdir -p "$STATE_DIR"

log() {
  printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >> "$LOG"
  # keep the log bounded (last 2000 lines)
  if [ "$(wc -l < "$LOG" 2>/dev/null || echo 0)" -gt 4000 ]; then
    tail -n 2000 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"
  fi
}

in_repo() { git -C "$REPO" "$@"; }

tick() {
  if [ -f "$PAUSE_FILE" ]; then log "paused (PAUSE file present)"; return 0; fi

  local head_branch
  head_branch="$(in_repo rev-parse --abbrev-ref HEAD 2>/dev/null)"
  if [ "$head_branch" != "$BRANCH" ]; then
    log "skip: HEAD is '$head_branch', expected '$BRANCH' (not switching)"
    return 0
  fi

  # never race an agent-handsfree round (it owns the handshake file)
  if pgrep -f 'agent-handsfree.sh' >/dev/null 2>&1; then
    log "skip: agent-handsfree.sh is running"
    return 0
  fi

  if ! timeout 90 git -C "$REPO" fetch --quiet "$REMOTE" "$BRANCH" 2>>"$LOG"; then
    log "fetch failed (network?) - will retry"
    return 0
  fi

  # ---- 1) push local changes inside the whitelist -------------------------
  local dirty
  dirty="$(in_repo status --porcelain -- "${ALLOW_PATHS[@]}" 2>/dev/null \
            | grep -v -F -- "${NEVER_PUSH[0]}" || true)"
  if [ -n "$dirty" ]; then
    local count
    count="$(printf '%s\n' "$dirty" | grep -c .)"
    if [ -f "$REPO/code/check_all.sh" ] && ! (cd "$REPO" && bash code/check_all.sh >>"$LOG" 2>&1); then
      log "gate failed - not committing $count change(s)"
      return 0
    fi
    local existing=() p
    for p in "${ALLOW_PATHS[@]}"; do [ -e "$REPO/$p" ] && existing+=("$p"); done
    in_repo add -- "${existing[@]}" 2>>"$LOG"
    for p in "${NEVER_PUSH[@]}"; do in_repo reset -q -- "$p" 2>/dev/null || true; done
    if in_repo diff --cached --quiet; then
      log "nothing staged after filtering"
    else
      in_repo commit -q -m "sandbox: auto-sync $(date -u +%Y-%m-%dT%H:%MZ)" 2>>"$LOG" \
        && log "committed $count change(s)"
    fi
  fi
  # push only when we are actually ahead of the remote
  local ahead
  ahead="$(in_repo rev-list --count "$REMOTE/$BRANCH..HEAD" 2>/dev/null || echo 0)"
  if [ "${ahead:-0}" -gt 0 ]; then
    if timeout 120 git -C "$REPO" push -q "$REMOTE" "HEAD:$BRANCH" 2>>"$LOG"; then
      log "pushed $ahead commit(s) to $REMOTE/$BRANCH"
    else
      log "push rejected/failed - will pull --rebase and retry next tick"
    fi
  fi

  # ---- 2) pull remote commits (the local watcher answers here) ------------
  local behind
  behind="$(in_repo rev-list --count "HEAD..$REMOTE/$BRANCH" 2>/dev/null || echo 0)"
  if [ "${behind:-0}" -gt 0 ]; then
    if timeout 120 git -C "$REPO" pull -q --rebase --autostash "$REMOTE" "$BRANCH" 2>>"$LOG"; then
      log "pulled $behind remote commit(s)"
    else
      log "pull --rebase failed - manual attention needed"
      in_repo rebase --abort >/dev/null 2>&1 || true
      return 0
    fi
  fi

  # ---- 3) report what the watcher answered ---------------------------------
  local hs="$REPO/results/status/handshake.json"
  if [ -f "$hs" ] && command -v jq >/dev/null 2>&1; then
    local hsum
    hsum="$(jq -c '{round, arena_state, local_state, local_updated}' "$hs" 2>/dev/null)"
    [ -n "$hsum" ] && log "handshake: $hsum"
  fi
  local receipts
  receipts="$(ls "$REPO"/results/v2ray_subs/RECEIPT* 2>/dev/null | wc -l)"
  [ "$receipts" -gt 0 ] && log "receipts present: $receipts"
  return 0
}

if [ "${1:-}" = "--once" ]; then
  tick
  exit 0
fi

# single instance (a second copy exits instead of racing the first)
exec 9>"$STATE_DIR/poller.lock"
if ! flock -n 9; then
  echo "another poller is already running (lock held) - exiting" >&2
  exit 0
fi

log "poller started: repo=$REPO branch=$BRANCH interval=${INTERVAL}s"
while true; do
  tick || log "tick error (continuing)"
  sleep "$INTERVAL"
done
