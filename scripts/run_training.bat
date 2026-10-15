@echo off
title SecureFlowAI - Model Training Terminal
cd /d "c:\Users\RUSHIKESH\SecureFLowAI"
echo ================================================================================
echo  SecureFlowAI Banking DLP Model Training - Epoch 1
echo  Anti-Cheating Sanitization: ENABLED
echo  Auto-Checkpointing: Every 500 steps + Every Epoch
echo ================================================================================
echo.
.\.venv\Scripts\python.exe -u ai-service/models/scripts/train_banking_classifier.py --dataset_name_or_path ./dataset_output --epochs 1 --batch_size 16 --save_strategy steps --save_steps 500 --save_total_limit 10
echo.
echo ================================================================================
echo  Training session complete or paused. Checkpoints saved in models/checkpoints.
echo ================================================================================
pause
