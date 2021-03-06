#!/bin/bash

DEMO_DIR="demo"

command -v kaylee-admin.py >/dev/null 2>&1 || { echo >&2 "I require Kaylee, but it has not been found. Aborting."; exit 1; }
command -v coffee >/dev/null 2>&1 || { echo >&2 "I require CoffeeScript compiler, but it has not been found. Aborting."; exit 1; }
command -v python -c "import PIL" >/dev/null 2>&1 || { echo >&2 "I require pillow (PIL fork for Python3), but it has not been found. Aborting."; exit 1; }

run() {
    python klmanage.py build || exit 1;
    python klmanage.py run --debug
}

if [ -d "$DEMO_DIR" ]; then
    # Run the demo if it has already been created
    cd $DEMO_DIR
    run
else
    # start Kaylee environment
    kaylee-admin.py startenv demo || exit 1;
    # copy the projects to the environment
    cp -r src/* demo
    cd $DEMO_DIR
    run
fi
