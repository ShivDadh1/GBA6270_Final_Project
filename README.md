# DevOps Integration Workflow - WebEx Bot → spaCy → ServiceNow

## Overview
This project implements an automation pipeline that listens to WebEx messages (mentions), uses spaCy NLP to classify and extract entities, creates incidents in ServiceNow, and replies back to the WebEx room. It is containerized with Docker and includes CI workflow example and documentation.

## Files in this package
- bot_code.py           : Main bot application
- spacy_module.py       : spaCy-based classification & entity extraction
- requirements.txt      : Python dependencies
- Dockerfile            : Container image definition
- documentation.pdf     : Project documentation (human readable)
- presentation.pptx     : Slide deck for final presentation
- workflow_diagram.png  : Visual diagram of integration
- .github/workflows/ci.yml : Example GitHub Actions workflow (CI)
- README.md             : This file

## Environment variables (required)
- WEBEX_TOKEN : WebEx Bot token
- ROOM_ID : WebEx Room ID where the bot listens (use room where bot is a member)
- SERVICENOW_INSTANCE : ServiceNow base URL, e.g. https://dev123456.service-now.com
- SERVICENOW_USER : ServiceNow username
- SERVICENOW_PASSWORD : ServiceNow password
- POLL_INTERVAL : (optional) poll interval in seconds (default: 2)

## Running locally (recommended for testing)
1. Create a Python virtualenv:
   python -m venv venv
   source venv/bin/activate
2. Install dependencies:
   pip install -r requirements.txt
3. Ensure spaCy model is installed:
   python -m spacy download en_core_web_sm
4. Export env vars and run:
   export WEBEX_TOKEN=your_token
   export ROOM_ID=your_room_id
   export SERVICENOW_INSTANCE=https://devXXXX.service-now.com
   export SERVICENOW_USER=admin
   export SERVICENOW_PASSWORD=securepassword
   python bot_code.py

## Docker
Build image:
  docker build -t webex-sn-bot:latest .

Run container (pass envs):
  docker run -e WEBEX_TOKEN=$WEBEX_TOKEN -e ROOM_ID=$ROOM_ID \ 
    -e SERVICENOW_INSTANCE=$SERVICENOW_INSTANCE -e SERVICENOW_USER=$SERVICENOW_USER \
    -e SERVICENOW_PASSWORD=$SERVICENOW_PASSWORD webex-sn-bot:latest

## CI (GitHub Actions)
An example workflow lives at `.github/workflows/ci.yml` — it runs tests and linting.

## Notes and security
- Do NOT commit tokens or credentials in source control.
- Use secret management in CI/CD and container platforms.
- ServiceNow credentials used here should be scoped to a dedicated integration user with least privilege.
