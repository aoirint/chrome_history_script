#!/bin/bash

set -eux

DATE_STRING=$(date '+%Y-%m-%d_%H-%M-%S')

mkdir -p work

cp "$HOME/.config/google-chrome/Default/History" "work/Chrome_History_${DATE_STRING}.sqlite3"
