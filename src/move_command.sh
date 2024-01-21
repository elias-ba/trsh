# Moving a file to the trash
# Define the trash path, for example $HOME/.trashbin/
# Define the trash metadata to save information about trash files
# Get the argument and save the provided argument(s) for the file(s) to move to the trash
# Define an array to save the file(s) to move to the trash.
# Loop through the array of files.
# For each file:
#   - Extract the basename of the file with basename
#   - Extract the path of the directory of the file with dirname
#   (Those two elements constitute the full path of the filename)
#   - Save the metadata of the file
#   - Save the basename of the file as trash path for this file
#   - While trash path of the file does exist in the trash
#     - Update the trash path to "basename + '.' + counter"
#     - Increment the counter
#   - Save the metadata of the file:
#     - name: Name of the file
#     - inode: Inode number of the file
#     - type: Type of the file
#     - size: Size of the file
#     - ttime: Datetime of move to the trash
#     - atime: Datetime of last access
#     - mtime: Datetime of the last modification
#     - device: Device number ID
#     - uid: User ID
#     - gid: Group ID
#     - links: Number of hard links
#         - Initialize a counter to 2
#   - Move the file to the trash:
#     - Source : Original full path of the file to move to trash
#     - Destination: available trash path for the file.

initialize_trash

TRASH_DIR="$HOME/.trashbin"
METADATA_FILE="$TRASH_DIR/trash_metadata.json"
metadata=$(cat "$METADATA_FILE")

files=''


eval "files=(${args[file]:-})"

for file_path in "${files[@]}"; do
  bname=$(basename "$file_path")
  dname=$(dirname "$file_path")

  file_type=$(stat -c "%F" "$file_path")
  file_name=$(basename "$file_path")
  origin=$(realpath "$dname")
  if [ "$origin" == "." ]; then
    origin=$(pwd)
  fi

  inode=$(stat -c "%i" "$file_path")

  atime=$(stat -c "%X" "$file_path")
  atime=$(date "+%Y-%m-%d %H:%M:%S" --date="@$atime")

  mtime=$(stat -c "%Y" "$file_path")
  mtime=$(date "+%Y-%m-%d %H:%M:%S" --date="@$mtime")

  local trash_file_name="$bname"
  local file_name_no_ext="${bname%.*}"
  local trash_path_file="$TRASH_DIR/$bname"
  if [ -e "$trash_path_file" ]; then
    if [ "$trash_file_name" == "$file_name_no_ext" ]; then
      counter=2
      while [ -e "$trash_path_file" ]; do
        trash_file_name="$file_name_no_ext.$counter"
        trash_path_file="$TRASH_DIR/$trash_file_name"
        ((counter++))
      done
    else
      counter=2
      local file_extension="${bname##*.}"
      while [ -e "$trash_path_file" ]; do
        trash_file_name="$file_name_no_ext.$counter.$file_extension"
        trash_path_file="$TRASH_DIR/$trash_file_name"
        ((counter++))
      done
    fi
    dtime=$(date +"%Y-%m-%d %H:%M:%S")
      new_metadata='{
        "name": "'"$file_name"'",
        "tname": "'"$trash_file_name"'",
        "type": "'"$file_type"'",
        "origin": "'"$origin"'",
        "inode": '"$inode"',
        "dtime": "'"$dtime"'",
        "atime": "'"$atime"'",
        "mtime": "'"$mtime"'"
      }'

    jq --argjson new_metadata "$new_metadata" '. += [$new_metadata]' "$METADATA_FILE" > "$METADATA_FILE.tmp" && mv "$METADATA_FILE.tmp" "$METADATA_FILE"

    mv "$file_path" "$trash_path_file"
  else
    dtime=$(date +"%Y-%m-%d %H:%M:%S")
      new_metadata='{
        "name": "'"$file_name"'",
        "tname": "'"$trash_file_name"'",
        "type": "'"$file_type"'",
        "origin": "'"$origin"'",
        "inode": '"$inode"',
        "dtime": "'"$dtime"'",
        "atime": "'"$atime"'",
        "mtime": "'"$mtime"'"
      }'


    jq --argjson new_metadata "$new_metadata" '. += [$new_metadata]' "$METADATA_FILE" > "$METADATA_FILE.tmp" && mv "$METADATA_FILE.tmp" "$METADATA_FILE"

    mv "$file_path" "$trash_path_file"
  fi
done

