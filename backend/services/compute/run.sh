#!/usr/bin/env bash

uwsgi --http-socket 0.0.0.0:5001 --master --workers 1 --module service.compute.service:app --vacuum --die-on-term