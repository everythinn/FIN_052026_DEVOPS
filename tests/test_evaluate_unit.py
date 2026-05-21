from src.services.feature_evaluator import evaluate_feature_access

# Pas de TestClient, pas de serveur, pas d'HTTP !

FEATURE = {"key": "new-dashboard", "enabled": True}
USER = {"id": 1}


def test_feature_disabled_globally():
    feature = {"key": "new-dashboard", "enabled": False}
    result = evaluate_feature_access(feature, {}, USER, [])
    assert result["enabled"] is False
    assert result["reason"] == "feature is disabled globally"


def test_no_env_config():
    result = evaluate_feature_access(FEATURE, None, USER, [])
    assert result["enabled"] is False
    assert result["reason"] == "no config for this environment"


def test_feature_disabled_in_env():
    config = {"enabled": False, "rollout": 0, "allowedUsers": [], "allowedGroups": []}
    result = evaluate_feature_access(FEATURE, config, USER, [])
    assert result["enabled"] is False
    assert result["reason"] == "feature is disabled in this environment"


def test_user_explicitly_allowed():
    config = {"enabled": True, "rollout": 0, "allowedUsers": [1], "allowedGroups": []}
    result = evaluate_feature_access(FEATURE, config, USER, [])
    assert result["enabled"] is True
    assert result["reason"] == "user explicitly allowed"


def test_user_in_allowed_group():
    config = {"enabled": True, "rollout": 0, "allowedUsers": [], "allowedGroups": ["beta-testers"]}
    result = evaluate_feature_access(FEATURE, config, USER, ["beta-testers"])
    assert result["enabled"] is True
    assert result["reason"] == "user belongs to allowed group beta-testers"


def test_user_in_rollout():
    config = {"enabled": True, "rollout": 100, "allowedUsers": [], "allowedGroups": []}
    result = evaluate_feature_access(FEATURE, config, USER, [])
    assert result["enabled"] is True
    assert result["reason"] == "user included in rollout"


def test_user_not_in_rollout():
    config = {"enabled": True, "rollout": 0, "allowedUsers": [], "allowedGroups": []}
    result = evaluate_feature_access(FEATURE, config, USER, [])
    assert result["enabled"] is False
    assert result["reason"] == "user not included"


def test_rollout_is_stable():
    config = {"enabled": True, "rollout": 50, "allowedUsers": [], "allowedGroups": []}
    result1 = evaluate_feature_access(FEATURE, config, USER, [])
    result2 = evaluate_feature_access(FEATURE, config, USER, [])
    result3 = evaluate_feature_access(FEATURE, config, USER, [])
    assert result1["enabled"] == result2["enabled"] == result3["enabled"]