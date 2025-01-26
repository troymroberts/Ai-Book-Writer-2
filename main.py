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

# Define the task for the Story Planner agent
story_planning_task = Task(
    description=f"""{genre_config.get('STORY_PLANNING_DESCRIPTION', "Develop a high-level story arc plan based on the initial premise.")}

    Initial Premise: {initial_prompt}

    Format your output EXACTLY as:
    STORY_ARC_PLAN:
    - Overall Story Arc:
    [Describe the major phases of the story: Setup, Rising Action, Climax, Falling Action, Resolution]

    - Major Plot Points:
    [List each major event that drives the story forward in sequence]

    - Character Arc Overview:
    [For each main character, describe their intended development path across the book]

    - Pacing Plan:
    [Describe the intended pacing for different sections of the book, noting where pacing should be faster or slower to maximize impact]

    - Chapter Outline Review:
    [Provide feedback on the chapter outlines in terms of how well they fit into the planned story arc and pacing. Suggest any adjustments needed to strengthen the overall narrative]

    Always provide specific, detailed content - never use placeholders. Focus on actionable feedback to improve story structure and pacing.
    """,
    expected_output="A comprehensive story arc plan.",
    agent=story_planner
)
logging.getLogger("StoryPlanner").info(f"Story planning task assigned: {story_planning_task.description}")

# Define the task for the Setting Builder agent
setting_building_task = Task(
    description=f"""{genre_config.get('SETTING_BUILDING_DESCRIPTION', "Establish all settings and world elements needed for the entire story.")}

    Format your response as:
    SETTING_DETAILS:

    [LOCATION NAME - Chapter Number(s)]:
    - Physical Description: [detailed description including sensory details]
    - Atmosphere and Mood: [mood, time of day, lighting, weather, etc.]
    - Key Features: [important objects, layout elements, points of interest]
    - Thematic Resonance: [how this setting enhances story themes and character emotions]

    [RECURRING SETTINGS - Locations Appearing Multiple Times]:
    - [LOCATION NAME]: [Description of how this setting evolves across chapters, noting changes and recurring elements]

    [SETTING TRANSITIONS - Connections Between Locations]:
    - [LOCATION 1] to [LOCATION 2]: [Describe how characters move between these settings and any significant spatial relationships or transitions]

    Ensure every setting is vividly described and contributes meaningfully to the narrative.
    """,
    expected_output="Detailed descriptions of all settings and world elements.",
    agent=setting_builder
)
logging.getLogger("SettingBuilder").info(f"Setting building task assigned: {setting_building_task.description}")

# Define the task for the Character Agent
character_development_task = Task(
    description=f"""{genre_config.get('CHARACTER_DEVELOPMENT_DESCRIPTION', "Develop detailed character profiles for all main and significant supporting characters.")}
    Create character arcs that span across {num_chapters} chapters.

    Format your response as:
    CHARACTER_PROFILES:

    [CHARACTER FULL NAME] (Age: [Character's Age])
    - Backstory: [Detailed backstory relevant to their current role in the story, including significant life events and relationships]
    - Motivations: [Primary and secondary motivations driving their actions]
    - Personality: [Key personality traits, including strengths, weaknesses, quirks, and how they interact with others]
    - Relationships: [Significant relationships with other characters, noting dynamics, history, and current status. Include family, friends, rivals, love interests, etc.]
    - Physical Description: [Detailed physical description, including distinguishing features]
    - Character Stats:
        - Intelligence: [1-10 rating]
        - Charisma: [1-10 rating]
        - Education: [e.g., High School, College, Self-Educated]
        - Other relevant stats for the story
    - Speech Patterns: [Description of how the character speaks, including accent, tone, verbosity, and any specific speech habits or catchphrases]
    - Arc Overview: [Intended character arc across the story - how will they change and develop?]

    [CHARACTER ARCS - Detailed Chapter Breakdown]:
    - [CHARACTER FULL NAME] - Chapter [CHAPTER NUMBER]: [Describe specific character developments, actions, and emotional states within this chapter, linking to their overall arc]

    Ensure each character is richly developed and their journey is compelling and consistent.
    Limit character arcs and plot points to {num_chapters} chapters only.
    """,
    expected_output="Detailed character profiles and development plans, including full names, ages, backstories, motivations, personalities, relationships, and arc overviews.",
    agent=character_agent
)
logging.getLogger("CharacterCreator").info(f"Character development task assigned: {character_development_task.description}")

