from genventure.game import Game
from genventure.input import text_input
from genventure.world import World


class Orchestrator:
    def __init__(self):
        self.world = None

    def on_player_prompt(self, player_prompt):
        app = Game(
            player_prompt=player_prompt,
            world=self.world,
        )
        app.on_execute()

    def on_environment_prompt(self, noun):
        self.world = World(noun=noun, tile_shape=(1024, 1024))
        text_input(self.on_player_prompt, "What are you?")

    def run(self):
        text_input(self.on_environment_prompt, "Where are you?")


if __name__ == "__main__":
    orchestrator = Orchestrator()
    orchestrator.run()
