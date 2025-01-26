import os
import shutil
import importlib
import re
from crewai import Task, Crew, Process, Agent
from dotenv import load_dotenv
from agents import create_agents
import time
from litellm import Timeout, completion
import logging

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

# Validate Ollama configuration
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL')
if not OLLAMA_MODEL:
    raise ValueError("Missing OLLAMA_MODEL in .env file")

# Configure manager LLM for hierarchical processes
# Use a dictionary to hold the configuration
MANAGER_LLM_CONFIG = {
    "model": OLLAMA_MODEL,
    "api_base": "http://localhost:11434",
    "temperature": 0.3,
    "stream": False  # Remove streaming for now, focus on core issue
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

# Wrapper class for LiteLLM
class LiteLLMCompletionWrapper:
    def __init__(self, model, api_base, temperature=0.3, stream=False):
        self.model = model
        self.api_base = api_base
        self.temperature = temperature
        self.stream = stream
        self.stop = None  # Add the 'stop' attribute

    def __call__(self, *args, **kwargs):
        messages = kwargs.get('messages', [])
        response = completion(
            model=self.model,
            messages=messages,
            api_base=self.api_base,
            temperature=self.temperature
        )
        return response.choices[0].message.content

    def supports_stop_words(self):
        return False  # Ollama doesn't seem to support stop words

# Create agents using the create_agents function
agents = create_agents(None, num_chapters, "", genre_config)
(
    story_planner, outline_creator, setting_builder, character_agent,
    relationship_architect, plot_agent, writer, editor, memory_keeper,
    researcher, critic, reviser, outline_compiler, feedback_reviewer,
    dialogue_specialist, setting_description_agent
) = agents

# Set the LLM for each agent using the wrapper class
for agent in agents:
    agent.llm = LiteLLMCompletionWrapper(
        model=MANAGER_LLM_CONFIG["model"],
        api_base=MANAGER_LLM_CONFIG["api_base"],
        temperature=MANAGER_LLM_CONFIG["temperature"],
        stream=MANAGER_LLM_CONFIG["stream"]
    )
# Initial prompt
initial_prompt = os.getenv('INITIAL_PROMPT',
    "A group of friends decides to spend a memorable day at the beach...")

# Outline generation tasks
story_planning_task = Task(
    description=f"""Develop a high-level story arc for a {num_chapters}-chapter story based on the initial prompt: "{initial_prompt}".
    Consider the genre-specific pacing: {genre_config.get('PACING_SPEED_CHAPTER_START')}, {genre_config.get('PACING_SPEED_CHAPTER_MID')}, {genre_config.get('PACING_SPEED_CHAPTER_END')}.
    Identify major plot points, character arcs, and turning points across the entire narrative.""",
    expected_output="A comprehensive story arc plan with major plot points and character arcs.",
    agent=story_planner
)

setting_building_task = Task(
    description=f"""Establish all settings and world elements needed for the {num_chapters}-chapter story, ensuring they are rich, consistent, and dynamically integrated as the story progresses.
    Consider the genre-specific setting integration: {genre_config.get('SETTING_INTEGRATION')}.
    """,
    expected_output="Detailed descriptions of settings and world elements.",
    agent=setting_builder
)

character_development_task = Task(
    description=f"""Develop and maintain consistent, engaging, and evolving characters throughout the {num_chapters}-chapter book.
    Provide full names (first and last), ages, detailed backstories, motivations, personalities, strengths, weaknesses, and relationships for each character.
    Assign character stats (e.g., Intelligence, Charisma, etc.) on a scale of 1-10 and define their speech patterns (e.g., accent, tone, verbosity).
    Ensure characters are diverse and well-rounded.
    Consider the genre-specific character depth: {genre_config.get('CHARACTER_DEPTH')}.
    """,
    expected_output="Detailed character profiles for all main characters.",
    agent=character_agent
)

relationship_architecture_task = Task(
    description=f"""Develop and manage the relationships between characters, including family structures, friendships, rivalries, and romantic relationships.
    Ensure relationship dynamics are realistic, engaging, and contribute to the overall narrative.
    Provide detailed relationship backstories and evolution throughout the {num_chapters}-chapter story.
    Consider the genre-specific relationship depth: {genre_config.get('CHARACTER_RELATIONSHIP_DEPTH')}.
    """,
    expected_output="A detailed map of character relationships and their evolution.",
    agent=relationship_architect
)

outline_creator_task = Task(
    description=f"""Generate detailed chapter outlines based on the story arc plan for a {num_chapters}-chapter story.
    Include specific chapter titles, key events, character developments, setting, and tone for each chapter.
    Consider the genre-specific narrative style: {genre_config.get('NARRATIVE_STYLE')}.
    Create outlines for all {num_chapters} chapters
    """,
    expected_output="Detailed chapter outlines for the entire book.",
    agent=outline_creator
)

outline_compiler_task = Task(
    description=f"""Compile the complete book outline for a {num_chapters}-chapter story, integrating the overall story arc plan, setting details, character profiles, relationship dynamics, and individual chapter outlines into a single, cohesive document.
    Ensure the outline is well-structured, detailed, and follows the specified format.
    Output the ENTIRE outline, including all sections and all {num_chapters} chapters.""",
    expected_output="A complete and detailed book outline.",
    agent=outline_compiler
)

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
def create_chapter_tasks(chapter_number, outline_context, genre_config, agents, manager_llm_config):
    min_words = genre_config.get('MIN_WORDS_PER_CHAPTER', 1600)
    max_words = genre_config.get('MAX_WORDS_PER_CHAPTER', 3000)

    # Find the agents by their role
    researcher = next((agent for agent in agents if agent.role == 'Researcher'), None)
    setting_description_agent = next((agent for agent in agents if agent.role == 'Setting Description Agent'), None)
    dialogue_specialist = next((agent for agent in agents if agent.role == 'Dialogue Specialist'), None)
    writer = next((agent for agent in agents if agent.role == 'Writer'), None)
    critic = next((agent for agent in agents if agent.role == 'Critic'), None)
    reviser = next((agent for agent in agents if agent.role == 'Reviser'), None)
    editor = next((agent for agent in agents if agent.role == 'Editor'), None)
    feedback_reviewer = next((agent for agent in agents if agent.role == 'Feedback Reviewer'), None)

    # Create tasks with the LLM configuration directly in the task
    research_task = Task(
        description=f"""Research details for Chapter {chapter_number}. Context: {outline_context}""",
        expected_output="Relevant research data with citations",
        agent=researcher,
        llm=manager_llm_config
    )

    setting_description_task = Task(
        description=f"""Create a detailed setting description for Chapter {chapter_number} based on the outline: {outline_context}.
        Focus on vivid imagery, sensory details, and thematic relevance.""",
        expected_output="A richly detailed description of the chapter's setting",
        agent=setting_description_agent,
        llm=manager_llm_config
    )

    dialogue_task = Task(
        description=f"""Develop all dialogue sequences for Chapter {chapter_number}, adhering to character profiles and the outline: {outline_context}.
        Ensure dialogue is natural, advances the plot, and reveals character.""",
        expected_output="Realistic and engaging dialogue that aligns with character and plot",
        agent=dialogue_specialist,
        llm=manager_llm_config
    )

    write_task = Task(
        description=f"""Write Chapter {chapter_number} ({min_words}-{max_words} words) based on the outline: {outline_context}. MUST INCLUDE:
        - Detailed character interactions
        - Vivid setting descriptions from the Setting Description Agent
        - Multi-paragraph dialogue sequences from the Dialogue Specialist
        - Sensory details (smells, sounds, textures)
        - Internal character monologues
        If below {min_words} words, ADD:
        - Extended scene descriptions
        - Additional character backstory elements
        - Environmental observations
        Incorporate creative twists with a frequency of {genre_config.get('CREATIVE_TWISTS_FREQUENCY')}, experiment with narrative voice as defined by {genre_config.get('NARRATIVE_VOICE_EXPERIMENTATION')}, and explore themes with a freedom level of {genre_config.get('THEMATIC_EXPLORATION_FREEDOM')}.
        """,
        expected_output="Full chapter text meeting word count requirements",
        agent=writer,
        context=[research_task, setting_description_task, dialogue_task, outline_creator_task],
        llm=manager_llm_config
    )

    critic_task = Task(
        description=f"Provide detailed critique of Chapter {chapter_number}",
        expected_output="List of improvements needed with specific examples",
        agent=critic,
        context=[write_task],
        llm=manager_llm_config
    )

    revise_task = Task(
        description=f"""Revise Chapter {chapter_number} incorporating:
        - Critic feedback
        - Improved continuity
        - Enhanced character development""",
        expected_output="Polished chapter draft",
        agent=reviser,
        context=[write_task, critic_task],
        llm=manager_llm_config
    )

    edit_task = Task(
        description=f"""Final edit of Chapter {chapter_number}. ENSURE:
        - Word count: {min_words}-{max_words}
        - Grammar/style consistency
        - Adherence to outline
        - Proper paragraph structure""",
        expected_output="Publication-ready chapter",
        agent=editor,
        context=[revise_task],
        llm=manager_llm_config
    )

    feedback_review_task = Task(
        description=f"""Review and synthesize feedback from the Critic and Editor for Chapter {chapter_number}.
        Provide the Writer with a prioritized list of actionable feedback.""",
        expected_output="Concise, prioritized feedback for the Writer",
        agent=feedback_reviewer,
        context=[critic_task, edit_task],
        llm=manager_llm_config
    )

    return [research_task, setting_description_task, dialogue_task, write_task, critic_task, revise_task, edit_task, feedback_review_task]

# Chapter generation loop
for chapter_number in range(1, num_chapters + 1):
    chapter_tasks = create_chapter_tasks(chapter_number, outline_context, genre_config, agents, MANAGER_LLM_CONFIG)

    # Configure hierarchical crew with proper manager
    chapter_crew = Crew(
        agents=[agent for agent in agents if agent.role in ['Writer', 'Researcher', 'Critic', 'Reviser', 'Editor', 'Feedback Reviewer', 'Dialogue Specialist', 'Setting Description Agent']],
        tasks=chapter_tasks,
        verbose=True,
        process=Process.hierarchical,
        manager_llm=MANAGER_LLM_CONFIG
    )

    # Generation with validation
    valid = False
    attempts = 0
    while not valid and attempts < 3:
        try:
            for task in chapter_tasks:
                logging.info(f"Starting task: {task.description[:50]}... by {task.agent.role}")

                response = task.execute(context=task.context)
                logging.info(f"Task {task.description[:50]}... by {task.agent.role} completed")

                if task.agent.role == 'Writer':
                    chapter_content = response
                task.output = type('obj', (object,), {'value': response, 'raw_output': response, 'task': task})()

            # Validate word count
            word_count = len(re.findall(r'\w+', chapter_content))
            if word_count >= genre_config['MIN_WORDS_PER_CHAPTER']:
                valid = True
            else:
                print(f"Regenerating Chapter {chapter_number} (attempt {attempts+1}), word count: {word_count}")
                attempts += 1
                # Reset tasks for regeneration
                for task in chapter_tasks:
                    task.output = None

        except Timeout as e:  # Catch timeout errors
            logging.error(f"Timeout error during chapter generation: {e}")
            attempts += 1
            time.sleep(5) # short delay before retry

            # Reset tasks for regeneration
            for task in chapter_tasks:
                task.output = None

        except Exception as e:
            logging.error(f"Error generating chapter {chapter_number}: {str(e)}")
            attempts += 1

            # Reset tasks for regeneration
            for task in chapter_tasks:
                task.output = None

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
