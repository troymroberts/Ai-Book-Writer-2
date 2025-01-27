--- START OF FILE main.py ---
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

story_planning_task = Task(
    description=f"""Develop a high-level story arc plan based on the initial premise: {initial_prompt}""",
    expected_output="A story arc plan.",
    agent=story_planner,
    logger=comm_logger
)

setting_building_task = Task(
    description="Establish the main setting for the story, including locations and world details.",
    expected_output="Detailed setting descriptions.",
    agent=setting_builder,
    logger=comm_logger
)

character_development_task = Task(
    description="Develop detailed profiles for 3 main characters, including full names, backstories, personalities, and relationships.",
    expected_output="Comprehensive character profiles.",
    agent=character_agent,
    logger=comm_logger
)

relationship_architecture_task = Task(
    description="Define the relationships and family structures between the main characters, detailing their dynamics and histories.",
    expected_output="Detailed relationship dynamics and family structures.",
    agent=relationship_architect,
    context=[character_development_task],
    logger=comm_logger
)

item_development_task = Task(
    description="Develop a list of key items relevant to the story, detailing their descriptions and significance.",
    expected_output="List of key items with descriptions.",
    agent=item_developer,
    logger=comm_logger
)

outline_creator_task = Task(
    description=f"""Create a detailed chapter outline for each chapter, including chapter titles, key events, character developments, setting, and tone.
                Use the following for context:
                STORY ARC PLAN: {story_planning_task.output}
                SETTING DETAILS: {setting_building_task.output}
                CHARACTER PROFILES: {character_development_task.output}
                RELATIONSHIP DYNAMICS: {relationship_architecture_task.output}
                ITEM DESCRIPTIONS: {item_development_task.output}
                """,
    expected_output="Detailed chapter outlines.",
    agent=outline_creator,
    context=[story_planning_task, setting_building_task, character_development_task, relationship_architecture_task, item_development_task],
    logger=comm_logger
)

outline_compiler_task = Task(
    description="""Compile the final book outline, integrating all previously generated content.
                Ensure the outline is well-structured, detailed, and follows the specified format.
                Output the ENTIRE outline, including all sections.
                Use the following for context:
                STORY ARC PLAN: {story_planning_task.output}
                SETTING DETAILS: {setting_building_task.output}
                CHARACTER PROFILES: {character_development_task.output}
                RELATIONSHIP DYNAMICS: {relationship_architecture_task.output}
                ITEM DESCRIPTIONS: {item_development_task.output}
                CHAPTER OUTLINES: {outline_creator_task.output}
                """,
    expected_output="A complete and cohesive book outline document.",
    agent=outline_compiler,
    context=[story_planning_task, setting_building_task, character_development_task, relationship_architecture_task, item_development_task, outline_creator_task],
    logger=comm_logger
)


outline_crew = Crew(
    agents=agents[:-1],  # exclude the outline_compiler for now from the outline crew
    tasks=[
        story_planning_task,
        setting_building_task,
        character_development_task,
        relationship_architecture_task,
        item_development_task,
        outline_creator_task,
        outline_compiler_task
    ],
    verbose=True,  # Changed from 2 to True
    process=Process.sequential  # Tasks will be executed in order
)

