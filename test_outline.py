import os
import importlib
import re
from crewai import Task, Crew, Process
from dotenv import load_dotenv
from agents import create_agents
import logging
import warnings

from pywriter.model.novel import Novel
from pywriter.model.chapter import Chapter
from pywriter.model.scene import Scene
from pywriter.yw.yw7_file import Yw7File
from pywriter.model.id_generator import create_id

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
    print(f"\nStory Planner Output:\n{story_planning_task.output.output_value}")

if setting_building_task.output:
    print(f"\nSetting Builder Output:\n{setting_building_task.output.output_value}")

if character_development_task.output:
    print(f"\nCharacter Developer Output:\n{character_development_task.output.output_value}")

if relationship_architecture_task.output:
    print(f"\nRelationship Architect Output:\n{relationship_architecture_task.output.output_value}")

if outline_creator_task.output:
    print(f"\nOutline Creator Output:\n{outline_creator_task.output.output_value}")

# Accessing the result attribute of TaskOutput for the Outline Compiler
if outline_compiler_task.output:
    outline_text = outline_compiler_task.output.output_value
    print(f"\nOutline Compiler Output:\n{outline_text}")
else:
    outline_text = ""
    print(f"\nOutline Compiler Output:\nTask did not produce output.")

print("-" * 30)

# Create a Novel instance
novel = Novel()
novel.title = 'Generated Outline'

# Function to parse the generated text output and convert it into a structured format
def parse_outline(outline_text):
    chapters = []
    current_chapter = None
    current_scene = None

    # Use regular expressions to find chapter and scene titles
    chapter_pattern = re.compile(r"Chapter (\d+): (.+)")
    scene_pattern = re.compile(r"Scene (\d+): (.+)")

    lines = outline_text.split('\n')
    for line in lines:
        line = line.strip()
        chapter_match = chapter_pattern.match(line)
        scene_match = scene_pattern.match(line)

        if chapter_match:
            # If there's a current scene, add it to the last chapter
            if current_scene and current_chapter:
                current_chapter['scenes'].append(current_scene)

            # If there's a current chapter, add it to the list of chapters
            if current_chapter:
                chapters.append(current_chapter)

            # Start a new chapter
            chapter_number = chapter_match.group(1)
            chapter_title = chapter_match.group(2)
            current_chapter = {'title': f"Chapter {chapter_number}: {chapter_title}", 'scenes': []}
            current_scene = None  # Reset the current scene when starting a new chapter
        elif scene_match:
            # If there's a current scene, add it to the current chapter
            if current_scene and current_chapter:
                current_chapter['scenes'].append(current_scene)

            # Start a new scene
            scene_number = scene_match.group(1)
            scene_title = scene_match.group(2)
            current_scene = {'title': f"Scene {scene_number}: {scene_title}", 'desc': ''}
        elif current_scene is not None:
            # Append non-empty lines to the description of the current scene
            if line:
                current_scene['desc'] += line + ' '

    # Add the last scene to the last chapter if it exists
    if current_scene and current_chapter:
        current_chapter['scenes'].append(current_scene)

    # Add the last chapter to the list of chapters if it exists
    if current_chapter:
        chapters.append(current_chapter)

    return chapters

# Check if outline_compiler_task.output exists and has .output_value
if outline_compiler_task.output and hasattr(outline_compiler_task.output, 'output_value'):
    outline_text = outline_compiler_task.output.output_value
    print(f"\nOutline Compiler Output:\n{outline_text}")

    # Parse the outline text and populate outline_data
    outline_data = parse_outline(outline_text)
else:
    outline_text = ""
    outline_data = []
    print(f"\nOutline Compiler Output:\nTask did not produce output or has no .output_value attribute.")

# Initialize counters for chapter and scene IDs
chapter_id_counter = 1
scene_id_counter = 1

for chapter_data in outline_data:
    # Create a new chapter
    chapter = Chapter()
    chapter.title = chapter_data['title']
    chapter.chType = 0 # 0 = normal
    chapter.chLevel = 0 # 0 = normal
    chapter.chId = str(chapter_id_counter)
    novel.chapters[chapter.chId] = chapter
    novel.srtChapters.append(chapter.chId)
    chapter_id_counter += 1

    for scene_data in chapter_data['scenes']:
        # Create a new scene
        scene = Scene()
        scene.title = scene_data['title']
        scene.desc = scene_data['desc']
        scene.status = 1 # 1 = Outline
        scene.scType = 0 # 0 = Normal
        scene.scId = str(scene_id_counter)
        scene.sceneContent = '' # No scene content added
        novel.scenes[scene.scId] = scene

        # Associate the scene with the current chapter
        chapter.srtScenes.append(scene.scId)
        scene_id_counter += 1

# Create the output folder if it doesn't exist
output_folder = "book-output"
os.makedirs(output_folder, exist_ok=True)

# Create a Yw7File instance
yw7File = Yw7File(f'{output_folder}/outline.yw7')
yw7File.novel = novel

# Write the .yw7 file
try:
    yw7File.write()
    print(f"Outline written to {yw7File.filePath}")
except Exception as e:
    print(f"Error writing .yw7 file: {e}")

print("Test complete.")