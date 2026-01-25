# AI Council Ecosystem Architecture
## Multi-Agent Decision Intelligence for Shapira Ventures

**Version:** 1.0  
**Date:** January 24, 2026  
**Author:** Claude AI Architect  
**Scope:** ZoneWise, SPD, BidDeed.AI

---

## Executive Summary

This document defines the AI Council architecture that unifies decision-making across all Shapira venture platforms. Based on Mark Kashef's methodology, we implement **distributed cognition** through specialized agents that analyze, debate, and synthesize recommendations.

### Core Principle

```
Single AI Response → AI Council Synthesis
     ↓                      ↓
  One perspective    Multiple perspectives
  Hidden reasoning   Transparent audit trail
  Fast but shallow   Thorough and defensible
```

---

## 1. UNIFIED COUNCIL ARCHITECTURE

### 1.1 Three-Tier Agent Structure

```
┌─────────────────────────────────────────────────────────────┐
│           TIER 3: EXECUTIVE SYNTHESIS LAYER                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Executive Synthesizer Agent                         │   │
│  │  - Reads all shared_reasoning.md entries            │   │
│  │  - Identifies consensus and conflicts               │   │
│  │  - Produces final recommendation with confidence    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↑
┌─────────────────────────────────────────────────────────────┐
│           TIER 2: PERSPECTIVE AGENTS (CROSS-DOMAIN)          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   BULL CASE  │  │   BEAR CASE  │  │   ANALYST    │      │
│  │   (Optimist) │  │   (Skeptic)  │  │   (Neutral)  │      │
│  │              │  │              │  │              │      │
│  │ Opportunities│  │ Risks/Flaws  │  │ Pure Numbers │      │
│  │ Upside       │  │ Deal Killers │  │ Probabilities│      │
│  │ Scenarios    │  │ Worst Case   │  │ Comparables  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↑
┌─────────────────────────────────────────────────────────────┐
│           TIER 1: SPECIALIST AGENTS (DOMAIN-SPECIFIC)        │
│                                                              │
│  ZONEWISE          SPD               BIDDEED.AI             │
│  ┌────────────┐   ┌────────────┐   ┌────────────┐          │
│  │Zoning Agent│   │Approval    │   │Title Agent │          │
│  │CMA Agent   │   │Agent       │   │Lien Agent  │          │
│  │HBU Agent   │   │Engineering │   │Repair Agent│          │
│  │Reporter    │   │Agent       │   │Exit Agent  │          │
│  └────────────┘   └────────────┘   └────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Communication Protocol

All agents communicate through **shared_reasoning.md** files:

```
project_analysis/
├── shared_reasoning.md      ← Central audit trail
├── agent_outputs/
│   ├── bull_case.md        ← Individual analyses
│   ├── bear_case.md
│   ├── analyst.md
│   └── specialists/
│       ├── zoning.md
│       ├── title.md
│       └── ...
└── final_synthesis.md       ← Executive output
```

---

## 2. PLATFORM-SPECIFIC COUNCILS

### 2.1 ZoneWise Council

**Purpose:** Evaluate zoning feasibility, highest-and-best-use, development potential

| Agent | Role | Key Questions |
|-------|------|---------------|
| **Zoning Specialist** | Ordinance expert | What's allowed by-right? Conditional uses? |
| **CMA Analyst** | Market valuation | What are comparable developments worth? |
| **HBU Strategist** | Highest-best-use | What's the optimal development scenario? |
| **Regulatory Navigator** | Process expert | What approvals needed? Timeline? |
| **Bull Case** | Opportunity finder | Best case development scenario |
| **Bear Case** | Risk identifier | Zoning denials, market risks, delays |
| **Executive Synthesizer** | Final recommendation | GO/NO-GO with confidence score |

**Trigger Conditions:**
- Complex zoning questions (multiple zones, conditional uses)
- HBU analysis requests
- Development feasibility studies
- Queries with >$500K potential impact

### 2.2 SPD Council (Site Plan Development)

**Purpose:** Evaluate site plan approval probability and optimize submissions

| Agent | Role | Key Questions |
|-------|------|---------------|
| **Planning Agent** | Zoning compliance | Does design meet setbacks, FAR, parking? |
| **Engineering Agent** | Technical review | Drainage, utilities, traffic impact? |
| **Environmental Agent** | Eco compliance | Wetlands, trees, stormwater? |
| **Approval Strategist** | Process optimizer | Which variances needed? Success probability? |
| **Bull Case** | Approval advocate | Path to approval, precedents |
| **Bear Case** | Denial predictor | Likely objections, design flaws |
| **Executive Synthesizer** | APPROVE/REVISE/REJECT | With specific action items |

**Trigger Conditions:**
- New site plan submissions
- Variance requests
- Pre-application consultations
- Multi-phase developments

### 2.3 BidDeed.AI Council

**Purpose:** Evaluate foreclosure auction properties for bid decisions

| Agent | Role | Key Questions |
|-------|------|---------------|
| **Title Agent** | Lien priority | Who survives foreclosure? Hidden liens? |
| **Repair Agent** | Cost estimator | Condition assessment, rehab costs? |
| **Market Agent** | ARV calculator | After-repair value, days-on-market? |
| **Exit Agent** | Strategy optimizer | Flip vs. Third Sword vs. wholesale? |
| **Bull Case** | Upside finder | Best case profit scenario |
| **Bear Case** | Deal killer | Title defects, cost overruns, market risk |
| **Executive Synthesizer** | BID/REVIEW/SKIP | Max bid with confidence |

**Trigger Conditions:**
- All properties with judgment >$100K
- BECA-verified cases
- Complex lien structures (HOA foreclosures, tax certificates)
- Properties flagged by ML as edge cases (40-60% confidence)

---

## 3. LANGGRAPH ORCHESTRATION

### 3.1 Council Workflow State

```python
from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END

