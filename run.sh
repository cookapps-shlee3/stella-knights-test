#!/bin/bash
export PRODUCTION='dev'
python3 ~/.local/bin/gunicorn -k uvicorn.workers.UvicornWorker app.main:app --reload --daemon -p gunicorn.pid
