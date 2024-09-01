#!/bin/bash

set -ex

for f in */checker.py; do
    echo $f
    chmod +x $f
done