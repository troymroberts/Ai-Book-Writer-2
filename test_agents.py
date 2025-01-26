# test_agents.py
import pytest
from agents import create_agents
from crewai import Agent

# Mock model and config for testing
MODEL_TO_USE = "mock_model"
NUM_CHAPTERS = 3
OUTLINE_CONTEXT = "This is a test outline."
GENRE_CONFIG = {
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

def test_create_agents_returns_list():
    agents = create_agents(MODEL_TO_USE, NUM_CHAPTERS, OUTLINE_CONTEXT, GENRE_CONFIG)
    assert isinstance(agents, list)

def test_create_agents_returns_correct_number_of_agents():
    agents = create_agents(MODEL_TO_USE, NUM_CHAPTERS, OUTLINE_CONTEXT, GENRE_CONFIG)
    assert len(agents) == 13  # Expected number of agents

def test_create_agents_returns_agent_instances():
    agents = create_agents(MODEL_TO_USE, NUM_CHAPTERS, OUTLINE_CONTEXT, GENRE_CONFIG)
    for agent in agents:
        assert isinstance(agent, Agent)

def test_story_planner_agent_has_correct_role():
    agents = create_agents(MODEL_TO_USE, NUM_CHAPTERS, OUTLINE_CONTEXT, GENRE_CONFIG)
    story_planner = agents[0]
    assert story_planner.role == 'Story Planner'

# Add more tests for other agents and their attributes...

def test_writer_agent_has_word_limit_in_goal():
    agents = create_agents(MODEL_TO_USE, NUM_CHAPTERS, OUTLINE_CONTEXT, GENRE_CONFIG)
    writer = agents[6]
    assert "Each chapter MUST be at least 100" in writer.goal
    assert "no more than 200 words" in writer.goal