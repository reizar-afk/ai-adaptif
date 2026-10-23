import json, os

class UserMemory:
    def __init__(self, path="data/user_profiles.json"):
        self.path = path
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path, encoding="utf-8") as f:
                self.profiles = json.load(f)
        else:
            self.profiles = {}

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.profiles, f, ensure_ascii=False, indent=2)

    def get(self, user_id):
        return self.profiles.get(user_id, {
            "preferred_lang": "id",
            "technical_level": "medium",
            "style": "jelas dan ringkas"
        })

    def update(self, user_id, key, value):
        self.profiles.setdefault(user_id, {})
        self.profiles[user_id][key] = value
        self.save()

    def build_system_prompt(self, user_id):
        p = self.get(user_id)
        return (
            f"Jawab dalam bahasa {p['preferred_lang']}. "
            f"Level teknis user: {p['technical_level']}. "
            f"Gaya jawaban yang disukai: {p['style']}."
        )
