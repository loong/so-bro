#!/bin/sh

# Create new tmux session with 2 windows
tmux new -d -s "so-bro"
tmux split-window -d -t 0 -h

# Adjust pane width
WIDTH=$(($(tmux display-message -p '#{pane_width}') / 3))
tmux resize-pane -R $WIDTH

# Need to run the debugger first to provide debugging service on which
# the watcher connects to
params="$@"
sleep 2 && tmux send-keys -t 0 "python3 watcher.py $params" enter &
tmux send-keys -t 1 "python3 debugger.py" enter

# Watchdog will check if number of windows drop below 2 (means one
# window has been closed). If so, tmux session is killed
# automatically.
echo "Run watchdog"
function watchdog() {
    while true; do
    sleep 1

    if [[ $((`tmux list-panes | wc -l`)) -lt 2 ]]; then
	tmux kill-session -t "so-bro"
	break
    fi
    done
}

watchdog &

tmux attach -t "so-bro"
