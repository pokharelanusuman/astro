import os
from crewai import Agent, Task, Crew, Process
from db import fetch_house_tree

def run_astrology_crew_analysis(snapshot_id: int, house_num: int) -> str:
    """Extracts raw database data graphs and streams them through a local CrewAI pipeline."""
    
    # 1. Pull down our database tree layout to pass to the agents
    raw_data_tree = fetch_house_tree(snapshot_id, house_num)
    
    # 2. Define the local model string format CrewAI expects for Ollama
    local_llm_string = "ollama/mistral"

    # 3. Define Agent 1: The Astronomical Data Auditor
    auditor_agent = Agent(
        role="Senior Astronomical Data Auditor",
        goal="Deconstruct the raw planet-to-house relational database trees into mathematical and positional realities.",
        backstory=(
            "You are a meticulous structural data analyst. You look at raw database branches, "
            "verify exact alignments, confirm line placements, and filter out noise. "
            "You focus purely on objective data and physical presence."
        ),
        verbose=False,            # CHANGED: Lower console IO overhead
        llm=local_llm_string,
        allow_delegation=False,
        memory=False              # FIXED: Disables memory allocation for this agent
    )

    # 4. Define Agent 2: The Classical Text Scholar
    scholar_agent = Agent(
        role="Classical Jyotish Text Scholar",
        goal="Correlate verified planetary nodes against classical Vedic guidelines and historical source rules.",
        backstory=(
            "You are an academic historian specialized in classical calculations. You map audited "
            "planetary positions to structural principles, analyzing how specific configurations "
            "traditionally function within a given house."
        ),
        verbose=False,            # CHANGED: Lower console IO overhead
        llm=local_llm_string,
        allow_delegation=False,
        memory=False              # FIXED: Disables memory allocation for this agent
    )

    # 5. Define Agent 3: The Synthesis Master
    synthesizer_agent = Agent(
        role="Vedic Astrological Lead Synthesizer",
        goal="Compile analytical technical notes into a clear, cohesive final summary.",
        backstory=(
            "You convert dense, technical data and classical rules into clear, actionable advice. "
            "You organize reports logically using markdown headers and clean bullet points, ensuring "
            "complex insights are easy to read and understand."
        ),
        verbose=False,            # CHANGED: Lower console IO overhead
        llm=local_llm_string,
        allow_delegation=False,
        memory=False              # FIXED: Disables memory allocation for this agent
    )

    # 6. Establish Task 1: Audit Data Vectors
    task_audit = Task(
        description=(
            f"Analyze this raw database tree text for House {house_num}:\n\n{raw_data_tree}\n\n"
            "Identify every active planetary node. Extract their exact functional type (Occupant or Aspect) "
            "and list the stated rationales clearly. Do not assume or add details not in the text."
        ),
        expected_output="A structured markdown summary listing verified active planetary nodes, types, and database rationales.",
        agent=auditor_agent
    )

    # 7. Establish Task 2: Cross-Reference Classical Principles
    task_scholarship = Task(
        description=(
            "Review the audited data vectors from the previous step. Apply classical principles to analyze "
            f"how these combined planetary nodes interact within House {house_num}, considering its core significance."
        ),
        expected_output="An analysis evaluating the structural harmony, potential challenges, and dynamics of the verified nodes.",
        agent=scholar_agent
    )

    # 8. Establish Task 3: Final Synthesis Generation
    task_synthesis = Task(
        description=(
            "Combine the audited metrics and scholarly notes into a comprehensive, polished summary. "
            "Structure your response with clear headers: "
            "'1. Core Significances Affected', '2. Dynamic Influence Paths', and '3. Strategic Summary'. "
            "Ensure the final text is clean, structured, and easy to read."
        ),
        expected_output="A well-structured, comprehensive report formatted using clean markdown headers and bullet points.",
        agent=synthesizer_agent
    )

    # 9. Assemble the Crew and run it sequentially with optimized telemetry
    astro_squad = Crew(
        agents=[auditor_agent, scholar_agent, synthesizer_agent],
        tasks=[task_audit, task_scholarship, task_synthesis],
        process=Process.sequential,
        verbose=True,
        memory=False,             # FIXED: Stops global vector DB instantiation
        cache=True                # FIXED: Enables internal embedding reuse to minimize CPU thrashes
    )

    print(f"\n[CrewAI Orchestration]: Launching local agent pipeline for House {house_num}...")
    result = astro_squad.kickoff()
    
    return str(result)