output_folder = "book-output"

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Clear the output folder before generating new content
def clear_output_folder(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

clear_output_folder(output_folder)

print(" ভূমিক্স######################")
print("Starting outline generation...")
outline = outline_crew.kickoff()
print("Outline generation complete.")
print("######################")

# Output outline to a text file
outline_text_file = os.path.join(output_folder, "outline.txt")
with open(outline_text_file, "w") as f:
    f.write(str(outline))
logger.info(f"Outline saved to {outline_text_file}")

# Get the outline text for chapter tasks context
outline_text = ""
if outline_compiler_task.output:
    outline_text = outline_compiler_task.output.output_value
else:
    outline_text = "No outline generated."
logger.info(f"Outline Context for Chapter Tasks: {outline_text[:100]}...") # Log first 100 chars of outline

# Get the context window size from the .env file
context_window_size = int(os.getenv('OLLAMA_CONTEXT_WINDOW', 4096))
logger.info(f"Context window size: {context_window_size}")

# Check if the model_to_use is an Ollama model
if model_to_use.startswith("ollama/"):
    if context_window_size < 4096:
        logger.warning("Using Ollama model with context window size less than 4096. Consider increasing OLLAMA_CONTEXT_WINDOW in .env for potentially better results.")
    if context_window_size > 4096:
        logger.info("Using Ollama model with context window size greater than 4096.")


# Function to create tasks for each chapter
def create_chapter_tasks(chapter_number, outline_context, context_window_size, genre_config):
    min_words = genre_config.get('MIN_WORDS_PER_CHAPTER', 1600)
    max_words = genre_config.get('MAX_WORDS_PER_CHAPTER', 3000)

    research_task = Task(
        description=f"""Research specific details needed for chapter {chapter_number}, based on the chapter outline and overall story context. Pay special attention to details about beach activities, marine life, and coastal weather patterns.
                    Chapter Outline: {outline_context}""",
        expected_output="Research findings and specific details for chapter.",
        agent=researcher,
        logger=comm_logger
    )

    outline_creator_task = Task(
        description=f"""Refine and detail the chapter outline for chapter {chapter_number}, based on the overall book outline and incorporating genre-specific elements. Expand on key events, character developments, setting details, and tone for this chapter.
                    Overall Book Outline: {outline_context}""",
        expected_output="Detailed and refined chapter outline.",
        agent=outline_creator,
        context=[story_planning_task, setting_building_task, character_development_task, relationship_architecture_task, item_development_task], # using outline crew tasks as context
        logger=comm_logger
    )

    logger.debug(f"Debug: Chapter {chapter_number} - research_task.output: {research_task.output}") # ADDED DEBUG
    logger.debug(f"Debug: Chapter {chapter_number} - outline_creator_task.output: {outline_creator_task.output}") # ADDED DEBUG

    write_task = Task(
        description=f"""Write chapter {chapter_number} of the novel, following the detailed chapter outline and incorporating research findings. Expand on the key events, character developments, and setting descriptions with vivid prose and engaging dialogue.
                    Chapter Outline: {outline_creator_task.output}
                    Research Findings: {research_task.output}
                    Overall Book Outline: {outline_context}
                    Ensure chapter is at least {min_words} words and not exceeding {max_words} words.""",
        expected_output="Complete draft of chapter content in HTML format.",
        agent=writer,
        context=[outline_creator_task, research_task, story_planning_task, setting_building_task, character_development_task, relationship_architecture_task, item_development_task], # using outline crew tasks as context
        logger=comm_logger
    )

    critic_task = Task(
        description=f"""Critically review chapter {chapter_number} for plot holes, inconsistencies, pacing issues, and areas for improvement in narrative structure and character development. Evaluate scene order and suggest reordering for better flow and impact.
                    Chapter Draft: {write_task.output}
                    Chapter Outline: {outline_creator_task.output}
                    Overall Book Outline: {outline_context}""",
        expected_output="Constructive criticism and feedback on chapter draft, including scene reordering suggestions.",
        agent=critic,
        context=[write_task, outline_creator_task, story_planning_task, setting_building_task, character_development_task, relationship_architecture_task, item_development_task], # using outline crew tasks as context
        logger=comm_logger
    )

    revise_task = Task(
        description=f"""Revise chapter {chapter_number} based on feedback from the Critic and Editor. Ensure revisions improve coherence, consistency, and polish. Incorporate scene reordering suggestions and rewrite transitions for smooth flow.
                    Critic Feedback: {critic_task.output}
                    Editor Feedback: {edit_task.output}
                    Original Chapter Draft: {write_task.output}
                    Chapter Outline: {outline_creator_task.output}
                    Overall Book Outline: {outline_context}""",
        expected_output="Revised and polished chapter content in HTML format.",
        agent=reviser,
        context=[critic_task, edit_task, write_task, outline_creator_task, story_planning_task, setting_building_task, character_development_task, relationship_architecture_task, item_development_task], # using outline crew tasks as context
        logger=comm_logger
    )

    edit_task = Task(
        description=f"""Edit chapter {chapter_number} for grammar, style, clarity, and adherence to the chapter outline and word count requirements. Ensure the chapter is well-written and free of errors.
                    Chapter Draft: {write_task.output}
                    Chapter Outline: {outline_creator_task.output}
                    Overall Book Outline: {outline_context}
                    Word count should be between {min_words} and {max_words} words.""",
        expected_output="Edited and proofread chapter content, ready for final review.",
        agent=editor,
        context=[write_task, outline_creator_task, story_planning_task, setting_building_task, character_development_task, relationship_architecture_task, item_development_task], # using outline crew tasks as context
        logger=comm_logger
    )

    return [research_task, write_task, critic_task, revise_task, edit_task]

# Initialize a list to store chapter outputs
chapter_outputs = []

# Loop through each chapter and create a crew to write it
for chapter_number in range(1, num_chapters + 1):
    try:
        chapter_tasks = create_chapter_tasks(chapter_number, outline_text, context_window_size, genre_config)
        chapter_crew = Crew(
            agents=[researcher, writer, critic, editor, reviser], # Removed memory_keeper from chapter_crew
            tasks=chapter_tasks,
            verbose=True, # Chapter process verbosity: 1 for smart, 2 for high - changed to True
            process=Process.sequential # For chapter generation, process sequentially
        )
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