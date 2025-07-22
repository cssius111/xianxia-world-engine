from xwe.core.achievement_system import AchievementSystem


def test_invalid_achievement_id():
    system = AchievementSystem()
    assert not system.check_achievement('nonexistent')


def test_claim_before_completion():
    system = AchievementSystem()
    assert system.claim_achievement_rewards('first_battle') is None


def test_complete_and_claim():
    system = AchievementSystem()
    assert system.check_achievement('first_battle')
    # Already completed, should return False
    assert not system.check_achievement('first_battle')
    rewards = system.claim_achievement_rewards('first_battle')
    assert rewards == {'exp': 100, 'gold': 50}
    # Duplicate claim should return None
    assert system.claim_achievement_rewards('first_battle') is None


def test_hidden_achievement_visibility():
    system = AchievementSystem()
    normal_list = [a['id'] for a in system.get_achievement_list()]
    assert 'win_streak_10' not in normal_list
    all_list = [a['id'] for a in system.get_achievement_list(show_hidden=True)]
    assert 'win_streak_10' in all_list


def test_unique_requirement_and_stats():
    system = AchievementSystem()
    # Requirement not met
    assert not system.check_achievement('explorer_5', value=3)
    assert not system.player_progress['explorer_5'].completed
    # Complete achievement
    assert system.check_achievement('explorer_5', value=5)
    rewards = system.claim_achievement_rewards('explorer_5')
    assert rewards == {'item': 'explorer_map'}
    # Total points should include both first_battle and explorer_5 after completion
    system.check_achievement('first_battle')
    system.claim_achievement_rewards('first_battle')
    assert system.get_total_points() == 25
    stats = system.get_completion_stats()
    assert stats['completed'] >= 2
    assert stats['total_points'] == system.get_total_points()
