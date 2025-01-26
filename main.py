import os
import shutil
import importlib
<<<<<<< HEAD
import re
from crewai import Task, Crew, Process, Agent
=======
from crewai import Task, Crew, Process
>>>>>>> parent of b953067 (update)
from dotenv import load_dotenv
from agents import create_agents
import time
from litellm import Timeout, completion
import logging

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

# Define the model to be used by the agents
model_to_use = f"ollama/{os.getenv('OLLAMA_MODEL')}"

<<<<<<< HEAD
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
=======
# Specify the genre from the .env file
GENRE = os.getenv('GENRE', 'literary_fiction')  # Default to 'literary_fiction' if not specified
>>>>>>> parent of b953067 (update)

# Function to load configuration from the selected genre
def load_genre_config(genre):
    try:
        genre_module = importlib.import_module(f"genres.{genre}")
<<<<<<< HEAD
        return {
            k: v for k, v in genre_module.__dict__.items()
            if not k.startswith("_") and k.isupper()
        }
=======
        config = {k: v for k, v in genre_module.__dict__.items() if not k.startswith("_")}
        config['GENRE'] = genre  # Add the genre name to the config
        return config
>>>>>>> parent of b953067 (update)
    except ModuleNotFoundError:
        print(f"Genre configuration for '{genre}' not found. Using default settings.")
        return {}

# Load the genre configuration
genre_config = load_genre_config(GENRE)

# Get the number of chapters from the genre config
num_chapters = genre_config.get('NUM_CHAPTERS', 3)

<<<<<<< HEAD
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
=======
# Create agents using the function from agents.py, passing num_chapters and an empty outline_context for now
agents = create_agents(model_to_use, num_chapters, "", genre_config)

# Assign agents to variables
story_planner, outline_creator, setting_builder, character_agent, relationship_architect, plot_agent, writer, editor, memory_keeper, researcher, critic, reviser, outline_compiler = agents

# Get the initial prompt from the .env file
initial_prompt = os.getenv('INITIAL_PROMPT', "A group of friends decides to spend a memorable day at the beach. Each friend has a different idea of what makes a perfect beach day, leading to a series of adventures and misadventures as they try to make the most of their time together.")
>>>>>>> parent of b953067 (update)

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

# Define the task for the Outline Creator agent
outline_creator_task = Task(
    description=f"""
    Create a detailed chapter outline for each of the {num_chapters} chapters individually, based on the following premise, the developed story arc plan, character profiles, relationship dynamics, and setting details:

    Initial Premise: {initial_prompt}

    Story Arc Plan: [Provided by the Story Planner agent]

    Character Profiles: [Provided by the Character Agent]

    Relationship Dynamics: [Provided by the Relationship Architect Agent]

    Setting Details: [Provided by the Setting Builder Agent]

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

    Repeat EXACTLY this format for all {num_chapters} chapters.

    Ensure that each chapter outline is comprehensive and detailed, providing a solid foundation for the writing process.
    """,
    expected_output=f"A detailed chapter outline for each of the {num_chapters} chapters.",
    agent=outline_creator,
    context=[story_planning_task, character_development_task, setting_building_task, relationship_architecture_task]
)

# Define the task for the Outline Compiler agent
outline_compiler_task = Task(
    description=f"""
    Compile the final outline for the {num_chapters}-chapter story, integrating all previously generated content:

    - Overall Story Arc Plan: [Provided by the Story Planner agent]
    - Setting Details: [Provided by the Setting Builder Agent]
    - Character Profiles: [Provided by the Character Agent]
    - Relationship Dynamics: [Provided by the Relationship Architect Agent]
    - Chapter Outlines: [Provided by the Outline Creator Agent]

    Format your response as:
    - STORY ARC PLAN: [Insert the Story Planner Agent's output here]
    - SETTING DETAILS: [Insert the Setting Builder Agent's output here]
    - CHARACTER PROFILES: [Insert the Character Agent's output here]
    - RELATIONSHIP DYNAMICS: [Insert the Relationship Architect Agent's output here]
    - CHAPTER OUTLINES: [Insert the Outline Creator Agent's output here]

    Combine all this information into a single, cohesive document. Ensure the outline is well-structured, detailed, and follows a logical sequence.
    """,
    expected_output=f"A comprehensive and well-structured outline for the {num_chapters}-chapter story, integrating all elements.",
    agent=outline_compiler,
    context=[story_planning_task, setting_building_task, character_development_task, relationship_architecture_task, outline_creator_task]
)

# Create a Crew and assign the task
outline_crew = Crew(
    agents=[story_planner, setting_builder, character_agent, relationship_architect, outline_creator, outline_compiler],
    tasks=[story_planning_task, setting_building_task, character_development_task, relationship_architecture_task, outline_creation_task, outline_compiler_task],
    verbose=True,
    process=Process.sequential
)

# Run the Crew to generate the outline
outline_result = outline_crew.kickoff()

# Create the book-output subfolder if it doesn't exist
output_folder = "book-output"
os.makedirs(output_folder, exist_ok=True)

# Save the outline to a file in the output folder
outline_file_path = os.path.join(output_folder, "outline.txt")
with open(outline_file_path, "w") as f:
    f.write(str(outline_result))

