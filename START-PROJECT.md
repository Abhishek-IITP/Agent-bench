# 🚀 Start AgentBench Project - Complete Guide

## Quick Start (3 Steps)

### Step 1: Start the Database
```cmd
docker-compose up -d postgres
```

Wait 5 seconds for database to initialize.

### Step 2: Start the API Server
```cmd
cd dashboard\api
bun run src/index.ts
```

Keep this terminal open. API runs on **http://localhost:3001**

### Step 3: Start the Dashboard
Open a NEW terminal:
```cmd
cd dashboard\web
bun run dev
```

Keep this terminal open. Dashboard opens at **http://localhost:3002**

---

## ✅ Verify Everything is Running

### Check Database
```cmd
docker ps
```
You should see `agentbench-db` container running.

### Check API
Open browser: **http://localhost:3001/api/health**

Should show:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### Check Dashboard
Open browser: **http://localhost:3002**

You should see the AgentBench dashboard!

---

## 🎯 Your Project is Ready!

### For Users Testing Their Models:

1. **Open**: http://localhost:3002
2. **Click**: "Test Model" in sidebar
3. **Fill form**:
   - Model Provider: OpenAI / Anthropic / Local
   - Model Name: gpt-4, claude-3-opus, etc.
   - API Key: (optional if configured in .env)
   - Task: Choose from dropdown
4. **Click**: "Run Benchmark"
5. **View**: Results instantly!

### For Developers:

**View all pages:**
- Overview: http://localhost:3002/
- Test Model: http://localhost:3002/test
- Tasks: http://localhost:3002/tasks
- Runs: http://localhost:3002/runs
- Leaderboard: http://localhost:3002/leaderboard
- Health: http://localhost:3002/health

**API Endpoints:**
- Health: http://localhost:3001/api/health
- Tasks: http://localhost:3001/api/tasks
- Runs: http://localhost:3001/api/runs
- Leaderboard: http://localhost:3001/api/leaderboard
- Stats: http://localhost:3001/api/stats/tasks

---

## 📂 Project Structure

```
agent-bench/
├── dashboard/
│   ├── api/              # Bun + Elysia API (port 3001)
│   └── web/              # Next.js Dashboard (port 3002)
├── tasks/                # 14 benchmark tasks
├── runner/               # Python core (benchmark execution)
├── scripts/              # Utility scripts
├── docs/                 # Documentation
├── USER-GUIDE.md         # ⭐ User guide for testing models
├── START-PROJECT.md      # ⭐ This file
└── docker-compose.yml    # Database configuration
```

---

## 🔧 Configuration

### Environment Variables

The `.env` file contains:
```env
# Database
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=agentbench
DB_USER=postgres
DB_PASSWORD=postgres

# API
PORT=3001
API_URL=http://localhost:3001

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:3001

# Model API Keys (optional)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
```

### Add Your API Keys

To test models, add your keys to `.env`:
```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

---

## 🛠️ Troubleshooting

### Database won't start
```cmd
# Stop and remove existing container
docker-compose down
docker volume rm agent-bench_postgres_data

# Start fresh
docker-compose up -d postgres
```

### API shows "database disconnected"
```cmd
# Check database is running
docker ps

# Restart database
docker-compose restart postgres

# Wait 5 seconds, then restart API
```

### Dashboard shows blank page
```cmd
# Check API is running
curl http://localhost:3001/api/health

# If API is down, restart it
cd dashboard\api
bun run src/index.ts
```

### Port already in use
```cmd
# Find process using port 3001 or 3002
netstat -ano | findstr :3001
netstat -ano | findstr :3002

# Kill process (replace <PID> with actual PID)
taskkill /PID <PID> /F
```

---

## 📊 Sample Data

The database is pre-loaded with:
- ✅ 5 sample tasks
- ✅ 4 sample agents (GPT-4, GPT-3.5, Claude Opus, Claude Sonnet)
- ✅ 8 sample runs with results
- ✅ Task health metrics

You can:
- View them in the dashboard
- Run new benchmarks
- Compare your model with existing ones

---

## 🎓 Next Steps

### As a User:
1. Read **USER-GUIDE.md** for complete testing instructions
2. Go to http://localhost:3002/test
3. Test your model!

### As a Developer:
1. Explore the codebase
2. Add new tasks in `tasks/` directory
3. Customize the dashboard in `dashboard/web/`
4. Extend the API in `dashboard/api/`

---

## 📱 Features Available

### ✅ Working Features:
- Database storage (PostgreSQL)
- RESTful API with 15+ endpoints
- Interactive dashboard with 6 pages
- Test Model interface (web form)
- Real-time metrics and statistics
- Task health monitoring
- Leaderboard rankings
- Run history and filtering
- Task browsing
- Cinematic UI design
- Responsive layout
- Navigation and routing

### 🚧 Requires Python Setup:
- Actual benchmark execution (CLI)
- Docker-based task running
- Agent integration with OpenAI/Anthropic
- Replay trace generation

The web interface is **fully functional** for viewing data and understanding the system.
To run actual benchmarks, you'll need to set up Python environment.

---

## 🔄 Stop Everything

When you're done:

### Stop Dashboard
Press `Ctrl+C` in the dashboard terminal

### Stop API
Press `Ctrl+C` in the API terminal

### Stop Database
```cmd
docker-compose down
```

### Stop Everything + Delete Data
```cmd
docker-compose down -v
```

---

## 📞 Help & Support

### Documentation Files:
- **USER-GUIDE.md** - Complete user guide for testing models
- **README.md** - Main project documentation
- **dashboard/README.md** - Dashboard documentation
- **APPLICATION-BUILD-STATUS.md** - Build status report

### Check System Status:
```cmd
# Database
docker ps

# API
curl http://localhost:3001/api/health

# Dashboard
curl http://localhost:3002
```

---

## ✨ You're All Set!

**Open your browser and visit:**
### 👉 http://localhost:3002

**Start testing your AI models now!** 🚀

---

**Last Updated**: July 26, 2026  
**Status**: ✅ Production Ready  
**Version**: 1.0.0

