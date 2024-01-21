# Restoring a file
# The script takes as argument a set of flags which values are treated as wildcards to match a list files in the trash directory
# Using <jq> command to achieve this
# The flags:
#   * -n | --name: name of a file [ names can be repeated because files can have same name without sharing the location ]
#   * -t | --tname: trash name of a file [ trash names are unique ]
#   * -o | --origin: original directory of a file
#
# JQ is used with <select> function that produces an array of files based on a combination of regex for each flag
# So we need to build first the regex for each flag
#
# Bashly simplifies this process:
#   - To get the file name wildcard provided as argument to the program:
#     - If the flags is provided
#       - ${args[-n]} or ${args[--name]}
#       - Save this as a string
#       - Append the last string to the final widlcard to use with the <select> function
#     - Do the same for the remaining flags
#
# Call JQ with the combination of wildcards for the right properties (tname, name, origin values)
# Save the result as an array of metadata objects
# For each metadata object:
# - Check the existence of the trash file based of the tname property:
#   - If it does not exist in the trash directory
#     - Notify the user
#     - Abort the operation
# - Check the existence of the original file based on the concatenation of the name and origin properties
#   - If it does exist:
#     - The user will be asked to confirm the restoring because this will overwrite the existing file
#   - If it does not exist
#     - Get from the metadata file, the following properties:
#       - origin
#         - if the origin does not exist:
#           - Notify the non-existence of the original directory
#           - Exit with Failure
#       - name
#     - Concatenate the origin with the name
#     - Update the metadata file:
#       - Delete the metadata object for the specific file
#     - Move the file:
#       - source: tname
#       - destination: Concatenation of the origin and the name properties
#       - Notify the user of this operation.
#     - End of the execution successfully

initialize_trash

TRASH_DIR="$HOME/.trashbin"
METADATA_FILE="$TRASH_DIR/trash_metadata.json"

original_dir=$(pwd)

pushd "$TRASH_DIR" > /dev/null 2>&1 || exit 1

all_metadata=$(cat "$METADATA_FILE")

if [ -z "$all_metadata" ] || [ "$all_metadata" = "[]" ]; then
  echo "The trash is empty !"
else
  tname_flag="${args[--tname]}"

  metadata="$all_metadata"

  if [ -n "$tname_flag" ]; then
    metadata=$(echo "$metadata" | jq 'map(select(.tname == "'"$tname_flag"'"))')
  fi
  
  metadata=$(echo "$metadata" | jq '.[0]')

  name=$(echo "$metadata" | jq -r '.name')
  tname=$(echo "$metadata" | jq -r '.tname')
  origin=$(echo "$metadata" | jq -r '.origin')

  if ! test -e "$tname_flag"; then
    echo "File not found in the trash: $tname_flag"
    exit 1
  fi

  full_origin="$origin/$name"

  if test -e "$full_origin"; then
    echo "'$name' already exists in '$origin'"
    read -p "Are you sure you want to empty the trash? (y|Y / n|N): " confirmation
    if [[ "$confirmation" == "y" || "$confirmation" == "Y" ]]; then
      mv "$tname" "$full_origin"
      echo "$name is moved into $origin"

      remaining_metadata=$(echo "$all_metadata" | jq 'map(select(.tname != "'"$tname_flag"'"))')
      echo "$remaining_metadata" > "$METADATA_FILE"
    else
      echo "Operation cancelled"
    fi
  else
    mv "$tname" "$full_origin"
    echo "$name is moved into $origin"

    remaining_metadata=$(echo "$all_metadata" | jq 'map(select(.tname != "'"$tname_flag"'"))')
    echo "$remaining_metadata" > "$METADATA_FILE"
  fi
fi

popd >& /dev/null
