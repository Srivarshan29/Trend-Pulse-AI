#!/bin/bash
echo "Ensuring pip is installed..."
python3 -m ensurepip || (curl -sS https://bootstrap.pypa.io/get-pip.py | python3)

echo "Installing dependencies..."
python3 -m pip install -r requirements.txt

echo "Starting FastAPI backend..."
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 &

echo "Starting Streamlit frontend..."
python3 -m streamlit run app.py --server.port 3000 --server.address 0.0.0.0

