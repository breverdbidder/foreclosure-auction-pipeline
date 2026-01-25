"""
AI Council LangGraph Workflow
=============================
Multi-Agent Decision Intelligence Orchestration

Platforms: ZoneWise, SPD, BidDeed.AI
Version: 1.0
Date: January 24, 2026
"""

import asyncio
import json
import os
from datetime import datetime
from typing import TypedDict, List, Optional, Annotated, Literal
from dataclasses import dataclass
import operator

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# Import agent prompts
from council_prompts import (
    Platform, AgentRole, AgentPrompt,
    get_council_agents, create_shared_reasoning_file, update_shared_reasoning,
    BULL_CASE_PROMPT, BEAR_CASE_PROMPT, ANALYST_PROMPT, EXECUTIVE_SYNTHESIZER_PROMPT
)


# =============================================================================
# STATE DEFINITIONS
# =============================================================================

class CouncilState(TypedDict):
    """State object for the AI Council workflow."""
    
    # Input
    query: str
    context: dict
    platform: str  # 'zonewise' | 'spd' | 'biddeed'
    subject: str  # Property address or project name
    
    # Configuration
    council_id: str
    started_at: str
    output_dir: str
    
    # Specialist outputs (Tier 1)
    specialist_analyses: Annotated[dict, operator.or_]
    
    # Perspective outputs (Tier 2)
    bull_case_output: str
    bear_case_output: str
    analyst_output: str
    
    # Debate round
    debate_log: Annotated[List[dict], operator.add]
    
    # Executive synthesis (Tier 3)
    recommendation: str
    confidence: float
    action_items: List[str]
    
    # Audit trail
    shared_reasoning_path: str
    
    # Execution tracking
    execution_time_ms: int
    token_usage: dict
    errors: Annotated[List[str], operator.add]
    
    # Control flow
    iteration_count: int
    max_iterations: int


# =============================================================================
# LLM ROUTER
# =============================================================================

class SmartRouter:
    """Routes requests to optimal LLM based on task and cost."""
    
    def __init__(self):
        self.model_configs = {
            "gemini-2.5-flash": {
                "cost_tier": "FREE",
                "max_tokens": 8192,
                "api_key_env": "GEMINI_API_KEY"
            },
            "claude-sonnet-4.5": {
                "cost_tier": "PREMIUM",
                "max_tokens": 8192,
                "api_key_env": "ANTHROPIC_API_KEY"
            },
            "deepseek-v3.2": {
                "cost_tier": "ULTRA_CHEAP",
                "max_tokens": 4096,
                "api_key_env": "DEEPSEEK_API_KEY"
            }
        }
    
    async def call_llm(
        self,
        model: str,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.7
    ) -> tuple[str, dict]:
        """Call LLM and return (response, usage_stats)."""
        
        # In production, implement actual API calls
        # This is a placeholder for the routing logic
        
        if model.startswith("gemini"):
            return await self._call_gemini(system_prompt, user_message, temperature)
        elif model.startswith("claude"):
            return await self._call_claude(system_prompt, user_message, temperature)
        elif model.startswith("deepseek"):
            return await self._call_deepseek(system_prompt, user_message, temperature)
        else:
            raise ValueError(f"Unknown model: {model}")
    
    async def _call_gemini(self, system: str, user: str, temp: float) -> tuple[str, dict]:
        """Call Gemini 2.5 Flash API."""
        import httpx
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}",
                json={
                    "contents": [
                        {"role": "user", "parts": [{"text": f"{system}\n\n{user}"}]}
                    ],
                    "generationConfig": {
                        "temperature": temp,
                        "maxOutputTokens": 8192
                    }
                },
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()
            
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            usage = data.get("usageMetadata", {})
            
            return text, {
                "model": "gemini-2.5-flash",
                "input_tokens": usage.get("promptTokenCount", 0),
                "output_tokens": usage.get("candidatesTokenCount", 0),
                "cost_tier": "FREE"
            }
    
    async def _call_claude(self, system: str, user: str, temp: float) -> tuple[str, dict]:
        """Call Claude Sonnet 4.5 API."""
        import httpx
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-sonnet-4-5-20250929",
                    "max_tokens": 8192,
                    "temperature": temp,
                    "system": system,
                    "messages": [{"role": "user", "content": user}]
                },
                timeout=120.0
            )
            response.raise_for_status()
            data = response.json()
            
            text = data["content"][0]["text"]
            usage = data.get("usage", {})
            
            return text, {
                "model": "claude-sonnet-4.5",
                "input_tokens": usage.get("input_tokens", 0),
                "output_tokens": usage.get("output_tokens", 0),
                "cost_tier": "PREMIUM"
            }
    
    async def _call_deepseek(self, system: str, user: str, temp: float) -> tuple[str, dict]:
        """Call DeepSeek V3.2 API."""
        import httpx
        
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY not set")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.deepseek.com/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user}
                    ],
                    "temperature": temp,
                    "max_tokens": 4096
                },
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()
            
            text = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            
            return text, {
                "model": "deepseek-v3.2",
                "input_tokens": usage.get("prompt_tokens", 0),
                "output_tokens": usage.get("completion_tokens", 0),
                "cost_tier": "ULTRA_CHEAP"
            }