# Define the task for the Relationship Architect agent
relationship_architecture_task = Task(
    description=f"""{genre_config.get('RELATIONSHIP_ARCHITECTURE_DESCRIPTION', "Develop and manage the relationships between characters, including family structures, friendships, rivalries, and romantic relationships.")}
    Create relationship dynamics that are realistic, engaging, and contribute to the overall narrative.

    Format your response as:
    RELATIONSHIP_DYNAMICS:

    [CHARACTER 1 FULL NAME] and [CHARACTER 2 FULL NAME]:
    - Relationship Type: [e.g., siblings, friends, rivals, lovers, parent-child]
    - Relationship Backstory: [Detailed backstory of their relationship, including how they met, significant events, and past conflicts or alliances]
    - Current Status: [Description of their current relationship status, including any ongoing conflicts, loyalties, or emotional bonds]
    - Relationship Arc: [How their relationship will evolve throughout the story, potential turning points, and impact on the plot]

    [FAMILY STRUCTURE]:
    - Family Name: [Last name]
    - Family Members: [List of family members with their roles (e.g., father, mother, sister, brother)]
    - Family Dynamic: [Description of the overall family dynamic, including relationships between members, family values, and any significant family history]

    Ensure relationship dynamics are nuanced and contribute to the depth of the story.
    """,
    expected_output="Detailed relationship dynamics and family structures.",
    agent=relationship_architect,
    context=[character_development_task]  # Ensure access to character details
)
logging.getLogger("RelationshipArchitect").info(f"Relationship architecture task assigned: {relationship_architecture_task.description}")

# Define the task for the Item Developer agent
item_development_task = Task(
    description=f"""{genre_config.get('ITEM_DEVELOPMENT_DESCRIPTION', "Develop detailed item profiles for all significant items in the story.")}
    Create items that are relevant to the plot and world-building of the {num_chapters} chapter story.

    Format your response as:
    ITEM_PROFILES:

    [ITEM NAME]
    - Description: [Detailed description of the item, including its physical appearance, history, and any special properties]
    - Purpose in Story: [How the item is used in the plot and its significance to the characters or events]
    - Symbolic Meaning (if any): [Any symbolic or thematic resonance the item carries]
    - Chapters/Scenes of Appearance: [List of chapters and scenes where the item appears or is relevant]

    Ensure each item is well-defined and its role in the story is clear.
    """,
    expected_output="Detailed item profiles with descriptions, purpose, symbolic meaning, and chapters/scenes of appearance.",
    agent=item_developer
)
logging.getLogger("ItemDeveloper").info(f"Item development task assigned: {item_development_task.description}")


