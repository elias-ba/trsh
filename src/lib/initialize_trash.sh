TRASH_DIR="$HOME/.trashbin/"
METADATA_FILE="$TRASH_DIR/trash_metadata.json"

initialize_trash() {
    if [ ! -d "$TRASH_DIR" ]; then
        mkdir -p "$TRASH_DIR"
    fi

    if [ ! -f "$METADATA_FILE" ]; then
        echo "[]" > "$METADATA_FILE"
    fi
}