# Global router instance
router = SmartRouter()


# =============================================================================
# WORKFLOW NODES
# =============================================================================

async def run_specialist_agents(state: CouncilState) -> dict:
    """Run platform-specific specialist agents in parallel."""
    
    platform = Platform(state["platform"])
    agents = get_council_agents(platform)
    
    # Get specialist agents only
    specialists = {k: v for k, v in agents.items() if v.role == AgentRole.SPECIALIST}
    
    if not specialists:
        return {"specialist_analyses": {}}
    
    # Run specialists in parallel
    async def run_specialist(name: str, agent: AgentPrompt) -> tuple[str, str, dict]:
        user_message = f"""
Analyze the following:

Subject: {state['subject']}
Platform: {state['platform']}
Query: {state['query']}

Context:
{json.dumps(state['context'], indent=2)}

Provide your specialist analysis following your output format.
"""
        response, usage = await router.call_llm(
            model=agent.model_preference,
            system_prompt=agent.system_prompt,
            user_message=user_message,
            temperature=agent.temperature
        )
        return name, response, usage
    
    tasks = [run_specialist(name, agent) for name, agent in specialists.items()]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    specialist_outputs = {}
    errors = []
    token_usage = state.get("token_usage", {"total_input": 0, "total_output": 0, "calls": []})
    
    for result in results:
        if isinstance(result, Exception):
            errors.append(f"Specialist error: {str(result)}")
        else:
            name, response, usage = result
            specialist_outputs[name] = response
            token_usage["calls"].append(usage)
            token_usage["total_input"] += usage.get("input_tokens", 0)
            token_usage["total_output"] += usage.get("output_tokens", 0)
            
            # Update shared reasoning file
            update_shared_reasoning(
                state["shared_reasoning_path"],
                agents[name].name,
                response,
                section="Specialist Analyses"
            )
    
    return {
        "specialist_analyses": specialist_outputs,
        "token_usage": token_usage,
        "errors": errors
    }


async def run_bull_case_agent(state: CouncilState) -> dict:
    """Run the Bull Case (optimist) agent."""
    
    user_message = f"""
Analyze the following opportunity:

Subject: {state['subject']}
Platform: {state['platform']}
Query: {state['query']}

Context:
{json.dumps(state['context'], indent=2)}

Specialist Analyses:
{json.dumps(state['specialist_analyses'], indent=2)}

Provide your Bull Case analysis identifying opportunities and upside potential.
"""
    
    response, usage = await router.call_llm(
        model="gemini-2.5-flash",
        system_prompt=BULL_CASE_PROMPT,
        user_message=user_message,
        temperature=0.7
    )
    
    # Update shared reasoning
    update_shared_reasoning(
        state["shared_reasoning_path"],
        "Bull Case Agent",
        response
    )
    
    token_usage = state.get("token_usage", {"total_input": 0, "total_output": 0, "calls": []})
    token_usage["calls"].append(usage)
    token_usage["total_input"] += usage.get("input_tokens", 0)
    token_usage["total_output"] += usage.get("output_tokens", 0)
    
    return {
        "bull_case_output": response,
        "token_usage": token_usage
    }


