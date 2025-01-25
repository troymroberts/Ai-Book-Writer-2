import os
import shutil
import importlib
import re
from crewai import Task, Crew, Process
from dotenv import load_dotenv
from agents import create_agents

# Load environment variables
load_dotenv()

# Validate Ollama configuration
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL')
if not OLLAMA_MODEL:
    raise ValueError("Missing OLLAMA_MODEL in .env file")

# Configure manager LLM for hierarchical processes
MANAGER_LLM_CONFIG = {
    "provider": "ollama",
    "config": {
        "model": OLLAMA_MODEL,
        "base_url": "http://localhost:11434",
        "temperature": 0.3
    }
}

# Genre configuration
GENRE = os.getenv('GENRE', 'literary_fiction')

def load_genre_config(genre):
    try:
        genre_module = importlib.import_module(f"genres.{genre}")
        return {
            k: v for k, v in genre_module.__dict__.items() 
            if not k.startswith("_") and k.isupper()
        }
    except ModuleNotFoundError:
        print(f"Genre configuration for '{genre}' not found. Using defaults.")
        return {}

# Load genre configuration
genre_config = load_genre_config(GENRE)
num_chapters = genre_config.get('NUM_CHAPTERS', 3)

# Create agents
model_to_use = f"ollama/{OLLAMA_MODEL}"
agents = create_agents(model_to_use, num_chapters, "", genre_config)
(
    story_planner, outline_creator, setting_builder, character_agent,
    relationship_architect, plot_agent, writer, editor, memory_keeper,
    researcher, critic, reviser, outline_compiler
) = agents

# Initial prompt
initial_prompt = os.getenv('INITIAL_PROMPT', 
    "A group of friends decides to spend a memorable day at the beach...")

# Outline generation tasks (keep original task definitions)
# ... [keep all original task definitions unchanged] ...

# Create and run outline crew
outline_crew = Crew(
    agents=[story_planner, setting_builder, character_agent,
            relationship_architect, outline_creator, outline_compiler],
    tasks=[
        story_planning_task,
        setting_building_task,
        character_development_task,
        relationship_architecture_task,
        outline_creator_task,
        outline_compiler_task
    ],
    verbose=True,
    process=Process.sequential
)

# Generate outline
outline_result = outline_crew.kickoff()

# Save outline
output_folder = "book-output"
os.makedirs(output_folder, exist_ok=True)
outline_file_path = os.path.join(output_folder, "outline.txt")
with open(outline_file_path, "w") as f:
    f.write(str(outline_result))

print(f"Outline written to {outline_file_path}")

# Update agent context
outline_context = str(outline_result)
for agent in agents:
    agent.goal = agent.goal.replace("{outline_context}", outline_context)
    agent.backstory = agent.backstory.replace("{outline_context}", outline_context)

# Chapter generation functions
def create_chapter_tasks(chapter_number, outline_context, genre_config):
    min_words = genre_config.get('MIN_WORDS_PER_CHAPTER', 1600)
    max_words = genre_config.get('MAX_WORDS_PER_CHAPTER', 3000)
    
    research_task = Task(
        description=f"""Research details for Chapter {chapter_number}. Context: {outline_context}""",
        expected_output="Relevant research data with citations",
        agent=researcher
    )

    write_task = Task(
        description=f"""Write Chapter {chapter_number} ({min_words}-{max_words} words). MUST INCLUDE:
        - Detailed character interactions
        - Vivid setting descriptions
        - Multi-paragraph dialogue sequences
        - Sensory details (smells, sounds, textures)
        - Internal character monologues
        If below {min_words} words, ADD:
        - Extended scene descriptions
        - Additional character backstory elements
        - Environmental observations""",
        expected_output="Full chapter text meeting word count requirements",
        agent=writer,
        context=[research_task, outline_creator_task]
    )

    critic_task = Task(
        description=f"Provide detailed critique of Chapter {chapter_number}",
        expected_output="List of improvements needed with specific examples",
        agent=critic,
        context=[write_task]
    )

    revise_task = Task(
        description=f"""Revise Chapter {chapter_number} incorporating:
        - Critic feedback
        - Improved continuity
        - Enhanced character development""",
        expected_output="Polished chapter draft",
        agent=reviser,
        context=[write_task, critic_task]
    )

    edit_task = Task(
        description=f"""Final edit of Chapter {chapter_number}. ENSURE:
        - Word count: {min_words}-{max_words}
        - Grammar/style consistency
        - Adherence to outline
        - Proper paragraph structure""",
        expected_output="Publication-ready chapter",
        agent=editor,
        context=[revise_task]
    )

    return [research_task, write_task, critic_task, revise_task, edit_task]

# Chapter generation loop
for chapter_number in range(1, num_chapters + 1):
    chapter_tasks = create_chapter_tasks(chapter_number, outline_context, genre_config)
    
    # Configure hierarchical crew with proper manager
    chapter_crew = Crew(
        agents=[writer, researcher, critic, reviser, editor],
        tasks=chapter_tasks,
        verbose=True,
        process=Process.hierarchical,
        manager_llm=MANAGER_LLM_CONFIG,
        memory=True
    )

    # Generation with validation
    valid = False
    attempts = 0
    while not valid and attempts < 3:
        try:
            result = chapter_crew.kickoff()
            
            # Extract writer's output
            chapter_content = ""
            for task in chapter_tasks:
                if task.agent.role == 'Writer':
                    chapter_content = str(task.output)
                    break
                    
            # Validate word count
            word_count = len(re.findall(r'\w+', chapter_content))
            if word_count >= genre_config['MIN_WORDS_PER_CHAPTER']:
                valid = True
            else:
                print(f"Regenerating Chapter {chapter_number} (attempt {attempts+1})")
                attempts += 1
                
        except Exception as e:
            print(f"Error generating chapter {chapter_number}: {str(e)}")
            attempts += 1

    # Format and save chapter
    paragraphs = chapter_content.split("\n\n")
    formatted_paragraphs = [f"<p>{p.strip()}</p>" for p in paragraphs if p.strip()]
    formatted_text = "\n".join(formatted_paragraphs)

    html_content = f"""<!DOCTYPE html>
    <html>
    <head>
        <title>A Day at the Beach - Chapter {chapter_number}</title>
    </head>
    <body>
        <h1>Chapter {chapter_number}</h1>
        {formatted_text}
        <p>Word Count: {word_count}</p>
    </body>
    </html>"""

    output_file = os.path.join(output_folder, f"beach_story_chapter_{chapter_number}.html")
    with open(output_file, "w") as f:
        f.write(html_content)

    print(f"Chapter {chapter_number} written to {output_file}")

print("######################")
print("Story generation complete.")
