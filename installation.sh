#!/bin/bash

filename="trsh" 

if [ -e trsh ]; then
  chmod +x "$filename"
  sudo cp -f trsh /usr/local/bin
  echo -e "\033[1;32mSuccess:\033[0m Installation completed successfully."
  echo -e "See \033[1;32mtrsh\033[0m or \033[1;32mtrsh --help\033[0m  for more informations"
  exit 0
else
  echo -e "\033[1;31mError:\033[0m Installation failed."
  echo -e "\033[1;34mReason:\033[0m The required file '\033[1;33m$filename\033[0m' is missing."
  echo -e "\033[1;35mSuggested Actions:\033[0m"
  echo -e "   - Make sure the file '\033[1;33m$filename\033[0m' is available."
  echo -e "   - Check existence of \"/usr/local/bin\" in PATH environment variable"
  echo -e "   - Retry the installation."
  echo -e "If the issue persists, please get a proper clone of this repository at https://github.com/elias-ba/trsh"
  exit 1
fi