async def run_bear_case_agent(state: CouncilState) -> dict:
    """Run the Bear Case (skeptic) agent."""
    
    user_message = f"""
Analyze the following for risks:

Subject: {state['subject']}
Platform: {state['platform']}
Query: {state['query']}

Context:
{json.dumps(state['context'], indent=2)}

Specialist Analyses:
{json.dumps(state['specialist_analyses'], indent=2)}

Provide your Bear Case analysis identifying risks, deal killers, and worst-case scenarios.
"""
    
    response, usage = await router.call_llm(
        model="gemini-2.5-flash",
        system_prompt=BEAR_CASE_PROMPT,
        user_message=user_message,
        temperature=0.7
    )
    
    # Update shared reasoning
    update_shared_reasoning(
        state["shared_reasoning_path"],
        "Bear Case Agent",
        response
    )
    
    token_usage = state.get("token_usage", {"total_input": 0, "total_output": 0, "calls": []})
    token_usage["calls"].append(usage)
    token_usage["total_input"] += usage.get("input_tokens", 0)
    token_usage["total_output"] += usage.get("output_tokens", 0)
    
    return {
        "bear_case_output": response,
        "token_usage": token_usage
    }


async def run_analyst_agent(state: CouncilState) -> dict:
    """Run the Analyst (neutral) agent."""
    
    user_message = f"""
Provide objective analysis:

Subject: {state['subject']}
Platform: {state['platform']}
Query: {state['query']}

Context:
{json.dumps(state['context'], indent=2)}

Specialist Analyses:
{json.dumps(state['specialist_analyses'], indent=2)}

Provide your neutral, data-driven analysis with probability assessments.
"""
    
    response, usage = await router.call_llm(
        model="gemini-2.5-flash",
        system_prompt=ANALYST_PROMPT,
        user_message=user_message,
        temperature=0.3
    )
    
    # Update shared reasoning
    update_shared_reasoning(
        state["shared_reasoning_path"],
        "Analyst Agent",
        response
    )
    
    token_usage = state.get("token_usage", {"total_input": 0, "total_output": 0, "calls": []})
    token_usage["calls"].append(usage)
    token_usage["total_input"] += usage.get("input_tokens", 0)
    token_usage["total_output"] += usage.get("output_tokens", 0)
    
    return {
        "analyst_output": response,
        "token_usage": token_usage
    }


async def conduct_debate_round(state: CouncilState) -> dict:
    """Facilitate a debate round between perspective agents."""
    
    debate_prompt = f"""
You are facilitating a debate between three perspectives on: {state['subject']}

Bull Case Position:
{state['bull_case_output']}

Bear Case Position:
{state['bear_case_output']}

Analyst Assessment:
{state['analyst_output']}

Generate a brief debate exchange where:
1. Bull responds to Bear's top concern
2. Bear challenges Bull's key assumption
3. Analyst provides data-driven mediation

Format as a dialogue with clear speaker labels.
"""
    
    response, usage = await router.call_llm(
        model="gemini-2.5-flash",
        system_prompt="You facilitate structured debates between analytical perspectives. Keep exchanges focused and productive.",
        user_message=debate_prompt,
        temperature=0.6
    )
    
    debate_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "content": response
    }
    
    # Update shared reasoning
    with open(state["shared_reasoning_path"], 'a') as f:
        f.write(f"\n## Debate Round\n\n{response}\n")
    
    token_usage = state.get("token_usage", {"total_input": 0, "total_output": 0, "calls": []})
    token_usage["calls"].append(usage)
    token_usage["total_input"] += usage.get("input_tokens", 0)
    token_usage["total_output"] += usage.get("output_tokens", 0)
    
    return {
        "debate_log": [debate_entry],
        "token_usage": token_usage
    }


