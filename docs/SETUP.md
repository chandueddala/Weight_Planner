# Installation & Setup Guide

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Installation Steps](#installation-steps)
3. [Environment Configuration](#environment-configuration)
4. [Data Setup](#data-setup)
5. [Running the Application](#running-the-application)
6. [Troubleshooting](#troubleshooting)
7. [Platform-Specific Instructions](#platform-specific-instructions)
8. [Advanced Configuration](#advanced-configuration)

---

## System Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|-------------|
| **Operating System** | Windows 10/11, macOS 10.15+, Ubuntu 20.04+ |
| **Python** | 3.8 or higher (3.10 recommended) |
| **RAM** | 4 GB minimum (8 GB recommended) |
| **Disk Space** | 2 GB free space |
| **Internet** | Stable connection for API calls |
| **Browser** | Chrome, Firefox, Safari, or Edge (latest versions) |

### Software Dependencies

- **Python 3.8+**: [Download Python](https://www.python.org/downloads/)
- **pip**: Python package manager (included with Python)
- **Git**: Version control system (optional, for cloning)
- **OpenAI API Account**: Required for AI features

### Checking Your System

```bash
# Check Python version
python --version
# or
python3 --version

# Check pip version
pip --version
# or
pip3 --version

# Check Git (optional)
git --version
```

---

## Installation Steps

### Option 1: Clone from Repository (Recommended)

#### Step 1: Clone the Repository

```bash
# Using HTTPS
git clone https://github.com/yourusername/Weight_Planner.git

# OR using SSH
git clone git@github.com:yourusername/Weight_Planner.git

# Navigate to the project directory
cd Weight_Planner
```

#### Step 2: Create Virtual Environment

**Windows:**
```bash
# Create virtual environment
python -m venv myenv

# Activate virtual environment
myenv\Scripts\activate

# You should see (myenv) in your terminal prompt
```

**macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv myenv

# Activate virtual environment
source myenv/bin/activate

# You should see (myenv) in your terminal prompt
```

#### Step 3: Install Dependencies

```bash
# Upgrade pip (recommended)
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

**Expected Installation Time**: 5-10 minutes depending on your internet connection.

#### Step 4: Configure Environment Variables

```bash
# Create .env file from template
cp .env.example .env

# Edit .env file with your API key
# Windows: notepad .env
# macOS: nano .env
# Linux: nano .env
```

Add your OpenAI API key:
```env
OPENAI_API_KEY=sk-proj-your-actual-api-key-here
```

#### Step 5: Verify Installation

```bash
# Verify all packages are installed
pip list

# Check if critical packages are present
pip show streamlit
pip show openai
pip show langchain
pip show faiss-cpu
```

### Option 2: Download ZIP Archive

#### Step 1: Download

1. Go to the repository page
2. Click **Code** → **Download ZIP**
3. Extract the ZIP file to your desired location

#### Step 2: Follow Steps 2-5 from Option 1

---

## Environment Configuration

### Creating the .env File

The `.env` file stores sensitive configuration data like API keys.

#### 1. Create the File

```bash
# In the project root directory
touch .env  # macOS/Linux
type nul > .env  # Windows
```

#### 2. Add Configuration

Open `.env` in a text editor and add:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Optional: Additional Configuration
# OPENAI_ORG_ID=org-xxxxxxxxxxxxxxxxxxxxx
# OPENAI_MODEL_NAME=gpt-4-turbo
# STREAMLIT_SERVER_PORT=8501
```

### Getting Your OpenAI API Key

#### Step 1: Create OpenAI Account
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account

#### Step 2: Generate API Key
1. Navigate to **API Keys** section
2. Click **Create new secret key**
3. Name your key (e.g., "Weight Planner App")
4. **IMPORTANT**: Copy the key immediately (you won't see it again)

#### Step 3: Add to .env File
```env
OPENAI_API_KEY=sk-proj-your-copied-key-here
```

### Setting Usage Limits (Recommended)

To avoid unexpected charges:

1. Go to [OpenAI Usage Limits](https://platform.openai.com/account/billing/limits)
2. Set a monthly spending limit (e.g., $10)
3. Enable email notifications for usage alerts

---

## Data Setup

### Required Data Files

The application requires the following data files (included in the repository):

#### 1. Recipe Database

**File**: `Calories/Recipes.csv`

**Description**: Contains 10,000+ recipes with nutritional information

**Location**: `Weight_Planner/Calories/Recipes.csv`

**Verification**:
```bash
# Check if file exists
ls Calories/Recipes.csv

# Windows
dir Calories\Recipes.csv
```

#### 2. Vector Store (FAISS Index)

**Files**:
- `vector/index.faiss` (FAISS binary index)
- `vector/index.pkl` (Metadata)

**Description**: Pre-built embeddings for RAG (Retrieval-Augmented Generation)

**Verification**:
```bash
# Check vector store
ls vector/

# Should show:
# index.faiss
# index.pkl
```

#### 3. Image Assets

**Location**: `images/`

**Files**:
- `CHi6.gif` (Sidebar animation)
- `Male.png` (Male avatar)
- `Female.png` (Female avatar)
- `nutritionist_dietitian_occupation_profession_male_avatar_doctor-512.webp` (Bot avatar)

**Verification**:
```bash
ls images/
```

### Handling Large Files with Git LFS

If you cloned the repository and large files are missing:

```bash
# Install Git LFS
git lfs install

# Pull LFS files
git lfs pull
```

---

## Running the Application

### Method 1: Using main.py (Recommended)

```bash
# Ensure virtual environment is activated
# You should see (myenv) in your prompt

# Run the application
python main.py
```

**Expected Output**:
```
Streamlit app is live at: http://localhost:8501
```

**What Happens**:
1. Launches Streamlit server in headless mode
2. Waits 5 seconds for server startup
3. Displays access URL
4. Browser may auto-open (depending on configuration)

### Method 2: Using Streamlit Directly

```bash
# Activate virtual environment first
# (myenv) should appear in prompt

# Run with Streamlit command
streamlit run Stream_lit_Chat.py
```

**Expected Output**:
```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### Accessing the Application

1. **Automatic**: Browser should open automatically
2. **Manual**: Navigate to `http://localhost:8501` in your browser

### Stopping the Application

**Method 1** (Terminal):
```bash
# Press Ctrl+C in the terminal
Ctrl+C
```

**Method 2** (Close Terminal):
- Simply close the terminal window

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: "Python not found" or "Command not found"

**Symptoms**:
```bash
python: command not found
```

**Solutions**:

**Windows**:
```bash
# Try with py instead
py --version

# Or add Python to PATH
# System Properties → Environment Variables → Edit PATH
# Add: C:\Python310\  (your Python installation path)
```

**macOS/Linux**:
```bash
# Use python3 explicitly
python3 --version

# Create alias (add to ~/.bashrc or ~/.zshrc)
alias python=python3
alias pip=pip3
```

#### Issue 2: "ModuleNotFoundError: No module named 'streamlit'"

**Cause**: Virtual environment not activated or dependencies not installed

**Solution**:
```bash
# 1. Activate virtual environment
myenv\Scripts\activate  # Windows
source myenv/bin/activate  # macOS/Linux

# 2. Reinstall dependencies
pip install -r requirements.txt
```

#### Issue 3: "API key not found" or "Invalid API key"

**Symptoms**:
```
ValueError: OPENAI_API_KEY not set in environment.
```

**Solution**:
```bash
# 1. Check .env file exists
ls .env

# 2. Check .env content
cat .env  # macOS/Linux
type .env  # Windows

# 3. Ensure format is correct
OPENAI_API_KEY=sk-proj-xxxxx
# NO SPACES around =
# NO QUOTES needed

# 4. Restart the application
```

#### Issue 4: "Port 8501 already in use"

**Cause**: Another Streamlit instance is running

**Solution**:

**Option 1** - Kill existing process:
```bash
# Find process using port 8501
# Windows
netstat -ano | findstr :8501

# macOS/Linux
lsof -i :8501

# Kill the process
# Windows
taskkill /PID <process_id> /F

# macOS/Linux
kill -9 <process_id>
```

**Option 2** - Use different port:
```bash
streamlit run Stream_lit_Chat.py --server.port 8502
```

#### Issue 5: "FileNotFoundError: Recipes.csv"

**Cause**: Data files missing or incorrect path

**Solution**:
```bash
# 1. Verify file exists
ls Calories/Recipes.csv

# 2. Check you're in correct directory
pwd  # Should show: /path/to/Weight_Planner

# 3. If file is missing, re-clone repository or download ZIP

# 4. If using Git LFS
git lfs pull
```

#### Issue 6: Vector Store Loading Error

**Symptoms**:
```
RuntimeError: Error in loading FAISS index
```

**Solution**:
```bash
# 1. Check vector files exist
ls vector/index.faiss
ls vector/index.pkl

# 2. Ensure faiss-cpu is installed
pip show faiss-cpu

# 3. Reinstall if needed
pip uninstall faiss-cpu
pip install faiss-cpu==1.12.0

# 4. Pull LFS files if missing
git lfs pull
```

#### Issue 7: Slow Performance or Timeouts

**Causes**:
- Slow internet connection
- OpenAI API rate limits
- Large recipe database loading

**Solutions**:

1. **Check internet connection**
```bash
# Test connectivity
ping openai.com
```

2. **Increase timeout** (edit `weight_planner.py`, `meal_planner.py`):
```python
# Add timeout parameter
response = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[...],
    timeout=60  # Add this line
)
```

3. **Clear Streamlit cache**:
```bash
# In the browser
# Settings (top-right) → Clear cache
```

#### Issue 8: Virtual Environment Issues

**Symptoms**:
- Packages not found even after installation
- Wrong Python version

**Solution**:
```bash
# 1. Deactivate current environment
deactivate

# 2. Remove old environment
rm -rf myenv  # macOS/Linux
rmdir /s myenv  # Windows

# 3. Recreate environment
python -m venv myenv

# 4. Activate
myenv\Scripts\activate  # Windows
source myenv/bin/activate  # macOS/Linux

# 5. Reinstall packages
pip install -r requirements.txt
```

---

## Platform-Specific Instructions

### Windows Setup

#### Prerequisites Installation

1. **Install Python**:
   - Download from [python.org](https://www.python.org/downloads/)
   - **IMPORTANT**: Check "Add Python to PATH" during installation

2. **Verify Installation**:
```cmd
python --version
pip --version
```

#### Complete Setup

```cmd
# 1. Clone or download project
git clone https://github.com/yourusername/Weight_Planner.git
cd Weight_Planner

# 2. Create virtual environment
python -m venv myenv

# 3. Activate virtual environment
myenv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create .env file
type nul > .env
notepad .env

# 6. Add API key in notepad, save and close

# 7. Run application
python main.py
```

### macOS Setup

#### Prerequisites Installation

1. **Install Homebrew** (if not installed):
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. **Install Python**:
```bash
brew install python@3.10
```

3. **Verify Installation**:
```bash
python3 --version
pip3 --version
```

#### Complete Setup

```bash
# 1. Clone or download project
git clone https://github.com/yourusername/Weight_Planner.git
cd Weight_Planner

# 2. Create virtual environment
python3 -m venv myenv

# 3. Activate virtual environment
source myenv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create .env file
touch .env
nano .env

# 6. Add API key in nano:
# Type: OPENAI_API_KEY=sk-proj-xxxxx
# Press: Ctrl+O (save), Enter, Ctrl+X (exit)

# 7. Run application
python main.py
```

### Linux (Ubuntu/Debian) Setup

#### Prerequisites Installation

```bash
# Update package list
sudo apt update

# Install Python and pip
sudo apt install python3.10 python3-pip python3-venv

# Install Git (if needed)
sudo apt install git

# Verify installation
python3 --version
pip3 --version
```

#### Complete Setup

```bash
# 1. Clone or download project
git clone https://github.com/yourusername/Weight_Planner.git
cd Weight_Planner

# 2. Create virtual environment
python3 -m venv myenv

# 3. Activate virtual environment
source myenv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create .env file
touch .env
nano .env

# 6. Add API key, save with Ctrl+O, exit with Ctrl+X

# 7. Run application
python main.py
```

---

## Advanced Configuration

### Customizing Streamlit Settings

Create `.streamlit/config.toml`:

```bash
mkdir -p .streamlit
nano .streamlit/config.toml
```

Add configuration:

```toml
[server]
port = 8501
headless = true
enableCORS = false
enableXsrfProtection = true

[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[browser]
gatherUsageStats = false
```

### Environment Variable Alternatives

Instead of `.env` file, you can set environment variables:

**Windows (PowerShell)**:
```powershell
$env:OPENAI_API_KEY="sk-proj-xxxxx"
python main.py
```

**Windows (CMD)**:
```cmd
set OPENAI_API_KEY=sk-proj-xxxxx
python main.py
```

**macOS/Linux**:
```bash
export OPENAI_API_KEY="sk-proj-xxxxx"
python main.py
```

### Running on Different Port

```bash
streamlit run Stream_lit_Chat.py --server.port 8080
```

### Enabling Network Access

To access from other devices on the same network:

```bash
streamlit run Stream_lit_Chat.py --server.address 0.0.0.0
```

Then access via: `http://<your-local-ip>:8501`

### Running in Background (Linux/macOS)

```bash
# Using nohup
nohup python main.py > app.log 2>&1 &

# View logs
tail -f app.log

# Stop
pkill -f streamlit
```

---

## Docker Deployment (Optional)

### Create Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "Stream_lit_Chat.py", "--server.headless", "true"]
```

### Build and Run

```bash
# Build image
docker build -t weight-planner .

# Run container
docker run -p 8501:8501 -e OPENAI_API_KEY=sk-xxx weight-planner
```

---

## Verification Checklist

After installation, verify:

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed (`pip list`)
- [ ] `.env` file created with valid API key
- [ ] Recipe CSV file present (`Calories/Recipes.csv`)
- [ ] Vector store files present (`vector/index.faiss`, `vector/index.pkl`)
- [ ] Image assets present (`images/`)
- [ ] Application starts without errors
- [ ] Browser opens to `http://localhost:8501`
- [ ] UI loads successfully
- [ ] Can submit user profile form
- [ ] Weight forecast displays
- [ ] Meal plan generates
- [ ] Chat interface accessible

---

## Getting Help

If you encounter issues not covered here:

1. **Check logs**: Terminal output for error messages
2. **GitHub Issues**: [Report an issue](https://github.com/yourusername/Weight_Planner/issues)
3. **Discussions**: [Ask the community](https://github.com/yourusername/Weight_Planner/discussions)
4. **Email Support**: your.email@example.com

---

## Next Steps

After successful installation:

1. Read [README.md](../README.md) for feature overview
2. Review [ARCHITECTURE.md](ARCHITECTURE.md) for system understanding
3. Check [CODE_DOCUMENTATION.md](CODE_DOCUMENTATION.md) for code details
4. Explore [API_REFERENCE.md](API_REFERENCE.md) for function documentation

---

**Last Updated**: December 2025
**Version**: 1.0
