#!/bin/bash
initialize_trash

TRASH_DIR="$HOME/.trashbin"

if [ -d "$TRASH_DIR" ]; then
  read -p "Are you sure you want to empty the trash? (y | Y/ n | N): " confirmation
  if [[ "$confirmation" == "y" || "$confirmation" == "Y" ]]; then
    rm -rf "$TRASH_DIR"/*
    echo "Trash emptied."
    initialize_trash
  else
    echo "Operation canceled"
  fi
else
  initialize_trash
  echo "Trash emptied"
fi