class CouncilState(TypedDict):
    # Input
    query: str
    context: dict
    platform: str  # 'zonewise' | 'spd' | 'biddeed'
    
    # Specialist outputs
    specialist_analyses: dict[str, str]
    
    # Perspective outputs
    bull_case: str
    bear_case: str
    analyst_case: str
    
    # Debate round
    debate_log: List[dict]
    
    # Final synthesis
    recommendation: str
    confidence: float
    action_items: List[str]
    
    # Audit trail
    shared_reasoning_path: str
    execution_time_ms: int
```

### 3.2 Council Workflow Graph

```python
def create_council_workflow(platform: str) -> StateGraph:
    workflow = StateGraph(CouncilState)
    
    # Tier 1: Specialist agents (parallel)
    workflow.add_node("run_specialists", run_specialist_agents)
    
    # Tier 2: Perspective agents (parallel)
    workflow.add_node("run_bull_case", run_bull_case_agent)
    workflow.add_node("run_bear_case", run_bear_case_agent)
    workflow.add_node("run_analyst", run_analyst_agent)
    
    # Debate round (sequential)
    workflow.add_node("conduct_debate", conduct_debate_round)
    
    # Tier 3: Executive synthesis
    workflow.add_node("synthesize", executive_synthesis)
    
    # Quality check
    workflow.add_node("quality_check", quality_check_agent)
    
    # Define flow
    workflow.set_entry_point("run_specialists")
    
    # Parallel perspective agents after specialists
    workflow.add_edge("run_specialists", "run_bull_case")
    workflow.add_edge("run_specialists", "run_bear_case")
    workflow.add_edge("run_specialists", "run_analyst")
    
    # Converge for debate
    workflow.add_edge("run_bull_case", "conduct_debate")
    workflow.add_edge("run_bear_case", "conduct_debate")
    workflow.add_edge("run_analyst", "conduct_debate")
    
    # Synthesis after debate
    workflow.add_edge("conduct_debate", "synthesize")
    workflow.add_edge("synthesize", "quality_check")
    
    # Quality gate
    workflow.add_conditional_edges(
        "quality_check",
        lambda s: "regenerate" if s["confidence"] < 0.6 else "complete",
        {"regenerate": "conduct_debate", "complete": END}
    )
    
    return workflow.compile()
```

---

## 4. SHARED REASONING FILE FORMAT

### 4.1 Template Structure

```markdown
# AI Council Analysis: [Subject]

**Platform:** [ZoneWise | SPD | BidDeed.AI]
**Analysis ID:** [UUID]
**Started:** [ISO 8601 timestamp]
**Query:** [Original user question or trigger]

---

## Specialist Analyses (Tier 1)

### [Specialist Name] Agent
**Completed:** [timestamp]
**Data Sources:** [list]

#### Findings
- [Finding 1]
- [Finding 2]

#### Confidence
[High/Medium/Low] - [Explanation]

---

## Perspective Analyses (Tier 2)

### Bull Case Agent
**Perspective:** Opportunity-focused, best-case scenario

#### Key Arguments
1. [Argument 1]
2. [Argument 2]

