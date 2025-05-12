#!/bin/bash
# Start both the Auth API server and Web server

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Check if node is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is required but not installed."
    exit 1
fi

# Check if tmux is installed
if command -v tmux &> /dev/null; then
    # Use tmux to run both servers in split panes
    echo "Starting Auth servers using tmux..."
    
    # Create new tmux session in detached mode
    tmux new-session -d -s "ai-agency-auth" -n "auth-servers"
    
    # Split the window vertically
    tmux split-window -v -t "ai-agency-auth"
    
    # Send commands to each pane
    tmux send-keys -t "ai-agency-auth:0.0" "cd \"$SCRIPT_DIR\" && node auth_api.js" C-m
    tmux send-keys -t "ai-agency-auth:0.1" "cd \"$SCRIPT_DIR\" && node serve_auth_page.js" C-m
    
    # Attach to the session
    tmux attach-session -t "ai-agency-auth"
else
    # Fallback to opening two terminals
    echo "Starting Auth API server..."
    
    # Use platform-specific terminal commands
    case "$(uname -s)" in
        Darwin)  # macOS
            osascript -e 'tell application "Terminal" to do script "cd \"'"$SCRIPT_DIR"'\" && node auth_api.js"'
            osascript -e 'tell application "Terminal" to do script "cd \"'"$SCRIPT_DIR"'\" && node serve_auth_page.js"'
            ;;
        Linux)
            if command -v gnome-terminal &> /dev/null; then
                gnome-terminal -- bash -c "cd \"$SCRIPT_DIR\" && node auth_api.js; exec bash"
                gnome-terminal -- bash -c "cd \"$SCRIPT_DIR\" && node serve_auth_page.js; exec bash"
            elif command -v konsole &> /dev/null; then
                konsole -e bash -c "cd \"$SCRIPT_DIR\" && node auth_api.js; exec bash" &
                konsole -e bash -c "cd \"$SCRIPT_DIR\" && node serve_auth_page.js; exec bash" &
            elif command -v xterm &> /dev/null; then
                xterm -e "cd \"$SCRIPT_DIR\" && node auth_api.js; exec bash" &
                xterm -e "cd \"$SCRIPT_DIR\" && node serve_auth_page.js; exec bash" &
            else
                echo "Warning: Cannot detect terminal emulator. Starting servers in background."
                cd "$SCRIPT_DIR" && node auth_api.js > auth_api.log 2>&1 &
                cd "$SCRIPT_DIR" && node serve_auth_page.js > auth_web.log 2>&1 &
                echo "Servers started in background. See auth_api.log and auth_web.log for output."
            fi
            ;;
        CYGWIN*|MINGW*|MSYS*)  # Windows
            start cmd /k "cd \"$SCRIPT_DIR\" && node auth_api.js"
            start cmd /k "cd \"$SCRIPT_DIR\" && node serve_auth_page.js"
            ;;
        *)
            echo "Warning: Unsupported platform. Starting servers in background."
            cd "$SCRIPT_DIR" && node auth_api.js > auth_api.log 2>&1 &
            cd "$SCRIPT_DIR" && node serve_auth_page.js > auth_web.log 2>&1 &
            echo "Servers started in background. See auth_api.log and auth_web.log for output."
            ;;
    esac
    
    echo "Auth servers should now be running in separate terminal windows."
fi

echo "Auth API server running at http://localhost:3000/"
echo "Auth Web interface running at http://localhost:8000/"
echo
echo "Available users:"
echo "  - admin@example.com / adminpass (full access)"
echo "  - user@example.com / userpass (read-only access)"