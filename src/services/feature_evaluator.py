import hashlib


def evaluate_feature_access(feature, config, user, user_groups):
    """
    Évalue si un utilisateur a accès à une feature.
    Fonction pure - aucune dépendance HTTP ou storage.

    Args:
        feature: dict avec au moins "key" et "enabled"
        config: dict avec "enabled", "rollout", "allowedUsers", "allowedGroups"
        user: dict avec "id"
        user_groups: list de noms de groupes auxquels appartient l'utilisateur

    Returns:
        dict avec "enabled" (bool) et "reason" (str)
    """

    # 1. Feature activée globalement ?
    if not feature.get("enabled", False):
        return {"enabled": False, "reason": "feature is disabled globally"}

    # 2. Config pour cet environnement existe ?
    if config is None:
        return {"enabled": False, "reason": "no config for this environment"}

    # 3. Feature activée dans l'environnement ?
    if not config.get("enabled", False):
        return {"enabled": False, "reason": "feature is disabled in this environment"}

    # 4. Utilisateur explicitement autorisé ?
    allowed_users = config.get("allowedUsers", [])
    if user["id"] in allowed_users:
        return {"enabled": True, "reason": "user explicitly allowed"}

    # 5. Utilisateur dans un groupe autorisé ?
    allowed_groups = config.get("allowedGroups", [])
    for group in user_groups:
        if group in allowed_groups:
            return {"enabled": True, "reason": f"user belongs to allowed group {group}"}

    # 6. Rollout progressif ?
    rollout = config.get("rollout", 0)
    if rollout > 0:
        hash_input = f"{user['id']}{feature['key']}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16) % 100
        if hash_value < rollout:
            return {"enabled": True, "reason": "user included in rollout"}

    return {"enabled": False, "reason": "user not included"}
