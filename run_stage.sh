#!/bin/bash
export PRODUCTION='stage'
/home/ec2-user/venv/bin/gunicorn -k uvicorn.workers.UvicornWorker app.main:app --reload --daemon -p gunicorn.pid
