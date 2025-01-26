import pytest
import os
import shutil  # Import the shutil module
import importlib
from crewai import Task, Crew, Process
from agents import create_agents
from unittest.mock import patch, MagicMock

# Mock configuration for testing
MOCK_MODEL = "ollama/llama3.2:latest"
MOCK_NUM_CHAPTERS = 3
MOCK_OUTLINE_CONTEXT = "Test outline context."
MOCK_GENRE_CONFIG = {
    'GENRE': 'test_genre',
    'PACING_SPEED_CHAPTER_START': 'slow',
    'PACING_SPEED_CHAPTER_MID': 'medium',
    'PACING_SPEED_CHAPTER_END': 'fast',
    'NARRATIVE_STYLE': 'test_style',
    'SETTING_INTEGRATION': 'test_integration',
    'CHARACTER_DEPTH': 'deep',
    'CHARACTER_RELATIONSHIP_DEPTH': 'deep',
    'PLOT_COMPLEXITY': 'complex',
    'MIN_WORDS_PER_CHAPTER': 100,  # Reduced for testing
    'MAX_WORDS_PER_CHAPTER': 200,  # Reduced for testing
    'PROSE_COMPLEXITY': 'high',
    'STORY_PLANNING_DESCRIPTION': 'Test story planning',
    'SETTING_BUILDING_DESCRIPTION': 'Test setting building',
    'CHARACTER_DEVELOPMENT_DESCRIPTION': 'Test character development',
    'RELATIONSHIP_ARCHITECTURE_DESCRIPTION': 'Test relationship architecture',
}
OUTPUT_FOLDER = "book-output"
DUMMY_OUTLINE_FILE = "dummy_outline.txt"

def test_chapter_generation():
    # Create dummy outline file
    dummy_outline_path = os.path.join(OUTPUT_FOLDER, DUMMY_OUTLINE_FILE)
    with open(dummy_outline_path, "w") as f:
        f.write("""
STORY ARC PLAN:
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
SETTING DETAILS:
[LOCATION NAME - Chapter Number(s)]:
- Physical Description: [detailed description including sensory details]
- Atmosphere and Mood: [mood, time of day, lighting, weather, etc.]
- Key Features: [important objects, layout elements, points of interest]
- Thematic Resonance: [how this setting enhances story themes and character emotions]
[RECURRING SETTINGS - Locations Appearing Multiple Times]:
- [LOCATION NAME]: [Description of how this setting evolves across chapters, noting changes and recurring elements]
[SETTING TRANSITIONS - Connections Between Locations]:
- [LOCATION 1] to [LOCATION 2]: [Describe how characters move between these settings and any significant spatial relationships or transitions]
CHARACTER PROFILES:
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
Chapter 1: The First Chapter Title
Title: The First Chapter
Key Events:
- [Event 1]
- [Event 2]
- [Event 3]
Character Developments: [Specific character moments and changes in this chapter]
Setting: [Specific location and atmosphere for this chapter]
Tone: [Specific emotional and narrative tone for this chapter]
Chapter 2: The Second Chapter Title
Title: The Second Chapter
Key Events:
- [Event 1]
- [Event 2]
- [Event 3]
Character Developments: [Specific character moments and changes in this chapter]
Setting: [Specific location and atmosphere for this chapter]
Tone: [Specific emotional and narrative tone for this chapter]
Chapter 3: The Third Chapter Title
Title: The Third Chapter
Key Events:
- [Event 1]
- [Event 2]
- [Event 3]
Character Developments: [Specific character moments and changes in this chapter]
Setting: [Specific location and atmosphere for this chapter]
Tone: [Specific emotional and narrative tone for this chapter]
        """)  # Add some content to the file

    # Load the genre configuration
    from main import load_genre_config
    genre_config = load_genre_config("literary_fiction")

    # Create agents
    agents = create_agents(MOCK_MODEL, MOCK_NUM_CHAPTERS, "", MOCK_GENRE_CONFIG)
    _, _, _, _, _, _, writer, editor, _, researcher, critic, reviser, _ = agents

    # Mock create_chapter_tasks (we'll define dummy tasks instead)
    research_task = Task(
        description="Dummy research task",
        expected_output="Dummy research output",
        agent=researcher
    )

    write_task = Task(
        description="Dummy write task",
        expected_output="Dummy chapter content",
        agent=writer,
        context=[research_task]  # Add the research_task as context
    )
    
    critic_task = Task(
        description="Dummy critic task",
        expected_output="Dummy criticism",
        agent=critic,
        context=[write_task]  # Assuming critic needs the write_task output
    )

    revise_task = Task(
        description="Dummy revise task",
        expected_output="Dummy revision",
        agent=reviser,
        context=[write_task, critic_task]  # Assuming reviser needs both write_task and critic_task output
    )

    edit_task = Task(
        description="Dummy edit task",
        expected_output="Dummy edited content",
        agent=editor,
        context=[write_task]  # Assuming editor needs the write_task output
    )

    # Create a Crew and assign the tasks
    chapter_crew = Crew(
        agents=[writer, editor, researcher, critic, reviser],
        tasks=[research_task, write_task, critic_task, revise_task, edit_task],
        verbose=True,
        process=Process.sequential
    )

    # Run the Crew to generate the chapter
    result = chapter_crew.kickoff()

    # Assert that the output file was created
    output_file = os.path.join(OUTPUT_FOLDER, "beach_story_chapter_1.html")
    assert os.path.exists(output_file)
    assert os.path.getsize(output_file) > 0  # Ensure the file is not empty

    # Clean up the dummy outline file
    os.remove(dummy_outline_path)

    # Clean up the output file
    os.remove(output_file)
