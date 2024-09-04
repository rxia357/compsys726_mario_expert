"""
This the primary class for the Mario Expert agent. It contains the logic for the Mario Expert agent to play the game and choose actions.

Your goal is to implement the functions and methods required to enable choose_action to select the best action for the agent to take.

Original Mario Manual: https://www.thegameisafootarcade.com/wp-content/uploads/2017/04/Super-Mario-Land-Game-Manual.pdf
"""

import json
import logging
import random

import cv2
import numpy as np
from mario_environment import MarioEnvironment
from pyboy.utils import WindowEvent


class MarioController(MarioEnvironment):
    """
    The MarioController class represents a controller for the Mario game environment.

    You can build upon this class all you want to implement your Mario Expert agent.

    Args:
        act_freq (int): The frequency at which actions are performed. Defaults to 10.
        emulation_speed (int): The speed of the game emulation. Defaults to 0.
        headless (bool): Whether to run the game in headless mode. Defaults to False.
    """

    def __init__(
        self,
        act_freq: int = 5,
        emulation_speed: int = 1,
        headless: bool = False,
    ) -> None:
        super().__init__(
            act_freq=act_freq,
            emulation_speed=emulation_speed,
            headless=headless,
        )

        self.act_freq = act_freq

        # Example of valid actions based purely on the buttons you can press
        valid_actions: list[WindowEvent] = [
            WindowEvent.PRESS_ARROW_DOWN,
            WindowEvent.PRESS_ARROW_LEFT,
            WindowEvent.PRESS_ARROW_RIGHT,
            WindowEvent.PRESS_ARROW_UP,
            WindowEvent.PRESS_BUTTON_A,
            WindowEvent.PRESS_BUTTON_B,
        ]

        release_button: list[WindowEvent] = [
            WindowEvent.RELEASE_ARROW_DOWN,
            WindowEvent.RELEASE_ARROW_LEFT,
            WindowEvent.RELEASE_ARROW_RIGHT,
            WindowEvent.RELEASE_ARROW_UP,
            WindowEvent.RELEASE_BUTTON_A,
            WindowEvent.RELEASE_BUTTON_B,
        ]

        self.valid_actions = valid_actions
        self.release_button = release_button

    def run_action(self, actions: list, delays: list) -> None:
        """
        This is a very basic example of how this function could be implemented

        As part of this assignment your job is to modify this function to better suit your needs

        You can change the action type to whatever you want or need just remember the base control of the game is pushing buttons
        """
        self.act_freq = max(delays)
        if self.act_freq == 0:
            self.act_freq = 5
            
        for i, action in enumerate(actions):
            self.pyboy.send_input(self.valid_actions[action])
            self.valid_action = delays[i]
            if self.act_freq == 0:
                self.act_freq = 5

            for _ in range(self.act_freq):
                self.pyboy.tick()

        for i, action in enumerate(actions):
            self.pyboy.send_input(self.release_button[action])

class MarioExpert:
    """
    The MarioExpert class represents an expert agent for playing the Mario game.

    Edit this class to implement the logic for the Mario Expert agent to play the game.

    Do NOT edit the input parameters for the __init__ method.

    Args:
        results_path (str): The path to save the results and video of the gameplay.
        headless (bool, optional): Whether to run the game in headless mode. Defaults to False.
    """

    def __init__(self, results_path: str, headless=True):
        self.results_path = results_path

        self.environment = MarioController(headless=headless)

        self.video = None

    def choose_action(self):
        state = self.environment.game_state()
        frame = self.environment.grab_frame()
        game_area = self.environment.game_area()
        
        # print(state)
        # print(frame)
        print(game_area)

        # Implement your code here to choose the best action
        # time.sleep(0.1)
        # return random.randint(0, len(self.environment.valid_actions) - 1)
        
        DOWN = 0
        LEFT = 1 # walk left
        RIGHT = 2 # walk right
        UP = 3
        A = 4 # jump
        B = 5
        
        # Initilisation
        mario = [0,0]
        delay = 0
        
        # Find mario's location
        mario_positions = np.argwhere(game_area == 1)
        mario = mario_positions[0]
        
        if len(mario) == 0:
            return 0, 0
        
        # if len(mario_positions) == 0:
        #     output = DOWN
        
        # go back a bit so it dosesn't collide on the monster when jumping over a pipe
        if game_area[mario[0]+1][mario[1]+2] == 14 and game_area[mario[0]+1][mario[1]+7] == 15:
            output = [LEFT]
            delay = [10]
        # Check if there's monster right on top of mario, then run to left
        elif 15 in game_area[:mario[0] - 1, mario[1]+1]:
            output = [LEFT]
            delay = [60] # increase delay
        # if there is something in front of mario, then jump
        elif game_area[mario[0]+1][mario[1]+ 2] != 0:
            output = [A]
            delay = [15]
        # Check if there is POT HOLE in front of mario, the gap is less than 3 pixels (1-2 pixels wide)
        elif game_area[mario[0]+2][mario[1]+1] == 10 and game_area[15][mario[1]+2] == 0 and game_area[15][mario[1]+4] != 0:
            output = [A]
            delay = [20]
        # huge POT HOLE, at least 3 pixels wide accelerate first
        elif game_area[mario[0]+2][mario[1]+1] == 10 and game_area[15][mario[1]+7] == 0 and game_area[15][mario[1]+9] == 0:
            output = [RIGHT]
            delay = [30]
        # elif game_area[mario[0]+2][mario[1]+1] == 10 and game_area[15][mario[1]+2] == 0 and game_area[15][mario[1]+4] == 0:
        #     output = [A,RIGHT]
        #     delay = [30]
        # check for large monsters, and move back
        elif game_area[mario[0]-1][mario[1]+3] == 18:
            output = [LEFT]
            delay = [40]
        # normally run right
        else:
            output = [RIGHT]
            delay = [0]
            
        return output, delay


    def step(self):
        """
        Modify this function as required to implement the Mario Expert agent's logic.

        This is just a very basic example
        """

        # Choose an action - button press or other...
        actions, delays = self.choose_action()

        # Run the action on the environment
        self.environment.run_action(actions, delays)

    def play(self):
        """
        Do NOT edit this method.
        """
        self.environment.reset()

        frame = self.environment.grab_frame()
        height, width, _ = frame.shape

        self.start_video(f"{self.results_path}/mario_expert.mp4", width, height)

        while not self.environment.get_game_over():
            frame = self.environment.grab_frame()
            self.video.write(frame)

            self.step()

        final_stats = self.environment.game_state()
        logging.info(f"Final Stats: {final_stats}")

        with open(f"{self.results_path}/results.json", "w", encoding="utf-8") as file:
            json.dump(final_stats, file)

        self.stop_video()

    def start_video(self, video_name, width, height, fps=30):
        """
        Do NOT edit this method.
        """
        self.video = cv2.VideoWriter(
            video_name, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height)
        )

    def stop_video(self) -> None:
        """
        Do NOT edit this method.
        """
        self.video.release()
