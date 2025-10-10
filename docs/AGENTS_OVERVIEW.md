# LexiQ Agents - Overview

## Quick Reference

LexiQ uses 4 AI agents to provide comprehensive legal analysis:

### 1. 🏛️ Precedent Analysis (Main Agent)
**Purpose:** Find similar case precedents  
**Input:** Case text/file  
**Output:** AI analysis with similar cases, citations, page numbers, PDF links  
**Usage:**
```python
from utils.case_similarity import CaseSimilarityAnalyzer
analyzer = CaseSimilarityAnalyzer()
analyzer.initialize()
result = analyzer.analyze_case_from_text(case_text, k=5)
```

---

### 2. ⚖️ Statute Reference Agent
**Purpose:** Extract and explain legal provisions  
**Input:** Case text  
**Output:** Extracted articles/sections + plain-English explanations  
**Coverage:** Articles, IPC, CrPC, CPC, IT Act, Evidence Act, CGST  
**Usage:**
```python
from agents.statute_reference_agent import StatuteReferenceAgent
agent = StatuteReferenceAgent()
result = agent.analyze_statutes(case_text)
print(f"Found {result['num_provisions']} provisions")
```

**Example Output:**
- Article 21 of Constitution of India
- Section 302 of IPC
- Section 154 of CrPC

---

### 3. 📰 News Relevance Agent
**Purpose:** Find current events related to case  
**Input:** Case text  
**Output:** 3-5 relevant news articles + legal analysis  
**Features:** Auto keyword extraction, multi-country support, configurable time periods  
**Usage:**
```python
from agents.news_relevance_agent import NewsRelevanceAgent
agent = NewsRelevanceAgent(max_results=5, period='7d')
result = agent.find_relevant_news(case_text)
print(f"Found {result['num_articles']} articles")
```

---

### 4. 👨‍⚖️ Bench Bias Agent
**Purpose:** Analyze judge patterns from precedents  
**Input:** Similar cases from precedent agent  
**Output:** Judge statistics + pattern analysis  
**Usage:**
```python
from agents.bench_bias_agent import BenchBiasAgent
agent = BenchBiasAgent()
result = agent.analyze_bench_from_cases(similar_cases)
print(f"Analyzed {result['num_judges']} judges")
```

---

## Running All Agents

### CLI - Multi-Agent Orchestrator
```bash
python multi_agent_orchestrator.py
```
Runs all agents on same case input, displays results sequentially.

### UI - Streamlit Interface
```bash
streamlit run app_ui.py
```
Web interface with tabs for each agent. Enable/disable agents in sidebar.

### Programmatic
```python
from multi_agent_orchestrator import MultiAgentOrchestrator

orchestrator = MultiAgentOrchestrator(
    enable_news=True,
    enable_statutes=True,
    enable_bench=True
)
orchestrator.initialize()

results = orchestrator.analyze_case_complete(case_text, k_precedents=5)

# Access results
print(results['precedents']['analysis'])
print(results['statutes']['explanation'])
print(results['news']['analysis'])
print(results['bench']['analysis'])
```

---

## Architecture

```
User Input (Case Text/File)
         ↓
┌────────────────────────────┐
│ Multi-Agent Orchestrator   │
└────────────────────────────┘
         ↓
    ┌────────────────────────────────┐
    │   1. Precedent Analysis        │ ← Main Agent (Always runs)
    │   - FAISS vector search        │
    │   - Claude AI analysis         │
    └────────────────────────────────┘
         ↓
    ┌────────────────────────────────┐
    │   2. Statute Reference         │ ← Optional
    │   - Regex extraction           │
    │   - Claude explanations        │
    └────────────────────────────────┘
         ↓
    ┌────────────────────────────────┐
    │   3. News Relevance            │ ← Optional
    │   - Entity extraction          │
    │   - GNews API search           │
    │   - Claude analysis            │
    └────────────────────────────────┘
         ↓
    ┌────────────────────────────────┐
    │   4. Bench Bias                │ ← Optional (needs precedents)
    │   - Judge extraction           │
    │   - Pattern analysis           │
    └────────────────────────────────┘
         ↓
    UI Tabs: Precedents | Statutes | News | Bench
```

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run Streamlit UI
streamlit run app_ui.py

# Or use CLI
python multi_agent_orchestrator.py
```

---

## Individual Agents (Standalone)

Each agent can run independently:

```bash
# Precedent analysis only
python case_analyzer.py

# Statute analysis only
python statute_analyzer.py

# News analysis only
python news_analyzer.py
```

---

## Configuration

**Precedents:**
- `k`: Number of cases (1-20)
- `max_tokens`: Response detail (1000-3000)

**Statutes:**
- Automatically extracts all provisions
- `max_tokens`: Explanation detail

**News:**
- `max_results`: Articles (1-10)
- `period`: '7d', '14d', '30d'
- `country`: 'US', 'GB', 'IN', 'CA', 'AU'

**Bench:**
- Depends on precedent results
- Analyzes top 5 most active judges

---

## API Endpoints (Future)

Add to Flask API for web integration:

```python
# Add to case_api.py
@app.route('/api/multi-agent-analysis', methods=['POST'])
def multi_agent_analysis():
    data = request.json
    orchestrator = MultiAgentOrchestrator()
    orchestrator.initialize()
    results = orchestrator.analyze_case_complete(
        data['case_text'], 
        k_precedents=data.get('k', 5)
    )
    return jsonify(results)
```

---

## Files

- `agents/news_relevance_agent.py` - News agent
- `agents/statute_reference_agent.py` - Statute agent
- `agents/bench_bias_agent.py` - Bench bias agent
- `multi_agent_orchestrator.py` - CLI orchestrator
- `app_ui.py` - Streamlit UI
- Individual CLIs: `news_analyzer.py`, `statute_analyzer.py`

---

## Dependencies

```
boto3              # AWS Bedrock (Claude)
faiss-cpu          # Vector search
gnews              # News scraping
spacy              # NER (optional)
streamlit          # UI
```

