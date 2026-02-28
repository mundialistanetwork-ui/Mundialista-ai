\# MUNDIALISTA AI — STATUS \& TROUBLESHOOTING

\# Last Updated: Feb 25, 2026



\## ✅ WHAT'S INSTALLED \& WORKING



| Component        | Version/Model   | Location                                          | Status |

|------------------|-----------------|---------------------------------------------------|--------|

| Python           | 3.14.3          | System-wide                                       | ✅     |

| Ollama           | (latest)        | System-wide                                       | ✅     |

| LLM Model        | llama3.2:3b     | Ollama local                                      | ✅     |

| Nanobot          | 0.1.4.post2     | C:\\Users\\bayen\\mundialista-ai\\nanobot             | ✅     |

| Nanobot venv     | Python 3.14     | C:\\Users\\bayen\\mundialista-ai\\nanobot\\venv        | ✅     |

| Nanobot config   | config.json     | C:\\Users\\bayen\\.nanobot\\config.json               | ✅     |

| Mundialista repo | Python 3.14     | C:\\Users\\bayen\\mundialista-ai                     | ✅     |



\## 🚀 HOW TO START EVERYTHING



\### Step 1: Make sure Ollama is running

Open any PowerShell:

    ollama list

If no models listed or error:

    ollama serve        (leave this window open)

    ollama pull llama3.2:3b



\### Step 2: Activate Nanobot

    cd C:\\Users\\bayen\\mundialista-ai\\nanobot

    .\\venv\\Scripts\\Activate.ps1



You MUST see (venv) in your prompt before nanobot commands work.



\### Step 3: Test Nanobot

    nanobot agent -m "Hello, are you working?"



\### Step 4: Test Football AI

    nanobot agent -m "What formation beats a 4-3-3?"



\## 🔧 TROUBLESHOOTING



\### "nanobot is not recognized"

CAUSE: Venv not activated

FIX:

    cd C:\\Users\\bayen\\mundialista-ai\\nanobot

    .\\venv\\Scripts\\Activate.ps1



\### "No API key configured"

CAUSE: Config file missing or wrong format

FIX: Check config exists:

    type $env:USERPROFILE\\.nanobot\\config.json

If missing, recreate it:

    notepad $env:USERPROFILE\\.nanobot\\config.json



\### "404 page not found"

CAUSE: apiBase missing /v1

FIX: Config must have:

    "apiBase": "http://localhost:11434/v1"



\### "model not found"

CAUSE: Model not pulled or wrong name

