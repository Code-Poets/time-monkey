#!/usr/bin/env bash
python manage.py loaddata employees/fixtures/activities.yaml
python manage.py load_initial_data
