# Displaying information about the trash

initialize_trash

TRASH_DIR="$HOME/.trashbin/"
METADATA_FILE="$TRASH_DIR/trash_metadata.json"

metadata=$(cat "$METADATA_FILE") 

pushd "$TRASH_DIR" > /dev/null 2>&1 || exit 1

is_empty="$(ls "$TRASH_DIR")"

if [ -z "$metadata" ] || [ "$metadata" = "[]" ] || [ -z "$is_empty" ]; then
  echo "The trash is empty !"
else
  metadata=$(cat "$METADATA_FILE")
  metadata=$(echo "$metadata" | jq 'map(. | {name, tname, type, origin, dtime})')
  name_flag="${args[--name]}"
  tname_flag="${args[--tname]}"
  origin_flag="${args[--origin]}"

  if [ -n "$name_flag" ]; then
    metadata=$(echo "$metadata" | jq 'map(select(.name | test("'"$name_flag"'")))')
  fi

  if [ -n "$tname_flag" ]; then
    metadata=$(echo "$metadata" | jq 'map(select(.tname == "'"$tname_flag"'"))')
  fi

  if [ -n "$origin_flag" ]; then
    metadata=$(echo "$metadata" | jq 'map(select(.origin | test("'"$origin_flag"'")))')
  fi

  if [ -z "$metadata" ] || [ "$metadata" = "[]" ]; then
    echo "No matching"
  else
    echo "$metadata" | jq '.'
  fi
fi

popd >& /dev/null