async def executive_synthesis(state: CouncilState) -> dict:
    """Generate final executive recommendation."""
    
    # Read full shared reasoning file
    with open(state["shared_reasoning_path"], 'r') as f:
        full_reasoning = f.read()
    
    synthesis_prompt = f"""
You are the Executive Synthesizer. Read all analyses and produce a final recommendation.

Platform: {state['platform'].upper()}
Subject: {state['subject']}
Query: {state['query']}

=== FULL COUNCIL ANALYSIS ===
{full_reasoning}
=== END ANALYSIS ===

Produce your executive synthesis following the format for {state['platform'].upper()} platform.
Include:
1. Clear recommendation (BID/SKIP/REVIEW for BidDeed, GO/NO-GO for ZoneWise, APPROVE/REVISE/REJECT for SPD)
2. Confidence score (0.0-1.0)
3. Rationale synthesizing all perspectives
4. Specific action items
"""
    
    response, usage = await router.call_llm(
        model="claude-sonnet-4.5",  # Premium model for synthesis
        system_prompt=EXECUTIVE_SYNTHESIZER_PROMPT,
        user_message=synthesis_prompt,
        temperature=0.5
    )
    
    # Parse confidence from response (simple extraction)
    confidence = 0.7  # Default
    if "Confidence:" in response:
        try:
            conf_line = [l for l in response.split('\n') if "Confidence:" in l][0]
            conf_str = conf_line.split("Confidence:")[1].strip().split()[0]
            confidence = float(conf_str.replace('%', '').replace('**', ''))
            if confidence > 1:
                confidence = confidence / 100
        except:
            pass
    
    # Extract action items (simple extraction)
    action_items = []
    if "Action Items" in response:
        action_section = response.split("Action Items")[1].split("###")[0]
        for line in action_section.split('\n'):
            if line.strip().startswith('- [ ]') or line.strip().startswith('- [x]'):
                action_items.append(line.strip()[6:])
    
    # Update shared reasoning
    with open(state["shared_reasoning_path"], 'a') as f:
        f.write(f"\n## Executive Synthesis (Tier 3)\n\n{response}\n")
        f.write(f"\n---\n**Completed:** {datetime.utcnow().isoformat()}Z\n")
    
    token_usage = state.get("token_usage", {"total_input": 0, "total_output": 0, "calls": []})
    token_usage["calls"].append(usage)
    token_usage["total_input"] += usage.get("input_tokens", 0)
    token_usage["total_output"] += usage.get("output_tokens", 0)
    
    return {
        "recommendation": response,
        "confidence": confidence,
        "action_items": action_items,
        "token_usage": token_usage
    }


async def quality_check(state: CouncilState) -> dict:
    """Check quality and determine if regeneration needed."""
    
    iteration = state.get("iteration_count", 0) + 1
    max_iter = state.get("max_iterations", 2)
    
    return {
        "iteration_count": iteration
    }


def should_regenerate(state: CouncilState) -> Literal["regenerate", "complete"]:
    """Determine if we should regenerate or complete."""
    
    confidence = state.get("confidence", 0.7)
    iteration = state.get("iteration_count", 1)
    max_iter = state.get("max_iterations", 2)
    
    if confidence < 0.5 and iteration < max_iter:
        return "regenerate"
    return "complete"


# =============================================================================
# WORKFLOW BUILDER
# =============================================================================

def build_council_workflow() -> StateGraph:
    """Build the AI Council LangGraph workflow."""
    
    workflow = StateGraph(CouncilState)
    
    # Add nodes
    workflow.add_node("run_specialists", run_specialist_agents)
    workflow.add_node("run_bull_case", run_bull_case_agent)
    workflow.add_node("run_bear_case", run_bear_case_agent)
    workflow.add_node("run_analyst", run_analyst_agent)
    workflow.add_node("conduct_debate", conduct_debate_round)
    workflow.add_node("synthesize", executive_synthesis)
    workflow.add_node("quality_check", quality_check)
    
    # Set entry point
    workflow.set_entry_point("run_specialists")
    
    # Parallel perspective agents after specialists
    workflow.add_edge("run_specialists", "run_bull_case")
    workflow.add_edge("run_specialists", "run_bear_case")
    workflow.add_edge("run_specialists", "run_analyst")
    
    # Converge for debate (need all three)
    # Note: In production, use a barrier node pattern
    workflow.add_edge("run_bull_case", "conduct_debate")
    workflow.add_edge("run_bear_case", "conduct_debate")
    workflow.add_edge("run_analyst", "conduct_debate")
    
    # Synthesis after debate
    workflow.add_edge("conduct_debate", "synthesize")
    workflow.add_edge("synthesize", "quality_check")
    
    # Quality gate with conditional routing
    workflow.add_conditional_edges(
        "quality_check",
        should_regenerate,
        {
            "regenerate": "conduct_debate",
            "complete": END
        }
    )
    
    return workflow


