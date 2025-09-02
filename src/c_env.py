

class Environment:
    def __init__(self, parent_env, env_name = ""):
        self.variable_mapping = {}
        
        self.type_definitions = []
        self.parent_env = parent_env
        self.depth = 0 if not self.parent_env else self.parent_env.depth + 1
        self.name = env_name if env_name else f"Environment{self.depth}"
        
        if self.parent_env:
            for (key, value) in self.parent_env.variable_mapping.items():
                self.insert_mapping(key[0], key[1], value)
        
        
    def insert_mapping(self, var_name, var_type, var_value):
        return self.variable_mapping.setdefault(var_name, (var_value, var_type, self.depth)) is not None
        
    def get_mapping(self, var_name):
        return self.variable_mapping.get(var_name, (None, None, None))
        
    def propagate_mapping(self, var_name, var_type, var_value):
        pass
        
    def __str__(self):
        return f"{str(self.parent_env) + "\n" if self.parent_env else ""}{'\t' * self.depth}{self.name} @ depth {self.depth}: {self.variable_mapping}"
    