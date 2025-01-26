import os
import shutil
import importlib
from crewai import Task, Crew, Process
from dotenv import load_dotenv
from agents import create_agents
import logging

# Configure logging for main.py
logging.basicConfig(
    filename='book_writer.log',
    filemode='a',  # Append to the log file
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger("Main")

# Configure logging for agent communications - NEW LOGGER
comm_logger = logging.getLogger("AgentCommunicationLogger")
comm_logger.setLevel(logging.INFO)
comm_handler = logging.FileHandler('agent_communication.log', mode='a') # Separate log file
comm_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
comm_handler.setFormatter(comm_formatter)
comm_logger.addHandler(comm_handler)


# Load environment variables from .env file
load_dotenv()

# Define the model to be used by the agents
model_to_use = f"ollama/{os.getenv('OLLAMA_MODEL')}"
logger.info(f"Using model: {model_to_use}")

# Specify the genre from the .env file
GENRE = os.getenv('GENRE', 'literary_fiction')  # Default to 'literary_fiction' if not specified
logger.info(f"Using genre: {GENRE}")

# Function to load configuration from the selected genre
def load_genre_config(genre):
    try:
        genre_module = importlib.import_module(f"genres.{genre}")
        config = {k: v for k, v in genre_module.__dict__.items() if not k.startswith("_")}
        config['GENRE'] = genre  # Add the genre name to the config
        logger.info(f"Successfully loaded genre configuration for {genre}")
        return config
    except ModuleNotFoundError:
        logger.error(f"Genre configuration for '{genre}' not found. Using default settings.")
        return {}

# Load the genre configuration
genre_config = load_genre_config(GENRE)

# Get the number of chapters from the genre config
num_chapters = genre_config.get('NUM_CHAPTERS', 3)
logger.info(f"Number of chapters: {num_chapters}")

# Create agents using the function from agents.py, passing num_chapters and an empty outline_context for now
agents = create_agents(model_to_use, num_chapters, "", genre_config)

# Assign agents to variables
story_planner, outline_creator, setting_builder, character_agent, relationship_architect, plot_agent, writer, editor, memory_keeper, researcher, critic, reviser, outline_compiler, item_developer = agents

# Get the initial prompt from the .env file
initial_prompt = os.getenv('INITIAL_PROMPT', "A group of friends decides to spend a memorable day at the beach. Each friend has a different idea of what makes a perfect beach day, leading to a series of adventures and misadventures as they try to make the most of their time together.")
logger.info(f"Initial prompt: {initial_prompt}")

story_planning_task = Task( # ... (rest of story_planning_task, setting_building_task, character_development_task, relationship_architecture_task, item_development_task, outline_creator_task, outline_compiler_task are the same as before) ...
# ... (rest of outline_crew definition and kickoff for outline generation - same as before) ...

# Function to create tasks for each chapter
def create_chapter_tasks(chapter_number, outline_context, context_window_size, genre_config):
    min_words = genre_config.get('MIN_WORDS_PER_CHAPTER', 1600)
    max_words = genre_config.get('MAX_WORDS_PER_CHAPTER', 3000)

    research_task = Task( # ... (research_task definition - same as before) ... )
    write_task = Task( # ... (write_task definition - same as before) ... )
    critic_task = Task( # ... (critic_task definition - same as before) ... )
    revise_task = Task( # ... (revise_task definition - same as before) ... )
    edit_task = Task( # ... (edit_task definition - same as before) ... )

    chapter_outline = ""
    if outline_text:
        chapter_start = outline_text.find(f"Chapter {chapter_number}:")
        if chapter_start != -1:
            chapter_end = outline_text.find(f"Chapter {chapter_number + 1}:")
            if chapter_end == -1:
                chapter_end = len(outline_text)
            chapter_outline = outline_text[chapter_start:chapter_end]

    logger.debug(f"Debug: Chapter {chapter_number} - research_task.output: {research_task.output}") # ADDED DEBUG
    logger.debug(f"Debug: Chapter {chapter_number} - outline_creator_task.output: {outline_creator_task.output}") # ADDED DEBUG

    write_task = Task( # ... (write_task definition - same as before) ... ) # REPEATED for context - no change needed
    critic_task = Task( # ... (critic_task definition - same as before) ... ) # REPEATED for context - no change needed
    revise_task = Task( # ... (revise_task definition - same as before) ... ) # REPEATED for context - no change needed
    edit_task = Task( # ... (edit_task definition - same as before) ... ) # REPEATED for context - no change needed


    return [research_task, write_task, critic_task, revise_task, edit_task]

# Function to clear the output folder
def clear_output_folder(folder): # ... (clear_output_folder function - same as before) ...

# Clear the output folder before generating new content
clear_output_folder(output_folder) # ... (clear_output_folder call - same as before) ...

# Get the context window size from the .env file
context_window_size = int(os.getenv('OLLAMA_CONTEXT_WINDOW', 4096)) # ... (context_window_size retrieval - same as before) ...

# Check if the model_to_use is an Ollama model
if model_to_use.startswith("ollama/"): # ... (Ollama model context window check - same as before) ...

# Initialize a list to store chapter outputs
chapter_outputs = [] # ... (chapter_outputs initialization - same as before) ...

# Loop through each chapter and create a crew to write it
for chapter_number in range(1, num_chapters + 1): # ... (chapter loop - same as before) ...
    try:
        chapter_crew.kickoff()
        logger.info(f"Chapter {chapter_number} generation complete.")

        # Access the output of the write_task directly from chapter_tasks
        write_task = chapter_tasks[1]  # write_task is the second task in the list
        logger.debug(f"Debug: write_task.output: {write_task.output}") # ADDED DEBUG - check again in chapter loop
        logger.debug(f"Debug: write_task.output.__dict__: {write_task.output.__dict__}") # ADDED DEBUG - inspect object

        if write_task.output:
            print(f"Debug: write_task.output: {write_task.output}")
            chapter_content = write_task.output.output_value # NEW CORRECT LINE - ACCESSING output_value
            chapter_outputs.append(chapter_content)
            logger.info(f"Successfully generated content for Chapter {chapter_number}")
            logger.debug(f"Raw chapter content: {chapter_content}")

            # Post-process the chapter content to add paragraph tags
            paragraphs = str(chapter_content).split("\n\n")
            formatted_paragraphs = [f"<p>{p.strip()}</p>" for p in paragraphs if p.strip()]
            formatted_text = "\n".join(formatted_paragraphs)
            logger.debug(f"Formatted chapter content: {formatted_text}")

            # Wrap the chapter in basic HTML tags
            html_content = f"""<!DOCTYPE html>
            <html>
            <head>
                <title>A Day at the Beach - Chapter {chapter_number}</title>
            </head>
            <body>
                <h1>Chapter {chapter_number}</h1>
                {formatted_text}
            </body>
            </html>"""

            # Define the output file path for the chapter
            output_file = os.path.join(output_folder, f"beach_story_chapter_{chapter_number}.html")

            # Output the chapter to an HTML file
            with open(output_file, "w") as f:
                f.write(html_content)
            logger.info(f"Chapter {chapter_number} written to {output_file}")
        else:
            logger.error(f"Chapter {chapter_number} generation failed. No output file created.")

    except Exception as e:
        logger.exception(f"An error occurred during generation of Chapter {chapter_number}.")
        continue  # Move to the next chapter even if an error occurs

print("######################")
print("Story generation complete.")