FIX:

    ollama list                     (check what's installed)

    ollama pull llama3.2:3b         (if missing)



\### "does not support tools"

CAUSE: Model doesn't support function/tool calling

FIX: Use llama3.2:3b (NOT phi3:mini)



\### "Error calling LLM" / connection refused

CAUSE: Ollama not running

FIX: Open new PowerShell window:

    ollama serve



\### Execution policy error on Activate.ps1

FIX:

    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser



\## 📁 KEY FILE LOCATIONS



    Config:     C:\\Users\\bayen\\.nanobot\\config.json

    Nanobot:    C:\\Users\\bayen\\mundialista-ai\\nanobot\\

    Venv:       C:\\Users\\bayen\\mundialista-ai\\nanobot\\venv\\

    Skills:     C:\\Users\\bayen\\mundialista-ai\\nanobot\\nanobot\\skills\\

    Agent:      C:\\Users\\bayen\\mundialista-ai\\nanobot\\nanobot\\agent\\

    Mundialista: C:\\Users\\bayen\\mundialista-ai\\



\## ⚙️ CURRENT CONFIG (config.json)



{

  "agents": {

    "defaults": {

      "model": "openai/llama3.2:3b",

      "maxTokens": 2048,

      "temperature": 0.3,

      "maxToolIterations": 20,

      "memoryWindow": 50

    }

  },

  "providers": {

    "openai": {

      "apiKey": "ollama",

      "apiBase": "http://localhost:11434/v1"

    }

  },

  "gateway": {

    "host": "0.0.0.0",

    "port": 18790

  }

}



\## 📊 RAM BUDGET (7.6GB Total)



    Windows OS:          ~2.5 GB

    Ollama + llama3.2:   ~2.0 GB

    Mundialista:         ~0.5 GB

    Nanobot:             ~0.3 GB

    Free:                ~2.3 GB



\## 🔜 NEXT STEPS (NOT DONE YET)



1\. \[ ] Confirm nanobot agent talks to Ollama successfully

2\. \[ ] Create mundialista skill in nanobot/skills/mundialista/

3\. \[ ] Wire Nanobot agent to Mundialista match engine via WebSocket

4\. \[ ] First AI-powered match simulation

5\. \[ ] Test full loop: match state → agent decision → engine update



\## 🔄 QUICK HEALTH CHECK (run anytime)



    python --version

    ollama list

    cd C:\\Users\\bayen\\mundialista-ai\\nanobot

    .\\venv\\Scripts\\Activate.ps1

    nanobot agent -m "ping"

    type $env:USERPROFILE\\.nanobot\\config.json







-----------------------------------------------------------


# MUNDIALISTA AI — PROJECT STATUS

\# Last Updated: Feb 25, 2026



\## ✅ COMPLETED



\### Phase 1: Foundation (ch1\_foundations/)

\- Tasks 02-19 completed

\- Output PNGs saved at project root



\### Phase 2: Live Data Integration (Feb 25)

\- Connected results.csv → app.py (replaced hardcoded TEAM\_DATABASE)

\- 258 teams, 4,154 real matches (last 4 years)

\- Head-to-head data included in Bayesian priors

\- Team name aliases: USA→United States, Bosnia→Bosnia and Herzegovina, UAE→United Arab Emirates

\- TEAM\_DATABASE preserved as fallback if CSV missing



\### Phase 3: MCSE Reporting (Feb 25)

\- All probabilities display ± Monte Carlo Standard Error

\- Win/Draw/Loss: ± percentage MCSE

\- xG values: ± standard error

\- Formula: MCSE = sqrt(p \* (1-p) / n)



\### Phase 4: Inference Optimization (Feb 25)

\- Quick Mode toggle: 500 draws, 3,000 sims (~10-15 sec)

\- Full Mode: 2,000 draws, 10,200 sims (~30-60 sec)

\- Posterior caching: same matchup = instant on repeat

\- PyTensor C compiler disabled (permission fix on Windows)



\## 🔜 NEXT TASKS (in order)



1\. Hierarchical Priors

&nbsp;  - Share global attack/defense distribution across all teams

&nbsp;  - Small-sample teams get pulled toward global mean (shrinkage)

&nbsp;  - Improves predictions for obscure teams (Tahiti, Bhutan, etc.)



2\. Nanobot Mundialista Skill

&nbsp;  - AI football manager brain using llama3.2:3b via Ollama

&nbsp;  - Reads match state, suggests tactics/substitutions

&nbsp;  - Adjusts Poisson rates dynamically during simulation

&nbsp;  - Located in nanobot/skills/mundialista/



\## 📁 FILE LOCATIONS



\### Mundialista App

&nbsp;   Main app:       C:\\Users\\bayen\\mundialista-ai\\app.py

&nbsp;   Data loader:    C:\\Users\\bayen\\mundialista-ai\\data\_loader.py

&nbsp;   Match data:     C:\\Users\\bayen\\mundialista-ai\\data\\results.csv

&nbsp;   Goalscorers:    C:\\Users\\bayen\\mundialista-ai\\data\\goalscorers.csv

&nbsp;   Venv:           C:\\Users\\bayen\\mundialista-ai\\venv\\

&nbsp;   Curriculum:     C:\\Users\\bayen\\mundialista-ai\\ch1\_foundations\\



\### Nanobot

&nbsp;   Install:        C:\\Users\\bayen\\mundialista-ai\\nanobot\\

&nbsp;   Venv:           C:\\Users\\bayen\\mundialista-ai\\nanobot\\venv\\

&nbsp;   Config:         C:\\Users\\bayen\\.nanobot\\config.json

&nbsp;   Skills:         C:\\Users\\bayen\\mundialista-ai\\nanobot\\nanobot\\skills\\



\### Ollama

&nbsp;   Model:          llama3.2:3b (2.0 GB)

&nbsp;   Endpoint:       http://localhost:11434/v1



\## 🚀 HOW TO START



\### Run Mundialista App

&nbsp;   cd C:\\Users\\bayen\\mundialista-ai

&nbsp;   .\\venv\\Scripts\\Activate.ps1

&nbsp;   streamlit run app.py



\### Run Nanobot Agent

&nbsp;   cd C:\\Users\\bayen\\mundialista-ai\\nanobot

&nbsp;   .\\venv\\Scripts\\Activate.ps1

&nbsp;   nanobot agent -m "What formation beats a 4-3-3?"



\### Check Ollama

&nbsp;   ollama list

&nbsp;   ollama serve    (if not running)



\## 🔧 TROUBLESHOOTING



\### "nanobot not recognized"

&nbsp;   cd C:\\Users\\bayen\\mundialista-ai\\nanobot

&nbsp;   .\\venv\\Scripts\\Activate.ps1



\### "No module named pandas"

&nbsp;   You're in the wrong venv. Use mundialista venv:

&nbsp;   cd C:\\Users\\bayen\\mundialista-ai

&nbsp;   .\\venv\\Scripts\\Activate.ps1



\### PyTensor PermissionError

&nbsp;   Already fixed: pytensor.config.cxx = "" at top of app.py

&nbsp;   To re-enable C compiler later (faster machine):

&nbsp;   Remove those two lines from top of app.py

&nbsp;   Then: Remove-Item -Recurse -Force "$env:LOCALAPPDATA\\PyTensor\\compiledir\_\*"



\### Execution policy error

&nbsp;   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser



\### IndentationError in app.py

&nbsp;   All code inside main() uses 4-space indentation

&nbsp;   Inside if/elif blocks: 8 spaces

&nbsp;   Inside nested blocks: 12 spaces

&nbsp;   Validate: python -c "import ast; ast.parse(open('app.py', encoding='utf-8').read()); print('OK')"



\## ⚙️ CURRENT CONFIG



\### Nanobot (C:\\Users\\bayen\\.nanobot\\config.json)

{

&nbsp; "agents": {

&nbsp;   "defaults": {

&nbsp;     "model": "openai/llama3.2:3b",

&nbsp;     "maxTokens": 2048,

&nbsp;     "temperature": 0.3,

&nbsp;     "maxToolIterations": 20,

&nbsp;     "memoryWindow": 50

&nbsp;   }

&nbsp; },

&nbsp; "providers": {

&nbsp;   "openai": {

&nbsp;     "apiKey": "ollama",

&nbsp;     "apiBase": "http://localhost:11434/v1"

&nbsp;   }

&nbsp; },

&nbsp; "gateway": {

&nbsp;   "host": "0.0.0.0",

&nbsp;   "port": 18790

&nbsp; }

}



\### app.py Key Constants

&nbsp;   TOTAL\_MINUTES = 90

&nbsp;   NUM\_SIMULATIONS = 10,200 (full) / 3,000 (quick)

&nbsp;   HALF\_TIME = 45

&nbsp;   FINAL\_PUSH\_START = 80

&nbsp;   SEED = 42

&nbsp;   Quick Mode: 500 draws, 500 tune, 2 chains

&nbsp;   Full Mode: 2000 draws, 1000 tune, 2 chains



\## 📊 RAM BUDGET (7.6GB Total)



&nbsp;   Windows OS:          ~2.5 GB

&nbsp;   Ollama + llama3.2:   ~2.0 GB

&nbsp;   Mundialista:         ~0.5 GB

&nbsp;   Nanobot:             ~0.3 GB

&nbsp;   Free:                ~2.3 GB



\## 🔄 QUICK HEALTH CHECK



&nbsp;   python --version                          # Should be 3.14.3

&nbsp;   ollama list                               # Should show llama3.2:3b

&nbsp;   cd C:\\Users\\bayen\\mundialista-ai

&nbsp;   .\\venv\\Scripts\\Activate.ps1

&nbsp;   python -c "from data\_loader import load\_results; r = load\_results(4); print(f'{len(r)} matches')"

&nbsp;   streamlit run app.py



\## 📝 KNOWN LIMITATIONS



\- PyTensor C compiler disabled (slower inference, no permission errors)

\- litellm installed at v1.40.13 (nanobot wants >=1.81.5, works anyway)

\- Python 3.14 is bleeding edge (some packages lack wheels)

\- No rankings.csv file (rankings features disabled)

\- Hierarchical priors not yet implemented (teams estimated independently)

