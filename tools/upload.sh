#!/usr/bin/env bash
cd "$(dirname "${BASH_SOURCE[0]}")"
cd ..
git add *
git commit -m "auto commit"
git push origin main