# Define the task for the Outline Creator agent
outline_creator_task = Task(
    description=f"""
    Create a detailed chapter outline for each of the {num_chapters} chapters individually, based on the following premise, the developed story arc plan, character profiles, relationship dynamics, setting details, and item profiles:

    Initial Premise: {initial_prompt}

    Story Arc Plan: [Provided by the Story Planner agent]

    Character Profiles: [Provided by the Character Agent]

    Relationship Dynamics: [Provided by the Relationship Architect Agent]

    Setting Details: [Provided by the Setting Builder Agent]

    Item Profiles: [Provided by the Item Developer Agent]

    Follow this EXACT format for each chapter:

    Chapter [N]: [Chapter Title]
    Title: [Same title as above]
    Key Events:
    - [Event 1]
    - [Event 2]
    - [Event 3]
    Character Developments: [Specific character moments and changes in this chapter]
    Setting: [Specific location and atmosphere for this chapter]
    Tone: [Specific emotional and narrative tone for this chapter]
    Items: [List any important items that feature prominently in this chapter]

    Repeat EXACTLY this format for all {num_chapters} chapters.

    Ensure that each chapter outline is comprehensive and detailed, providing a solid foundation for the writing process.
    """,
    expected_output=f"A detailed chapter outline for each of the {num_chapters} chapters.",
    agent=outline_creator,
    context=[story_planning_task, character_development_task, setting_building_task, relationship_architecture_task, item_development_task]
)
logging.getLogger("OutlineCreator").info(f"Outline creator task assigned: {outline_creator_task.description}")

# Define the task for the Outline Compiler agent
outline_compiler_task = Task(
    description=f"""
    Compile the final outline for the {num_chapters}-chapter story, integrating all previously generated content:

    - Overall Story Arc Plan: [Provided by the Story Planner agent]
    - Setting Details: [Provided by the Setting Builder Agent]
    - Character Profiles: [Provided by the Character Agent]
    - Relationship Dynamics: [Provided by the Relationship Architect Agent]
    - Chapter Outlines: [Provided by the Outline Creator Agent]
    - Item Profiles: [Provided by the Item Developer Agent]

    Format your response as:
    - STORY ARC PLAN: [Insert the Story Planner Agent's output here]
    - SETTING DETAILS: [Insert the Setting Builder Agent's output here]
    - CHARACTER PROFILES: [Insert the Character Agent's output here]
    - RELATIONSHIP DYNAMICS: [Insert the Relationship Architect Agent's output here]
    - CHAPTER OUTLINES: [Insert the Outline Creator Agent's output here]
    - ITEM PROFILES: [Insert the Item Developer Agent's output here]

    Combine all this information into a single, cohesive document. Ensure the outline is well-structured, detailed, and follows a logical sequence.
    """,
    expected_output=f"A comprehensive and well-structured outline for the {num_chapters}-chapter story, integrating all elements including item profiles.",
    agent=outline_compiler,
    context=[story_planning_task, setting_building_task, character_development_task, relationship_architecture_task, outline_creator_task, item_development_task]
)
logging.getLogger("OutlineCompiler").info(f"Outline compiler task assigned: {outline_compiler_task.description}")

# Create a Crew and assign the task
outline_crew = Crew(
    agents=[story_planner, setting_builder, character_agent, relationship_architect, outline_creator, outline_compiler, item_developer],
    tasks=[story_planning_task, setting_building_task, character_development_task, relationship_architecture_task, item_development_task, outline_creator_task, outline_compiler_task],
    verbose=True,
    process=Process.sequential
)

# Run the Crew to generate the outline
try:
    outline_result = outline_crew.kickoff()
    # Check if outline_result is a string and not empty
    if isinstance(outline_result, str) and outline_result.strip():
        outline_text = outline_result
        logger.info("Outline generation complete.")
        logger.debug(f"Outline result: {outline_text}")
    else:
        logger.error("Outline generation failed: Result is not a non-empty string.")
        outline_text = ""  # Assign an empty string to avoid UnboundLocalError later
except Exception as e:
    logger.exception("An error occurred during outline generation.")
    outline_text = ""

# Initialize outline_context even if outline_text is empty
outline_context = outline_text

# Create the book-output subfolder if it doesn't exist
output_folder = "book-output"
os.makedirs(output_folder, exist_ok=True)
logger.info(f"Output folder: {output_folder}")

# Save the outline to a file in the output folder
if outline_text:
    outline_file_path = os.path.join(output_folder, "outline.txt")
    with open(outline_file_path, "w") as f:
        f.write(outline_text)
    logger.info(f"Outline written to {outline_file_path}")
else:
    logger.error("Outline generation failed. No output file created.")

