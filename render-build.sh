#!/usr/bin/env bash

echo "===== BUILD START ====="

apt-get update

apt-get install -y tesseract-ocr

which tesseract

tesseract --version

pip install -r requirements.txt

echo "===== BUILD COMPLETE ====="