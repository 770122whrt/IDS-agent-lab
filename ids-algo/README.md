# IDS Algo

## Install

### Option 1: Manual activation

Create and activate a virtual environment:

```bash
python3 -m venv venv

python -m venv venv
```

### 选择你需要的python版本

-> macOS / Linux

```bash
source venv/bin/activate
```

-> Windows PowerShell

```powershell
venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

When you're done working, deactivate:

```bash
deactivate
```

### Option 2: Automatic activation with direnv (MacOS)

Install direnv (if not already installed):

```bash
brew install direnv
```

Add direnv to your shell (add to `~/.zshrc`):

```bash
eval "$(direnv hook zsh)"
```

Create virtual environment and install dependencies:

```bash
make install
```

Allow direnv in this directory:

```bash
direnv allow
```

Now the virtual environment will **automatically activate** when you `cd` into this directory and **automatically deactivate** when you leave.

## Run test

```bash
python -m tests.a
```