# Extract the outline context from the outline_result
if outline_text:
    outline_context = outline_text

    # Update agent goals and backstories with the outline context
    for agent in agents:
        agent.goal = agent.goal.replace("{outline_context}", outline_context)
        agent.backstory = agent.backstory.replace("{outline_context}", outline_context)

# Function to create tasks for each chapter
def create_chapter_tasks(chapter_number, outline_context, context_window_size, genre_config):
    min_words = genre_config.get('MIN_WORDS_PER_CHAPTER', 1600)
    max_words = genre_config.get('MAX_WORDS_PER_CHAPTER', 3000)

    research_task = Task(
        description=f"""Research any specific details needed for Chapter {chapter_number}, such as information about beach activities, marine life, or coastal weather patterns. Refer to the outline for context: {outline_context}""",
        expected_output=f"Accurate and relevant research findings to support Chapter {chapter_number}.",
        agent=researcher
    )
    logging.getLogger("Researcher").info(f"Research task for Chapter {chapter_number} assigned: {research_task.description}")

    # Extract the relevant part of the outline for this chapter
    chapter_outline = ""
    if outline_text:
        # Assuming your outline format has chapters clearly marked, e.g., "Chapter 1:\n..."
        chapter_start = outline_text.find(f"Chapter {chapter_number}:")
        if chapter_start != -1:
            chapter_end = outline_text.find(f"Chapter {chapter_number + 1}:")
            if chapter_end == -1:
                chapter_end = len(outline_text)  # End of the outline
            chapter_outline = outline_text[chapter_start:chapter_end]

    write_task = Task(
        description=f"""Write Chapter {chapter_number} based on the outline provided below.
            Each chapter MUST be at least {min_words} words and no more than {max_words} words. Consider this a HARD REQUIREMENT. If your output is shorter, continue writing until you reach this minimum length.
            Focus on engaging the reader with descriptive language and compelling character interactions.
            Expand on the key events, character developments, and setting described in the outline for this chapter.
            Use paragraphs to separate different parts of the story and improve readability.
            Pay close attention to the character profiles, including their stats and speech patterns, to create realistic and consistent dialogue.
            ONLY WRITE CHAPTER {chapter_number}. DO NOT WRITE ANY OTHER CHAPTERS.

            Chapter Outline:
            {chapter_outline}

            Your specific instructions for this chapter are:
            1. Write according to the detailed chapter outline, incorporating all Key Events, Character Developments, Setting, and Tone.
            2. Maintain consistent character voices and personalities as defined by the Character Agent.
            3. Vividly incorporate world-building details and settings as established by the Setting Builder.
            4. Create engaging and immersive prose that captures the intended tone and style for the genre and chapter.
            5. Ensure each chapter is a complete and satisfying scene with a clear beginning, middle, and end - do not leave scenes incomplete or abruptly cut off.
            6. Ensure smooth and logical transitions between paragraphs and scenes within the chapter.
            7. Add rich sensory details and descriptions of the environment and characters where appropriate to enhance immersion and engagement.

        Always reference the chapter outline, previous chapter content (as summarized by the Memory Keeper), established world elements, and character developments to ensure consistency and coherence.
            """,
        expected_output=f"Chapter {chapter_number} written in engaging prose with proper paragraph formatting and a minimum of {min_words} words.",
        agent=writer,
        context=[research_task, outline_creator_task]
    )
    logging.getLogger("Writer").info(f"Write task for Chapter {chapter_number} assigned: {write_task.description}")

    critic_task = Task(
        description=f"""Provide a critical review of Chapter {chapter_number}, identifying any plot holes, inconsistencies, or areas that need improvement. Refer to the outline for context: {outline_context}""",
        expected_output=f"Constructive criticism and suggestions for enhancing Chapter {chapter_number}.",
        agent=critic,
        context=[outline_creator_task, write_task]
    )
    logging.getLogger("Critic").info(f"Critic task for Chapter {chapter_number} assigned: {critic_task.description}")

    revise_task = Task(
        description=f"""Revise Chapter {chapter_number} based on feedback from the Critic and Editor. Ensure the chapter is coherent, consistent, and polished. Refer to the outline for context: {outline_context}""",
        expected_output=f"A revised version of Chapter {chapter_number} that incorporates feedback and improvements.",
        agent=reviser,
        context=[outline_creator_task, write_task]
    )
    logging.getLogger("Reviser").info(f"Revise task for Chapter {chapter_number} assigned: {revise_task.description}")

    edit_task = Task(
        description=f"""Edit Chapter {chapter_number}, focusing on grammar, style, and overall flow. Incorporate changes directly into the chapter text.
        Verify that the chapter meets the length requirement of between {min_words} and {max_words} words. If it's too short, provide specific feedback to the Writer on what areas need expansion.
        Refer to the outline for context: {outline_context}""",
        expected_output=f"The final, edited version of Chapter {chapter_number}, meeting the minimum word count requirement.",
        agent=editor,
        context=[outline_creator_task, write_task]
    )
    logging.getLogger("Editor").info(f"Edit task for Chapter {chapter_number} assigned: {edit_task.description}")

    return [research_task, write_task, critic_task, revise_task, edit_task]

