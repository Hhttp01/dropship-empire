@echo off
title EmpireOS Control Center
echo Starting EmpireOS Autonomous Server...
echo ---------------------------------------
:: בדיקה אם הספריות מותקנות
pip install -r requirements.txt
:: הרצת השרת
python main.py
pause
