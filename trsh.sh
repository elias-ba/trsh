#!/bin/sh

trash_dir="$HOME/.trashbin"
metadata_file="$trash_dir/trash_metadata.txt"
days_to_restore=7

delete_files() {
    for file in "$@"; do
        if [ -e "$file" ]; then
            abs_path=$(command -v realpath >/dev/null && realpath "$file" || echo "$(cd "$(dirname "$file")" && pwd -P)/$(basename "$file")")
            mv "$abs_path" "$trash_dir"
            echo "Deleted: $abs_path"
            echo "$abs_path" >>"$metadata_file"
        else
            echo "File not found: $file"
        fi
    done
}

restore_files() {
    if [ -n "$1" ]; then
        file_to_restore="$trash_dir/$(basename "$1")"
        if [ -e "$file_to_restore" ]; then
            mv "$file_to_restore" "$(command -v realpath >/dev/null && realpath "$1" || echo "$(cd "$(dirname "$1")" && pwd -P)/$(basename "$1")")"
            echo "Restored: $1"
        else
            echo "File not found in trash: $1"
        fi
    else
        while IFS= read -r original_path; do
            file_in_trash="$trash_dir/$(basename "$original_path")"
            if [ -e "$file_in_trash" ]; then
                mv "$file_in_trash" "$original_path"
                echo "Restored: $original_path"
            else
                echo "File not found in trash: $original_path"
            fi
        done <"$metadata_file"
    fi
}

list_trash_items() {
    ls -l "$trash_dir"
}

empty_trash() {
    rm -rf "$trash_dir"/*
    echo "Trash emptied."
}

purge_old_files() {
    current_time=$(date +%s)
    for file in "$trash_dir"/*; do
        deletion_time=$(stat -c %Y "$file" 2>/dev/null || stat -f %B "$file")
        time_difference=$((current_time - deletion_time))
        if [ "$time_difference" -gt $((days_to_restore * 24 * 3600)) ]; then
            rm -rf "$file"
            echo "Purged: $file (beyond restore timeframe)"
        fi
    done
}

set_grace_period() {
    if [ -n "$1" ] && [ "$1" -eq "$1" ] 2>/dev/null; then
        days_to_restore="$1"
        echo "Grace period set to $days_to_restore days."

        # Check for cron or systemd timers
        if command -v cron >/dev/null; then
            (
                crontab -l 2>/dev/null
                echo "0 0 * * * $PWD/trsh.sh purge"
            ) | crontab -
            echo "Cron job added for automatic purging."
        elif command -v systemctl >/dev/null && systemctl list-units --type=timer --quiet; then
            echo "[Timer]" >"$HOME/.config/systemd/user/trsh.timer"
            echo "OnCalendar=daily" >>"$HOME/.config/systemd/user/trsh.timer"
            echo "Unit=trsh.service" >>"$HOME/.config/systemd/user/trsh.timer"

            echo "[Unit]" >"$HOME/.config/systemd/user/trsh.service"
            echo "Description=Trash Util Automatic Purge" >>"$HOME/.config/systemd/user/trsh.service"
            echo "ExecStart=$PWD/trsh.sh purge" >>"$HOME/.config/systemd/user/trsh.service"

            systemctl --user enable --now trsh.timer
            echo "Systemd timer added for automatic purging."
        else
            echo "Neither cron nor systemd timers found. Automatic purging not supported on this system."
        fi
    else
        echo "Invalid grace period. Please provide a valid number of days."
    fi
}

case "$1" in
"delete")
    shift
    delete_files "$@"
    ;;
"restore")
    shift
    restore_files "$@"
    ;;
"list")
    list_trash_items
    ;;
"empty")
    empty_trash
    ;;
"purge")
    purge_old_files
    ;;
"config")
    shift
    case "$1" in
    "--rentention-period")
        shift
        set_grace_period "$1"
        ;;
    *)
        echo "Invalid config option. Usage: trsh config --retention-period days"
        exit 1
        ;;
    esac
    ;;
*)
    echo "Usage: trsh [delete file1 file2 ... | restore [file] | list | empty | purge | config --retention-period days]"
    exit 1
    ;;
esac

exit 0
