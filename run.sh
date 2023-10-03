#! /usr/bin/bash

uvicorn app.server:app --host 0.0.0.0 --port 3000 --reload
