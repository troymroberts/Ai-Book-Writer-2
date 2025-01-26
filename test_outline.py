import os
import importlib
from crewai import Task, Crew, Process
from dotenv import load_dotenv
from agents import create_agents
import logging
import warnings

# Configure logging for outline testing
logging.basicConfig(
    filename='outline_test.log',
    filemode='a',  # Append to the log file
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger("OutlineTest")

# Suppress the specific deprecation warning from litellm
warnings.filterwarnings("ignore", category=DeprecationWarning, module="litellm")

# Load environment variables from .env file
load_dotenv()

# Define the model to be used by the agents
model_to_use = f"ollama/{os.getenv('OLLAMA_MODEL')}"
logger.info(f"Using model: {model_to_use}")

# Specify the genre from the .env file
GENRE = os.getenv('GENRE', 'literary_fiction')
logger.info(f"Using genre: {GENRE}")

# Function to load configuration from the selected genre
def load_genre_config(genre):
    try:
        genre_module = importlib.import_module(f"genres.{genre}")
        config = {k: v for k, v in genre_module.__dict__.items() if not k.startswith("_")}
        config['GENRE'] = genre
        return config
    except ModuleNotFoundError:
        logger.error(f"Genre configuration for '{genre}' not found. Using default settings.")
        return {}

# Load the genre configuration
genre_config = load_genre_config(GENRE)

# Get the number of chapters from the genre config
num_chapters = genre_config.get('NUM_CHAPTERS', 3)

# Create agents
agents = create_agents(model_to_use, num_chapters, "", genre_config)
story_planner, outline_creator, setting_builder, character_agent, relationship_architect, plot_agent, writer, editor, memory_keeper, researcher, critic, reviser, outline_compiler = agents

# Get the initial prompt
initial_prompt = os.getenv('INITIAL_PROMPT', "A group of friends decides to spend a memorable day at the beach. Each friend has a different idea of what makes a perfect beach day, leading to a series of adventures and misadventures as they try to make the most of their time together.")

# Define the tasks (simplified for debugging)
story_planning_task = Task(
    description=f"""Develop a high-level story arc plan based on the initial premise: {initial_prompt}""",
    expected_output="A story arc plan.",
    agent=story_planner
)

setting_building_task = Task(
    description="Establish the main setting for the story.",
    expected_output="A description of the setting.",
    agent=setting_builder
)

character_development_task = Task(
    description="Develop brief profiles for 3 main characters.",
    expected_output="Character profiles.",
    agent=character_agent
)

relationship_architecture_task = Task(
    description="Define the relationships between the 3 main characters.",
    expected_output="Relationship dynamics.",
    agent=relationship_architect,
    context=[character_development_task]
)

outline_creator_task = Task(
    description="Create a simple chapter outline for 3 chapters.",
    expected_output="A 3-chapter outline.",
    agent=outline_creator,
    context=[story_planning_task, character_development_task, setting_building_task, relationship_architecture_task]
)

outline_compiler_task = Task(
    description="""Compile the final outline for the story, integrating all previously generated content. 
    Format as a simple outline.
    
    - STORY ARC PLAN
    - SETTING DETAILS
    - CHARACTER PROFILES
    - RELATIONSHIP DYNAMICS
    - CHAPTER OUTLINES""",
    expected_output="A combined outline.",
    agent=outline_compiler,
    context=[story_planning_task, setting_building_task, character_development_task, relationship_architecture_task, outline_creator_task]
)

# Create the outline crew
outline_crew = Crew(
    agents=[story_planner, setting_builder, character_agent, relationship_architect, outline_creator, outline_compiler],
    tasks=[story_planning_task, setting_building_task, character_development_task, relationship_architecture_task, outline_creator_task, outline_compiler_task],
    verbose=True,
    process=Process.sequential
)

# Run the outline generation and print intermediate outputs
print("Starting outline generation...")
outline_result = outline_crew.kickoff()

print("\nOutline generation complete.\n")
print("-" * 30)
print("Individual Task Outputs:")

# Check for the existence of each task's output before accessing it
if story_planning_task.output:
    print(f"\nStory Planner Output:\n{story_planning_task.output.result}")

if setting_building_task.output:
    print(f"\nSetting Builder Output:\n{setting_building_task.output.result}")

if character_development_task.output:
    print(f"\nCharacter Developer Output:\n{character_development_task.output.result}")

if relationship_architecture_task.output:
    print(f"\nRelationship Architect Output:\n{relationship_architecture_task.output.result}")

if outline_creator_task.output:
    print(f"\nOutline Creator Output:\n{outline_creator_task.output.result}")

# Accessing the result attribute of TaskOutput for the Outline Compiler
if outline_compiler_task.output:
    outline_text = outline_compiler_task.output.result
    print(f"\nOutline Compiler Output:\n{outline_text}")
else:
    outline_text = ""
    print(f"\nOutline Compiler Output:\nTask did not produce output.")

print("-" * 30)

# Save the outline to a file
output_folder = "book-output"
os.makedirs(output_folder, exist_ok=True)
outline_file_path = os.path.join(output_folder, "outline.txt")
with open(outline_file_path, "w") as f:
    f.write(outline_text)  # Write the outline_text string

print(f"Outline written to {outline_file_path}")
