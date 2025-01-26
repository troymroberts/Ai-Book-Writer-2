import pytest
import logging
from crewai import Agent
from agents import create_agents
from unittest.mock import patch

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
    'MIN_WORDS_PER_CHAPTER': 100,
    'MAX_WORDS_PER_CHAPTER': 200,
    'PROSE_COMPLEXITY': 'high',
    'STORY_PLANNING_DESCRIPTION': 'Test story planning',
    'SETTING_BUILDING_DESCRIPTION': 'Test setting building',
    'CHARACTER_DEVELOPMENT_DESCRIPTION': 'Test character development',
    'RELATIONSHIP_ARCHITECTURE_DESCRIPTION': 'Test relationship architecture',
}

# Test individual agent creation and logging
@pytest.mark.parametrize("agent_name, expected_log_message", [
    ("StoryPlanner", "Story Planner agent created."),
    ("OutlineCreator", "Outline Creator agent created."),
    ("SettingBuilder", "Setting Builder agent created."),
    ("CharacterCreator", "Character Creator agent created."),
    ("RelationshipArchitect", "Relationship Architect agent created."),
    ("PlotAgent", "Plot Agent agent created."),
    ("Writer", "Writer agent created."),
    ("Editor", "Editor agent created."),
    ("MemoryKeeper", "Memory Keeper agent created."),
    ("Researcher", "Researcher agent created."),
    ("Critic", "Critic agent created."),
    ("Reviser", "Reviser agent created."),
    ("OutlineCompiler", "Outline Compiler agent created."),
])

def test_agent_creation_and_logging(agent_name, expected_log_message):
    with patch('logging.Logger.info') as mock_info:
        agents = create_agents(MOCK_MODEL, MOCK_NUM_CHAPTERS, MOCK_OUTLINE_CONTEXT, MOCK_GENRE_CONFIG)
        
        # Find the agent by role
        agent = next((a for a in agents if a.role.replace(" ", "") == agent_name), None)
        
        assert agent is not None, f"Agent {agent_name} not found in the created agents"
        
        # Check if the info method was called with the correct message
        if any(expected_log_message in str(call_args) for call_args in mock_info.call_args_list):
            print(f"Log message for {agent_name} found.")
        else:
            print(f"Log message for {agent_name} not found in calls:")
            for call_args in mock_info.call_args_list:
                print(f"  - {call_args}")
            pytest.fail(f"Expected log message for {agent_name} was not found.")
