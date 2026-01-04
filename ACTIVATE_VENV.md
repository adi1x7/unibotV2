# How to Activate the Virtual Environment

## Windows

### PowerShell (Recommended)
```powershell
cd C:\Users\novap\Desktop\unibot_\unibot_
.\venv\Scripts\Activate.ps1
```

If you get an execution policy error, run this first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Command Prompt (CMD)
```cmd
cd C:\Users\novap\Desktop\unibot_\unibot_
venv\Scripts\activate.bat
```

## Linux/Mac

```bash
cd ~/Desktop/unibot_/unibot_
source venv/bin/activate
```

## Verify Activation

After activation, you should see `(venv)` at the beginning of your command prompt:
```
(venv) PS C:\Users\novap\Desktop\unibot_\unibot_>
```

## Install/Update Dependencies

After activating, install dependencies:
```bash
pip install -r requirements.txt
```

## Deactivate

To exit the virtual environment:
```bash
deactivate
```

## Quick Start Script

You can also create a simple activation script. For Windows, create `activate.bat`:

```batch
@echo off
cd /d %~dp0
call venv\Scripts\activate.bat
```

Then just run `activate.bat` from the project directory.