# Function to clear the output folder
def clear_output_folder(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            logger.error(f"Failed to delete {file_path}. Reason: {e}")

# Clear the output folder before generating new content
clear_output_folder(output_folder)
logger.info("Output folder cleared.")

# Get the context window size from the .env file
context_window_size = int(os.getenv('OLLAMA_CONTEXT_WINDOW', 4096))  # Default to 4096
logger.info(f"Context window size from .env: {context_window_size}")

# Check if the model_to_use is an Ollama model
if model_to_use.startswith("ollama/"):
    try:
        # Extract the model name from the model_to_use string
        model_name = model_to_use.split('/')[1]

        # Use the ollama-python library to get model details including context window size
        from ollama import show
        model_info = show(model_name)  # Assuming 'show' is the correct function to get details
        ollama_context_window = int(model_info['parameters'].split('\n')[-2].split(' ')[-1])

        logger.info(f"Ollama model context window size: {ollama_context_window}")

        # You can now compare context_window_size and ollama_context_window
        if context_window_size != ollama_context_window:
            logger.warning(f"Context window size in .env ({context_window_size}) does not match Ollama model context window size ({ollama_context_window}). Using Ollama's setting.")
    except Exception as e:
        logger.exception("Error retrieving Ollama model information:")
else:
    logger.info("Not using an Ollama model. Context window size check skipped.")

# Initialize a list to store chapter outputs
chapter_outputs = []

# Loop through each chapter and create a crew to write it
for chapter_number in range(1, num_chapters + 1):
    logger.info(f"Starting generation for Chapter {chapter_number}")

    # Create tasks for the current chapter
    chapter_tasks = create_chapter_tasks(chapter_number, outline_context, context_window_size, genre_config)

    # Create a Crew and assign the tasks
    chapter_crew = Crew(
        agents=[writer, editor, researcher, critic, reviser],
        tasks=chapter_tasks,
        verbose=True,
        process=Process.sequential
    )
    logger.info(f"Crew created for Chapter {chapter_number}")

    # Run the Crew to generate the chapter
    try:
        chapter_crew.kickoff()
        logger.info(f"Chapter {chapter_number} generation complete.")

        # Access the output of the write_task directly from chapter_tasks
        write_task = chapter_tasks[1]  # write_task is the second task in the list
        if write_task.output:
            print(f"Debug: write_task.output: {write_task.output}")  # ADDED DEBUG PRINT
            # chapter_content = write_task.output.result # OLD INCORRECT LINE
            chapter_content = write_task.output # NEW CORRECT LINE - ASSUMING output_value is directly accessible
            chapter_outputs.append(chapter_content)  # Store the output
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