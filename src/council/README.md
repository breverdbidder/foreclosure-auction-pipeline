# AI Council Ecosystem
## Multi-Agent Decision Intelligence for Shapira Ventures

> **"The future of AI assistance isn't a single, all-knowing oracle—it's a council of specialized perspectives working together to illuminate the path forward."**

---

## 🎯 Overview

The AI Council is a multi-agent decision intelligence framework that brings diverse analytical perspectives to complex decisions. Based on Mark Kashef's methodology, it implements **distributed cognition** through specialized agents that analyze, debate, and synthesize recommendations.

### Supported Platforms

| Platform | Use Case | Decision Output |
|----------|----------|-----------------|
| **BidDeed.AI** | Foreclosure auction analysis | BID / REVIEW / SKIP |
| **ZoneWise** | Zoning feasibility studies | GO / CONDITIONAL GO / NO-GO |
| **SPD** | Site plan approval assessment | APPROVE / REVISE / REJECT |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│           TIER 3: EXECUTIVE SYNTHESIS                        │
│           - Reads all analyses                               │
│           - Resolves conflicts                               │
│           - Produces final recommendation                    │
└─────────────────────────────────────────────────────────────┘
                            ↑
┌─────────────────────────────────────────────────────────────┐
│           TIER 2: PERSPECTIVE AGENTS                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ BULL CASE│  │ BEAR CASE│  │ ANALYST  │                  │
│  │ Optimist │  │ Skeptic  │  │ Neutral  │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
└─────────────────────────────────────────────────────────────┘
                            ↑
┌─────────────────────────────────────────────────────────────┐
│           TIER 1: SPECIALIST AGENTS                          │
│  Platform-specific domain experts                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install langgraph httpx pydantic supabase
```

### 2. Set Environment Variables

```bash
export GEMINI_API_KEY="your-gemini-key"
export ANTHROPIC_API_KEY="your-anthropic-key"  # For executive synthesis
export SUPABASE_URL="your-supabase-url"
export SUPABASE_SERVICE_KEY="your-supabase-key"
```

### 3. Run a Council Session

```bash
python src/council_workflow.py \
  --platform biddeed \
  --subject "123 Ocean Ave, Satellite Beach, FL" \
  --query "Evaluate for December foreclosure auction" \
  --context '{"judgment": 150000, "arv": 350000}'
```

### 4. GitHub Actions (Automated)

Trigger via workflow dispatch or repository dispatch:

```bash
# Via GitHub CLI
gh workflow run council_analysis.yml \
  -f platform=biddeed \
  -f subject="123 Ocean Ave" \
  -f query="Evaluate for auction"
```

---

## 📁 File Structure

```
ai-council-ecosystem/
├── docs/
│   └── AI_COUNCIL_ECOSYSTEM.md    # Full architecture documentation
├── src/
│   ├── council_prompts.py         # Agent definitions and prompts
│   └── council_workflow.py        # LangGraph orchestration
├── .github/
│   └── workflows/
│       └── council_analysis.yml   # GitHub Actions workflow
├── supabase_schema.sql            # Database schema
└── README.md                      # This file
```

---

## 🤖 Agent Roles

### Tier 1: Specialists (Platform-Specific)

**BidDeed.AI:**
- **Title Agent**: Lien priority, title defects
- **Repair Agent**: Condition assessment, cost estimation
- **Exit Agent**: Strategy optimization (flip/MTR/wholesale)

**ZoneWise:**
- **Zoning Agent**: Code interpretation, use permissions
- **HBU Agent**: Highest and best use analysis

**SPD:**
- **Approval Agent**: Compliance checking, approval probability

### Tier 2: Perspectives (Cross-Platform)

- **Bull Case**: Opportunity finder, best-case scenarios
- **Bear Case**: Risk identifier, deal killers, worst-case
- **Analyst**: Neutral, data-driven, probability-weighted

### Tier 3: Synthesis

- **Executive Synthesizer**: Final recommendation with confidence score

---

## 📊 Output Format

### shared_reasoning.md

Every council session produces a `shared_reasoning.md` file that captures:

1. **Specialist analyses** with data and findings
2. **Perspective positions** (Bull/Bear/Analyst)
3. **Debate round** between perspectives
4. **Executive synthesis** with final recommendation

This creates a complete **audit trail** for every decision.

### council_result.json

```json
{
  "council_id": "uuid",
  "platform": "biddeed",
  "subject": "123 Ocean Ave",
  "recommendation": "BID at $175,000",
  "confidence": 0.78,
  "action_items": [
    "Order title search",
    "Schedule property inspection"
  ],
  "execution_time_ms": 28500,
  "token_usage": {
    "total_input": 12500,
    "total_output": 8200
  }
}
```

---

## 💰 Cost Optimization

| Agent Type | Model | Cost Tier |
|------------|-------|-----------|
| Specialists | Gemini 2.5 Flash | FREE |
| Bull/Bear/Analyst | Gemini 2.5 Flash | FREE |
| Executive Synthesizer | Claude Sonnet 4.5 | PREMIUM |

**Estimated cost per council session: $0.05-0.15**

---

## 📈 Success Metrics

| Metric | Target |
|--------|--------|
| False positive rate (BID → loss) | <5% |
| False negative rate (SKIP → missed deal) | <10% |
| Council execution time | <30 seconds |
| Confidence calibration | Outcomes match predictions |

---

## 🔗 Integration

### With BidDeed.AI Pipeline

The council integrates at the decision stage of the 12-stage pipeline:

```
Discovery → Scraping → Title → Lien Priority → Tax Certs → 
Demographics → ML Score → **AI COUNCIL** → Decision Log → 
Report → Disposition → Archive
```

### With ZoneWise Chatbot

For complex queries (HBU analysis, multi-zoning), the chatbot invokes the council:

```python
if query.complexity > threshold:
    result = await run_council(platform="zonewise", ...)
    return synthesize_response(result)
```

---

## 📚 References

- [Mark Kashef's AI Council Video](https://www.youtube.com/watch?v=...)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [E2B Fragments](https://github.com/e2b-dev/fragments)

---

## 📄 License

MIT License - Shapira Ventures 2026

---

*AI Council Ecosystem v1.0*
*Built for ZoneWise, SPD, and BidDeed.AI*
