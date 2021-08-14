@echo off
del /f /q *.mp3
del /f /q *.mp4
rd /s /q __pycache__
rd /q __pycache__
rd /s /q build
rd /q build
rd /s /q dist
rd /q dist
del main.spec
echo Clean Cache Sucessfully!
pause