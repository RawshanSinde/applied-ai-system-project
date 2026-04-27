# Complete Setup & Installation Guide

This guide ensures the Music Recommender System can be run correctly and reproducibly on any machine.

## System Requirements

- **Python**: 3.10 or higher (3.14+ recommended)
- **Operating System**: macOS, Linux, or Windows
- **RAM**: 2GB minimum
- **Disk Space**: 500MB

## Step 1: Verify Python Installation

```bash
python3 --version
```

Should output: `Python 3.10.x` or higher

If Python 3 is not installed:
- **macOS**: `brew install python3`
- **Ubuntu/Debian**: `sudo apt-get install python3`
- **Windows**: Download from [python.org](https://www.python.org/downloads/)

## Step 2: Clone the Repository

```bash
cd /path/to/your/workspace
git clone https://github.com/YourUsername/applied-ai-system-project.git
cd applied-ai-system-project
```

## Step 3: Create a Virtual Environment (Recommended)

Virtual environments isolate project dependencies and prevent conflicts.

### Option A: Using `venv` (Built-in)

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows
```

### Option B: Using `conda` (If installed)

```bash
conda create -n recommender python=3.10
conda activate recommender
```

### Verify Virtual Environment

```bash
which python      # Should show venv path
python --version  # Should show 3.10+
```

## Step 4: Install Dependencies

```bash
pip install --upgrade pip setuptools wheel  # (Optional but recommended)
pip install -r requirements.txt
```

**What gets installed:**
- `pandas==2.0.3` — Data processing
- `pytest==7.4.0` — Testing
- `streamlit==1.28.0` — Web UI (optional)
- `openai==1.3.0` — LLM API client
- `python-dotenv==1.0.0` — Environment variable management

### Verify Installation

```bash
python -c "import pandas, openai, dotenv; print('✓ All packages installed')"
```

Should output: `✓ All packages installed`

## Step 5: Set Up OpenAI API Key

### Get an API Key

1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Sign in (create account if needed)
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

### Configure Environment Variable

```bash
# Create .env file in project root
cp .env.example .env

# Edit .env and add your key
# macOS/Linux
nano .env

# Add this line:
OPENAI_API_KEY=sk-your-actual-key-here

# Save (Ctrl+O, Enter, Ctrl+X for nano)
```

**⚠️ IMPORTANT**: Never commit `.env` to git. It's protected by `.gitignore`.

### Verify API Key

```bash
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print('✓ API Key loaded' if os.getenv('OPENAI_API_KEY') else '✗ API Key not found')"
```

Should output: `✓ API Key loaded`

## Step 6: Run the Application

### Start the Music Recommender

```bash
cd src
python main.py
```

**Expected output:**
```
======================================================================
Starting Music Recommender System
======================================================================

✓ Loaded 20 songs from catalog
📝 Using AI-powered explanations from OpenAI

============================================================
  TOP RECOMMENDATIONS — High-Energy Pop
============================================================

#1  Sunrise City — Neon Echo
     Score : 0.75 / 1.00
     Genre : pop   Mood: happy
     Why   :
             • This track has the high-energy vibe you love! ...
...
```

### Run Without AI (Fallback Mode)

If you don't have an API key or want to test without API calls:

```bash
cd src
python main.py --no-ai
```

## Step 7: Run Integration Tests

Verify everything works correctly:

```bash
python ../test_rag_integration.py
```

**Expected output:**
```
==================================================
✅ All tests passed!
==================================================
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'openai'"

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # macOS/Linux

# Reinstall packages
pip install -r requirements.txt
```

### "OpenAI API key not found"

```bash
# Verify .env file exists
ls -la .env

# Verify content
cat .env  # Should show OPENAI_API_KEY=sk-...

# Check it's in project root, not in src/
pwd  # Should be .../applied-ai-system-project/
```

### "FileNotFoundError: data/songs.csv"

```bash
# Make sure you're in the correct directory
pwd  # Should end with: .../applied-ai-system-project

# Verify data exists
ls data/songs.csv
```

### API Rate Limits

OpenAI free tier has rate limits. If you get rate limit errors:
- Wait a few minutes before retrying
- Use `--no-ai` mode for testing
- Consider upgrading to paid tier for production use

### Slow API Responses

OpenAI API responses can take 2-5 seconds. This is normal.

## File Structure for Reference

```
applied-ai-system-project/
├── .env                          # Your API key (NOT in git)
├── .env.example                  # Template for .env
├── .gitignore                    # Protects secrets
├── requirements.txt              # Exact package versions
├── data/
│   └── songs.csv                # 20 song database
├── src/
│   ├── main.py                  # Entry point
│   ├── recommender.py           # Core recommendation logic
│   ├── rag.py                   # RAG module (AI explanations)
│   └── logger_config.py         # Logging configuration
├── tests/
│   └── test_recommender.py      # Unit tests
├── logs/                        # Generated at runtime
│   └── music_recommender_*.log  # Timestamped logs
├── README.md                    # Project overview
├── RAG_SETUP.md                # RAG-specific guide
├── RAG_IMPLEMENTATION.md       # Implementation details
└── SETUP.md                    # This file
```

## Logging

All activity is logged to `logs/` directory:

```bash
# View latest log
tail logs/music_recommender_*.log

# Follow logs in real-time
tail -f logs/music_recommender_*.log
```

Logs include:
- ✓ Success messages
- ⚠️ Warnings (e.g., API fallbacks)
- ✗ Errors with stack traces

## Running on Different Systems

### macOS M1/M2 Macs

```bash
# Might need to specify architecture
arch -arm64 python3 -m venv venv
```

### Docker (Optional)

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "src/main.py"]
```

### GitHub Actions (CI/CD)

```yaml
name: Test
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: python test_rag_integration.py
```

## Next Steps

1. ✅ Complete setup above
2. 📝 Read [README.md](README.md) for project overview
3. 🎯 Read [RAG_SETUP.md](RAG_SETUP.md) for RAG system details
4. 🧪 Run integration tests to verify setup
5. 🚀 Run `python src/main.py` to see recommender in action

## Support

If you encounter issues:

1. Check the error message and this guide
2. Search the logs in `logs/` directory
3. Try `python src/main.py --no-ai` to isolate API issues
4. Run `python test_rag_integration.py` to verify setup

## Notes

- All code includes comprehensive logging and error handling
- Empty `logs/` directory is auto-created at runtime
- API calls cost ~$0.001 per recommendation
- No GPU required
- Works offline with `--no-ai` flag

---

**Status: Ready to use!** 🎉

Once setup is complete, run: `cd src && python main.py`
