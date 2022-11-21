from game import Game
from input import text_input


class Orchestrator:
    def __init__(self):
        self.player_prompt = None
        self.environment_prompt = None

    def on_player_prompt(self, player_prompt):
        self.player_prompt = player_prompt
        text_input(self.on_environment_prompt)

    def on_environment_prompt(self, environment_prompt):
        self.environment_prompt = environment_prompt
        app = Game(
            player_prompt=self.player_prompt,
            background_prompt=self.environment_prompt,
        )
        app.on_execute()

    def run(self):
        text_input(self.on_player_prompt)


if __name__ == "__main__":
    orchestrator = Orchestrator()
    orchestrator.run()
