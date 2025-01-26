import os
import importlib
import re
from crewai import Task, Crew, Process
from dotenv import load_dotenv
import logging
import warnings

# PyWriter project imports:
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

# Get the initial prompt
initial_prompt = os.getenv('INITIAL_PROMPT', "A group of friends decides to spend a memorable day at the beach. Each friend has a different idea of what makes a perfect beach day, leading to a series of adventures and misadventures as they try to make the most of their time together.")

# (Here, you would define tasks similar to what's in your original `test_outline.py`, but this is commented out in your example)
# ... (Task definitions omitted for brevity) ...

# Instead of creating a Crew and running it, we'll create the outline manually using PyWriter classes.

# Create a Novel instance
novel = Novel()
novel.title = 'Generated Outline Test'
novel.authorName = 'Test Author'

# 2. Create chapters and add them to the novel.
chapter1 = Chapter()
chapter1.title = "Chapter 1: Arrival"
chapter1.chId = '1'
chapter1.chLevel = 0  # 0 for chapter, 1 for part (section)
chapter1.chType = 0   # 0 for Normal, 1 for Notes, 2 for Todo, 3 for Unused
novel.chapters[chapter1.chId] = chapter1
novel.srtChapters.append(chapter1.chId)

chapter2 = Chapter()
chapter2.title = "Chapter 2: The Sandcastle"
chapter2.chId = '2'
chapter2.chLevel = 0  # 0 for chapter, 1 for part (section)
chapter2.chType = 0
novel.chapters[chapter2.chId] = chapter2
novel.srtChapters.append(chapter2.chId)

# 3. Create scenes and add them to the chapters.

scene1 = Scene()
scene1.title = "Arrival at the Beach"
scene1.scId = '1'
scene1.desc = "The friends arrive at the beach and are amazed by the view."
scene1.sceneContent = 'Scene 1 content' # Generate with agents later
novel.scenes[scene1.scId] = scene1
chapter1.srtScenes.append(scene1.scId)

scene2 = Scene()
scene2.title = "Building a Sandcastle"
scene2.scId = '2'
scene2.desc = "They start building an elaborate sandcastle, but things go wrong."
scene2.sceneContent = 'Scene 2 content' # Generate with agents later
novel.scenes[scene2.scId] = scene2
chapter1.srtScenes.append(scene2.scId)

scene3 = Scene()
scene3.title = "A Special Find"
scene3.scId = '3'
scene3.desc = "One of the friends finds a special item at the beach."
scene3.sceneContent = 'Scene 3 content' # Generate with agents later
novel.scenes[scene3.scId] = scene3
chapter2.srtScenes.append(scene3.scId)

# 4. Create a Yw7File instance and link it to the novel.
yw7File = Yw7File('book-output/outline.yw7')  # Replace with your desired output path
yw7File.novel = novel

# 5. Write the .yw7 file.
try:
    yw7File.write()
    print(f"Outline written to {yw7File.filePath}")
except Exception as e:
    print(f"Error writing outline: {e}")

print("Test complete.")