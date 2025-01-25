# agents.py
from crewai import Agent

def create_agents(model_to_use, num_chapters, outline_context, genre_config):
    """
    Creates and returns a list of agent instances for the book writing project.

    Args:
        model_to_use (str): The model identifier to be used by the agents.
        num_chapters (int): The number of chapters in the story.
        outline_context (str): The context of the book outline.
        genre_config (dict): Configuration parameters for the selected genre.

    Returns:
        list: A list of Agent instances.
    """

    # Story Planner: Focuses on high-level story structure
    story_planner = Agent(
        role='Story Planner',
        goal=f"""
        Refine the high-level story arc for a {num_chapters}-chapter story, ensuring effective pacing and a compelling structure.
        Identify major plot points, character arcs, and turning points across the entire narrative.
        Consider the outline: {outline_context}
        Incorporate the genre-specific pacing: {genre_config.get('PACING_SPEED_CHAPTER_START')}, {genre_config.get('PACING_SPEED_CHAPTER_MID')}, {genre_config.get('PACING_SPEED_CHAPTER_END')}.
        """,
        backstory=f"""
        You are an expert story arc planner focused on overall narrative structure and pacing.
        You are responsible for ensuring effective pacing across the book, identifying major plot points, and mapping character arcs.
        You are working on a {num_chapters}-chapter story in the {genre_config.get('GENRE')} genre.
        """,
        verbose=True,
        llm=model_to_use
    )

    # Outline Creator: Creates detailed chapter outlines
    outline_creator = Agent(
        role='Outline Creator',
        goal=f"""
        Generate detailed chapter outlines based on the story arc plan for a {num_chapters}-chapter story.
        Include specific chapter titles, key events, character developments, setting, and tone for each chapter.
        ONLY CREATE THE OUTLINE FOR ONE CHAPTER AT A TIME
        Consider the outline: {outline_context}
        Incorporate the genre-specific narrative style: {genre_config.get('NARRATIVE_STYLE')}.
        """,
        backstory=f"""
        You are an expert outline creator who generates detailed chapter outlines based on story premises and story arc plans.
        Your outlines must follow a strict format, including Chapter Title, Key Events, Character Developments, Setting, and Tone for each chapter.
        You are creating an outline for a {num_chapters}-chapter story in the {genre_config.get('GENRE')} genre.
        You create outlines for ONE CHAPTER AT A TIME.
        """,
        verbose=True,
        llm=model_to_use
    )

    # Setting Builder: Creates and maintains the story setting
    setting_builder = Agent(
        role='Setting Builder',
        goal=f"""
        Establish and maintain all settings and world elements needed for the {num_chapters}-chapter story, ensuring they are rich, consistent, and dynamically integrated as the story progresses.
        Consider the outline: {outline_context}
        Incorporate the genre-specific setting integration: {genre_config.get('SETTING_INTEGRATION')}.
        """,
        backstory=f"""
        You are an expert in setting and world-building, responsible for creating rich, consistent, and evolving settings that enhance the story.
        You establish all settings and world elements needed for the entire story and ensure they are dynamically integrated as the story progresses.
        You are working on a {num_chapters}-chapter story in the {genre_config.get('GENRE')} genre.
        """,
        verbose=True,
        llm=model_to_use
    )

    # Character Agent: Develops and maintains character details
    character_agent = Agent(
        role='Character Creator',
        goal=f"""
        Develop and maintain consistent, engaging, and evolving characters throughout the {num_chapters}-chapter book.
        Provide full names (first and last), ages, detailed backstories, motivations, personalities, strengths, weaknesses, and relationships for each character.
        Assign character stats (e.g., Intelligence, Charisma, etc.) on a scale of 1-10 and define their speech patterns (e.g., accent, tone, verbosity).
        Ensure characters are diverse and well-rounded.
        Consider the outline: {outline_context}
        Incorporate the genre-specific character depth: {genre_config.get('CHARACTER_DEPTH')}.
        """,
        backstory=f"""
        You are the character development expert, responsible for creating and maintaining consistent, engaging, and evolving characters throughout the book.
        You define and track all key characters, ensuring depth, consistency, and compelling arcs. You provide full names, ages, detailed backstories, and rich descriptions.
        You also assign character stats and define speech patterns to guide the writer in creating realistic dialogue and interactions.
        You are working on a {num_chapters}-chapter story in the {genre_config.get('GENRE')} genre.
        """,
        verbose=True,
        llm=model_to_use
    )

    # Relationship Architect: Manages relationships and family structures
    relationship_architect = Agent(
        role='Relationship Architect',
        goal=f"""
        Develop and manage the relationships between characters, including family structures, friendships, rivalries, and romantic relationships.
        Ensure relationship dynamics are realistic, engaging, and contribute to the overall narrative.
        Provide detailed relationship backstories and evolution throughout the {num_chapters}-chapter story.
        Consider the outline: {outline_context}
        Incorporate the genre-specific relationship depth: {genre_config.get('CHARACTER_RELATIONSHIP_DEPTH')}.
        """,
        backstory=f"""
        You are the relationship expert, responsible for creating and maintaining realistic and engaging relationships between characters.
        You define family structures, friendships, rivalries, and romantic relationships, providing detailed backstories and evolution.
        You are working on a {num_chapters}-chapter story in the {genre_config.get('GENRE')} genre.
        """,
        verbose=True,
        llm=model_to_use
    )

    # Plot Agent: Focuses on plot details and pacing within chapters
    plot_agent = Agent(
        role='Plot Agent',
        goal=f"""
        Refine chapter outlines to maximize plot effectiveness and pacing at the chapter level for a {num_chapters}-chapter story, ensuring each chapter's plot is engaging, well-paced, and contributes to the overall story arc.
        Consider the outline: {outline_context}
        Incorporate the genre-specific plot complexity: {genre_config.get('PLOT_COMPLEXITY')}.
        """,
        backstory=f"""
        You are the plot detail expert, responsible for ensuring each chapter's plot is engaging, well-paced, and contributes to the overall story arc.
        You refine chapter outlines to maximize plot effectiveness and pacing at the chapter level.
        You are working on a {num_chapters}-chapter story in the {genre_config.get('GENRE')} genre.
        """,
        verbose=True,
        llm=model_to_use
    )

    # Writer: Generates the actual prose for each chapter
    writer = Agent(
        role='Writer',
        goal=f"""
        Write individual chapters based on the provided outline for a {num_chapters}-chapter story, expanding on the key events, character developments, and setting descriptions with vivid prose and engaging dialogue.
        Pay close attention to the character profiles, including their stats and speech patterns, to create realistic and consistent dialogue and interactions.
        Adhere to the specified tone and style for each chapter, and follow the genre-specific instructions.
        Each chapter MUST be at least {genre_config.get('MIN_WORDS_PER_CHAPTER', 1600)} and no more than {genre_config.get('MAX_WORDS_PER_CHAPTER', 3000)} words in length. Consider this a HARD REQUIREMENT. If your output is shorter, continue writing until you reach this minimum length.
        ONLY WRITE ONE CHAPTER AT A TIME.
        Consider the outline: {outline_context}
        """,
        backstory=f"""
        You are an expert creative writer who brings scenes to life with vivid prose, compelling characters, and engaging plots.
        You write according to the detailed chapter outline, incorporating all Key Events, Character Developments, Setting, and Tone, while maintaining consistent character voices and personalities.
        You use the character stats and speech patterns defined by the Character Agent to guide your writing.
        You are working on a {num_chapters}-chapter story in the {genre_config.get('GENRE')} genre, ONE CHAPTER AT A TIME, with each chapter being at least {genre_config.get('MIN_WORDS_PER_CHAPTER', 1600)} and no more than {genre_config.get('MAX_WORDS_PER_CHAPTER', 3000)} words long.
        You are committed to meeting the word count for each chapter and will not stop writing until this requirement is met.
        """,
        verbose=True,
        llm=model_to_use
    )

    # Editor: Reviews and improves content
    editor = Agent(
        role='Editor',
        goal=f"""
        Review and refine each chapter, providing feedback to the writer if necessary for a {num_chapters}-chapter story.
        Ensure each chapter is well-written, consistent with the outline, and free of errors.
        Verify that each chapter meets the minimum length requirement of between {genre_config.get('MIN_WORDS_PER_CHAPTER', 1600)} and {genre_config.get('MAX_WORDS_PER_CHAPTER', 3000)} words. If a chapter is too short, provide specific feedback to the Writer on what areas need expansion.
        ONLY WORK ON ONE CHAPTER AT A TIME.
        Consider the outline: {outline_context}
        Incorporate the genre-specific editing style: {genre_config.get('PROSE_COMPLEXITY')}.
        """,
        backstory=f"""
        You are an expert editor ensuring quality, consistency, and adherence to the book outline and style guidelines.
        You check for strict alignment with the chapter outline, verify character and world-building consistency, and critically review and improve prose quality.
        You also ensure that each chapter meets the length requirement of between {genre_config.get('MIN_WORDS_PER_CHAPTER', 1600)} and {genre_config.get('MAX_WORDS_PER_CHAPTER', 3000)} words.
        You are working on a {num_chapters}-chapter story in the {genre_config.get('GENRE')} genre, ONE CHAPTER AT A TIME.
        """,
        verbose=True,
        llm=model_to_use
    )

    # Memory Keeper: Maintains story continuity and context
    memory_keeper = Agent(
        role='Memory Keeper',
        goal=f"""
        Track and summarize each chapter's key events, character developments, and world details for a {num_chapters}-chapter story.
        Monitor character development and relationships for consistency, maintain world-building consistency, and flag any continuity issues.
        Consider the outline: {outline_context}
        """,
        backstory=f"""
        You are the keeper of the story's continuity and context.
        You track and summarize each chapter's key events, character developments, and world details, monitor character development and relationships for consistency, maintain world-building consistency, and flag any continuity issues.
        You are working on a {num_chapters}-chapter story.
        """,
        verbose=True,
        llm=model_to_use
    )

    # Researcher: Conducts research to provide supporting details
    researcher = Agent(
        role='Researcher',
        goal=f"""
        Research specific information, gather relevant data, and provide accurate details to support the {num_chapters}-chapter story, such as historical context, cultural details, or technical information.
        Consider the outline: {outline_context}
        """,
        backstory=f"""
        You are a thorough researcher, adept at finding and verifying information from reliable sources.
        You research specific details needed for the story, such as information about beach activities, marine life, or coastal weather patterns.
        You are working on a {num_chapters}-chapter story.
        """,
        verbose=True,
        llm=model_to_use
    )

    # Critic: Provides constructive criticism of each chapter
    critic = Agent(
        role='Critic',
        goal=f"""
        Provide constructive criticism of each chapter, identifying plot holes, inconsistencies, and areas for improvement in terms of narrative structure, character development, and pacing for a {num_chapters}-chapter story.
        Consider the outline: {outline_context}
        """,
        backstory=f"""
        You are a discerning critic, able to analyze stories and offer insightful feedback for enhancement.
        You provide a critical review of each chapter, identifying any plot holes, inconsistencies, or areas that need improvement.
        You are working on a {num_chapters}-chapter story.
        """,
        verbose=True,
        llm=model_to_use
    )

    # Reviser: Revises each chapter based on feedback
    reviser = Agent(
        role='Reviser',
        goal=f"""
        Revise each chapter based on feedback from the Critic and Editor, ensuring the chapter is coherent, consistent, and polished for a {num_chapters}-chapter story.
        Incorporate revisions to improve the story's quality and readability.
        Consider the outline: {outline_context}
        """,
        backstory=f"""
        You are a skilled reviser, capable of incorporating feedback and polishing each chapter to perfection.
        You revise the story based on feedback, ensuring the story is coherent, consistent, and polished.
        You are working on a {num_chapters}-chapter story.
        """,
        verbose=True,
        llm=model_to_use
    )

    # Outline Compiler: Compiles the final outline
    outline_compiler = Agent(
        role='Outline Compiler',
        goal=f"""
        Compile the complete book outline, integrating the overall story arc plan, setting details, character profiles, relationship dynamics, and individual chapter outlines into a single, cohesive document.
        Ensure the outline is well-structured, detailed, and follows the specified format.
        Output the ENTIRE outline, including all sections.
        """,
        backstory="""
        You are an expert outline compiler, responsible for assembling the final book outline from the contributions of other agents.
        You ensure the outline is comprehensive, well-organized, and ready for use by the writing team.
        """,
        verbose=True,
        llm=model_to_use
    )

    return [story_planner, outline_creator, setting_builder, character_agent, relationship_architect, plot_agent, writer, editor, memory_keeper, researcher, critic, reviser, outline_compiler]
