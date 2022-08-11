#!/bin/sh
cd pathhere && poetry shell && poetry install && python manage.py runserver