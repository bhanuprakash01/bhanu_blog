from app.services.relevance_filter import RelevanceFilter


def test_positive_ai_content():
    rf = RelevanceFilter()
    title = "DeepMind introduces new reinforcement learning agent for robotics control"
    summary = "The new algorithm significantly speeds up complex humanoid locomotion."
    is_rel, reason, score = rf.is_relevant(title, summary)
    assert is_rel is True
    assert score > 0
    assert "Passed keyword criteria" in reason


def test_negative_discard():
    rf = RelevanceFilter()
    title = "Best gardening shears for springtime flower beds"
    summary = "We tested 12 different steel pruners to see which cuts best without rusting."
    is_rel, reason, score = rf.is_relevant(title, summary)
    assert is_rel is False
    assert "No recognized AI keywords found" in reason


def test_obvious_off_topic_exclusion():
    rf = RelevanceFilter()
    title = "Celebrity gossip: Red carpet fashion recap"
    summary = "Hollywood stars gather for movie awards celebration in Los Angeles."
    is_rel, reason, score = rf.is_relevant(title, summary)
    assert is_rel is False
