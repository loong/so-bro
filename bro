#!/bin/sh

params="$@"

tmux new -d -s "so-bro"
tmux split-window -d -t 0 -h

WIDTH=$(($(tmux display-message -p '#{pane_width}') / 3))
tmux resize-pane -R $WIDTH

sleep 2 && tmux send-keys -t 0 "python3 watcher.py $params" enter &
tmux send-keys -t 1 "python3 debugger.py" enter

tmux attach -t "so-bro"