#### Upside Potential
[Description]

#### Assumptions
- [Assumption 1]
- [Assumption 2]

---

### Bear Case Agent
**Perspective:** Risk-focused, worst-case scenario

#### Deal Killers Identified
1. [Risk 1] - Severity: [High/Medium/Low]
2. [Risk 2] - Severity: [High/Medium/Low]

#### Mitigation Options
- [Mitigation 1]
- [Mitigation 2]

#### Assumptions
- [Assumption 1]

---

### Analyst Agent
**Perspective:** Data-driven, probability-weighted

#### Quantitative Analysis
| Metric | Value | Source |
|--------|-------|--------|
| [Metric 1] | [Value] | [Source] |

#### Probability Assessment
- Best case: [%] probability
- Base case: [%] probability
- Worst case: [%] probability

---

## Debate Round

### Bull responds to Bear:
[Response addressing risk concerns]

### Bear responds to Bull:
[Response challenging optimistic assumptions]

### Analyst mediates:
[Data-driven reconciliation]

---

## Executive Synthesis (Tier 3)

**Recommendation:** [BID/REVIEW/SKIP | GO/NO-GO | APPROVE/REVISE]
**Confidence:** [0.0-1.0]

### Rationale
[Synthesis of all perspectives into coherent recommendation]

### Key Factors
1. [Factor 1] - Weight: [High/Medium/Low]
2. [Factor 2] - Weight: [High/Medium/Low]

### Action Items
- [ ] [Action 1]
- [ ] [Action 2]

### Dissenting Views
[Any unresolved disagreements]

---

**Completed:** [timestamp]
**Execution Time:** [ms]
**Token Usage:** [count]
```

---

## 5. IMPLEMENTATION PRIORITIES

### Phase 1: BidDeed.AI (Week 1-2)
- Highest immediate value (auction decisions)
- Existing ML pipeline provides specialist data
- Clear BID/REVIEW/SKIP output format

### Phase 2: ZoneWise (Week 3-4)
- Aligns with Q1 2026 launch
- Council enhances chatbot responses for complex queries
- Differentiator vs. Gridics

### Phase 3: SPD (Week 5-6)
- Longest approval cycles benefit most from thorough analysis
- Integration with 12-stage pipeline

---

## 6. COST OPTIMIZATION

### Model Routing by Agent Type

| Agent Type | Model | Cost Tier | Rationale |
|------------|-------|-----------|-----------|
| Specialists | Gemini 2.5 Flash | FREE | Data extraction, structured output |
| Bull/Bear/Analyst | Gemini 2.5 Flash | FREE | Perspective generation |
| Executive Synthesizer | Claude Sonnet 4.5 | PREMIUM | Complex reasoning, synthesis |
| Quality Check | Gemini 2.5 Flash | FREE | Confidence scoring |

**Estimated Cost per Council Session:**
- 7 agents × ~2K tokens each = 14K tokens
- 90% FREE tier = $0.05-0.10 per session
- Target: <$0.15 per property analysis

---

## 7. SUCCESS METRICS

### Decision Quality
- False positive rate (BID → loss): <5%
- False negative rate (SKIP → missed deal): <10%
- Confidence calibration: Actual outcomes match predicted confidence

### Process Efficiency
- Council execution time: <30 seconds
- Audit trail completeness: 100%
- Agent agreement rate: Track consensus vs. debate frequency

### User Value
- Time saved per decision: 2-3 hours
- Decision confidence increase: 40%+
- Regret rate reduction: 50%+

---

## 8. OPEN SOURCE INTEGRATIONS

### 4 Key Open Source Projects

1. **LangGraph** (MIT License)
   - Orchestration engine
   - State management
   - Conditional routing

2. **E2B Fragments** (Apache-2.0)
   - Split-screen UI
   - Multi-LLM chat
   - Streaming responses

3. **OpenManus** (fork available)
   - Agent framework patterns
   - Tool integration
   - Memory systems

4. **MunicipalMCP** (MIT License)
   - Municode API access
   - Ordinance data extraction
   - ZoneWise data layer

---

## Next Steps

1. **Immediate:** Deploy council_prompts.py to all repos
2. **Week 1:** Implement BidDeed.AI council in foreclosure-auction-pipeline
3. **Week 2:** Add council to ZoneWise chatbot flow
4. **Week 3:** Create shared_reasoning viewer in dashboards

---

*AI Council Ecosystem Architecture*
*Claude AI Architect | January 24, 2026*