# =============================================================================
# MAIN EXECUTION
# =============================================================================

async def run_council(
    platform: str,
    subject: str,
    query: str,
    context: dict,
    output_dir: str = "/tmp/council"
) -> dict:
    """Execute a full AI Council session."""
    
    import uuid
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize shared reasoning file
    shared_reasoning_path = create_shared_reasoning_file(
        subject=subject,
        platform=Platform(platform),
        query=query,
        output_dir=output_dir
    )
    
    # Build workflow
    workflow = build_council_workflow()
    app = workflow.compile(checkpointer=MemorySaver())
    
    # Initial state
    initial_state: CouncilState = {
        "query": query,
        "context": context,
        "platform": platform,
        "subject": subject,
        "council_id": str(uuid.uuid4()),
        "started_at": datetime.utcnow().isoformat(),
        "output_dir": output_dir,
        "specialist_analyses": {},
        "bull_case_output": "",
        "bear_case_output": "",
        "analyst_output": "",
        "debate_log": [],
        "recommendation": "",
        "confidence": 0.0,
        "action_items": [],
        "shared_reasoning_path": shared_reasoning_path,
        "execution_time_ms": 0,
        "token_usage": {"total_input": 0, "total_output": 0, "calls": []},
        "errors": [],
        "iteration_count": 0,
        "max_iterations": 2
    }
    
    # Execute workflow
    start_time = datetime.utcnow()
    
    config = {"configurable": {"thread_id": initial_state["council_id"]}}
    final_state = await app.ainvoke(initial_state, config)
    
    end_time = datetime.utcnow()
    execution_time = int((end_time - start_time).total_seconds() * 1000)
    
    # Update final execution time
    final_state["execution_time_ms"] = execution_time
    
    # Save final state
    with open(f"{output_dir}/council_result.json", 'w') as f:
        # Convert to JSON-serializable
        result = {
            "council_id": final_state["council_id"],
            "platform": final_state["platform"],
            "subject": final_state["subject"],
            "query": final_state["query"],
            "recommendation": final_state["recommendation"],
            "confidence": final_state["confidence"],
            "action_items": final_state["action_items"],
            "execution_time_ms": execution_time,
            "token_usage": final_state["token_usage"],
            "shared_reasoning_path": shared_reasoning_path,
            "errors": final_state["errors"]
        }
        json.dump(result, f, indent=2)
    
    return final_state


# =============================================================================
# CLI INTERFACE
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run AI Council analysis")
    parser.add_argument("--platform", choices=["zonewise", "spd", "biddeed"], required=True)
    parser.add_argument("--subject", required=True, help="Property address or project name")
    parser.add_argument("--query", required=True, help="Analysis question")
    parser.add_argument("--context", type=str, default="{}", help="JSON context data")
    parser.add_argument("--output", default="/tmp/council", help="Output directory")
    
    args = parser.parse_args()
    
    context = json.loads(args.context)
    
    result = asyncio.run(run_council(
        platform=args.platform,
        subject=args.subject,
        query=args.query,
        context=context,
        output_dir=args.output
    ))
    
    print(f"\n{'='*60}")
    print(f"COUNCIL COMPLETE: {result['subject']}")
    print(f"{'='*60}")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"Execution Time: {result['execution_time_ms']}ms")
    print(f"Token Usage: {result['token_usage']['total_input']} in / {result['token_usage']['total_output']} out")
    print(f"\nFull reasoning: {result['shared_reasoning_path']}")
    print(f"Results JSON: {args.output}/council_result.json")