print(f"Outline written to {outline_file_path}")

# Extract the outline context from the outline_result
outline_context = str(outline_result)

# Update agent goals and backstories with the outline context
for agent in agents:
    agent.goal = agent.goal.replace("{outline_context}", outline_context)
    agent.backstory = agent.backstory.replace("{outline_context}", outline_context)

<<<<<<< HEAD
# Chapter generation functions
def create_chapter_tasks(chapter_number, outline_context, genre_config, agents, manager_llm_config):
=======
# Function to create tasks for each chapter
def create_chapter_tasks(chapter_number, outline_context, context_window_size, genre_config):
>>>>>>> parent of b953067 (update)
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
<<<<<<< HEAD
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
=======
        description=f"""Research any specific details needed for Chapter {chapter_number}, such as information about beach activities, marine life, or coastal weather patterns. Refer to the outline for context: {outline_context}""",
        expected_output=f"Accurate and relevant research findings to support Chapter {chapter_number}.",
        agent=researcher
    )

    write_task = Task(
        description=f"""Write Chapter {chapter_number} based on the outline in '{outline_file_path}'.
        Each chapter MUST be at least {min_words} words and no more than {max_words} words. Consider this a HARD REQUIREMENT. If your output is shorter, continue writing until you reach this minimum length.
        Focus on engaging the reader with descriptive language and compelling character interactions.
        Expand on the key events, character developments, and setting described in the outline for this chapter.
        Use paragraphs to separate different parts of the story and improve readability.
        Pay close attention to the character profiles, including their stats and speech patterns, to create realistic and consistent dialogue.
        ONLY WRITE CHAPTER {chapter_number}. DO NOT WRITE ANY OTHER CHAPTERS.
        Refer to the outline for context: {outline_context}

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
>>>>>>> parent of b953067 (update)
        agent=writer,
        context=[research_task, setting_description_task, dialogue_task, outline_creator_task],
        llm=manager_llm_config
    )
    
    critic_task = Task(
        description=f"""Provide a critical review of Chapter {chapter_number}, identifying any plot holes, inconsistencies, or areas that need improvement. Refer to the outline for context: {outline_context}""",
        expected_output=f"Constructive criticism and suggestions for enhancing Chapter {chapter_number}.",
        agent=critic,
<<<<<<< HEAD
        context=[write_task],
        llm=manager_llm_config
=======
        context=[outline_creator_task, write_task]
>>>>>>> parent of b953067 (update)
    )
    
    revise_task = Task(
        description=f"""Revise Chapter {chapter_number} based on feedback from the Critic and Editor. Ensure the chapter is coherent, consistent, and polished. Refer to the outline for context: {outline_context}""",
        expected_output=f"A revised version of Chapter {chapter_number} that incorporates feedback and improvements.",
        agent=reviser,
<<<<<<< HEAD
        context=[write_task, critic_task],
        llm=manager_llm_config
=======
        context=[outline_creator_task, write_task]
>>>>>>> parent of b953067 (update)
    )
    
    edit_task = Task(
        description=f"""Edit Chapter {chapter_number}, focusing on grammar, style, and overall flow. Incorporate changes directly into the chapter text. 
        Verify that the chapter meets the length requirement of between {min_words} and {max_words} words. If it's too short, provide specific feedback to the Writer on what areas need expansion.
        Refer to the outline for context: {outline_context}""",
        expected_output=f"The final, edited version of Chapter {chapter_number}, meeting the minimum word count requirement.",
        agent=editor,
<<<<<<< HEAD
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
=======
        context=[outline_creator_task, write_task]
    )
    
    return [research_task, write_task, critic_task, revise_task, edit_task]
>>>>>>> parent of b953067 (update)

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
            print(f"Failed to delete {file_path}. Reason: {e}")

# Clear the output folder before generating new content
clear_output_folder(output_folder)

# Get the context window size from the .env file
context_window_size = int(os.getenv('OLLAMA_CONTEXT_WINDOW', 4096))  # Default to 4096

# Loop through each chapter and create a crew to write it
for chapter_number in range(1, num_chapters + 1):
<<<<<<< HEAD
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
=======
    # Create tasks for the current chapter
    chapter_tasks = create_chapter_tasks(chapter_number, outline_context, context_window_size, genre_config)

    # Create a Crew and assign the tasks
    chapter_crew = Crew(
        agents=[writer, editor, researcher, critic, reviser],
        tasks=chapter_tasks,
        verbose=True,
        process=Process.sequential
    )

    # Run the Crew to generate the chapter
    chapter_crew.kickoff()
>>>>>>> parent of b953067 (update)

    # Access the output of the write_task directly
    chapter_content = write_task.output

    # Post-process the chapter content to add paragraph tags
    paragraphs = str(chapter_content).split("\n\n")
    formatted_paragraphs = [f"<p>{p.strip()}</p>" for p in paragraphs if p.strip()]
    formatted_text = "\n".join(formatted_paragraphs)

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

    print(f"Chapter {chapter_number} written to {output_file}")

print("######################")
print("Story generation complete.")
