"""Flappy bird game."""
import tkinter as tk
import random
import playsound
import threading


class Widgets:
    """Create the label and button and text if needed."""

    _RECT_HEIGHT = 100

    def __init__(self, window, canvas):
        """Create a label and start button all with textvariables."""
        self._window = window
        self._canvas = canvas

        self._score_var = tk.IntVar()
        self._start_b = tk.Button(self._window, text='Start', font='Courier 15', command=self._start)
        self._score_l = tk.Label(self._window, textvariable=self._score_var, font='Courier 30')
        self._score_var.set(0)

    def get_score(self):
        """Return the score stored in the score_var."""
        return self._score_var.get()

    def destroy_label(self):
        """Destroy the score label."""
        self._score_l.destroy()

    def score_label(self):
        """Show the label for scoring."""
        self._score_l.grid(row=0, column=0, sticky='NE')

    def start_button(self):
        """Show the start button if wanted."""
        self._start_b.grid(row=0, column=0)

    def _start(self):
        """When button pressed: destroys it self, calls Play."""
        self._start_b.destroy()
        self._canvas.delete('all')
        self.new_green_rectangle()
        Play(self._window, self._canvas)

    def update_score(self):
        """Update the score, by adding 1 to the current score."""
        playsound.playsound("sfx_point.wav", False)
        self._score_var.set(self._score_var.get() + 1)

    def new_text(self, *args, **kwargs):
        """Create text based on the arguments given."""
        self._canvas.create_text(*args, **kwargs)

    def new_green_rectangle(self):
        """Create the green rectangle at the bottom of the screen."""
        self._canvas.create_rectangle(0, Intro.CH - Widgets._RECT_HEIGHT, Intro.CW, Intro.CH,
                                      fill='lightgreen', outline='lightgreen')


class Pipes:
    """Create the pipes and get them moviing."""

    _GAP_SIZE = 200
    _PIPE_W = 50
    _MIN_SIZE = 50
    _PIPE_SPEED = -7.5

    def __init__(self, window, canvas):
        """Create the pipes and make it run."""
        self._window = window
        self._canvas = canvas
        self._game_over = False

        # Create the first 3 sets of pipes in the centre (height).
        # Pipes are half a canvas' width apart so 2 are on the screen.
        # Pipes are centred (height) by using CH / 2 +- GAP_S / 2.
        self._pipes = [[self._first_pipes(Intro.CW, 0, Intro.CW + Pipes._PIPE_W, Intro.CH / 2 - Pipes._GAP_SIZE / 2,
                                          outline='green', fill='lightgreen', width=Play.BORDER),
                       self._first_pipes(Intro.CW, Intro.CH / 2 + Pipes._GAP_SIZE / 2, Intro.CW + Pipes._PIPE_W,
                                         Intro.CH, fill='lightgreen', outline='green', width=Play.BORDER), True],
                       [self._first_pipes(1.5 * Intro.CW, 0, 1.5 * Intro.CW + Pipes._PIPE_W, Intro.CH / 2 -
                                          Pipes._GAP_SIZE / 2, outline='green', width=Play.BORDER, fill='lightgreen'),
                       self._first_pipes(1.5 * Intro.CW, Intro.CH / 2 + Pipes._GAP_SIZE / 2, 1.5 * Intro.CW +
                                         Pipes._PIPE_W, Intro.CH, outline='green', fill='lightgreen', width=Play.BORDER), True],
                       [self._first_pipes(2 * Intro.CW, 0, 2 * Intro.CW + Pipes._PIPE_W, Intro.CH / 2 -
                                          Pipes._GAP_SIZE / 2, width=Play.BORDER, fill='lightgreen', outline='green'),
                       self._first_pipes(2 * Intro.CW, Intro.CH / 2 + Pipes._GAP_SIZE / 2, 2 * Intro.CW +
                                         Pipes._PIPE_W, Intro.CH, outline='green', fill='lightgreen', width=Play.BORDER), True]]

        self._move_pipe()

    def get_pipes(self):
        """Get the pipe sets with their boolean."""
        return self._pipes

    def set_game_over(self):
        """Set the game_over function to True."""
        self._game_over = True

    def _height_of_pipe(self):
        """Generate a random height for the upper pipe."""
        height = random.uniform(Pipes._MIN_SIZE, Intro.CH - Pipes._MIN_SIZE -
                                Pipes._GAP_SIZE)
        return [height, height + Pipes._GAP_SIZE]

    def _move_pipe(self):
        """Move the pipes add a certain speed."""
        if self._game_over is False:
            for i in range(len(self._pipes)):
                if self._canvas.coords(self._pipes[i][0])[Play.X1] <= -Intro.CW / 4:
                    self._pipes[i] = self._create_new_pipes(i)
                self._canvas.move(self._pipes[i][1], Pipes._PIPE_SPEED, 0)
                self._canvas.move(self._pipes[i][0], Pipes._PIPE_SPEED, 0)
            # Calls itself again after 0.01 seconds.
            self._window.after(10, self._move_pipe)

    def _create_new_pipes(self, pipe):
        """Create pipes 1.5 * c_w away from where it was destroyed."""
        pipe_height = self._height_of_pipe()
        self._canvas.delete(self._pipes[pipe][0])
        self._canvas.delete(self._pipes[pipe][1])
        # New set of pipe at a 1 / 4 right of canvas at random heights.
        return [self._canvas.create_rectangle(1.25 * Intro.CW, 0, 1.25 * Intro.CW + Pipes._PIPE_W,
                                              pipe_height[0], outline='green', fill='lightgreen',
                                              width=Play.BORDER),
                self._canvas.create_rectangle(1.25 * Intro.CW, pipe_height[1], 1.25 * Intro.CW + Pipes._PIPE_W,
                                              Intro.CH, width=Play.BORDER, fill='lightgreen', outline='green'), True]

    def _first_pipes(self, *args, **kwargs):
        """Create the first 3 sets of pipes based on the parameters."""
        return self._canvas.create_rectangle(*args, **kwargs)


class Play:
    """The player moves, checks if player is out or hits the pipes."""

    BORDER = 5
    _BIRD_R = 20  # Bird radius
    _GRAVITY = 0.3
    _SPEED_UPWARDS = -5

    X1, Y1, X2, Y2 = 0, 1, 2, 3

    def __init__(self, window, canvas):
        """Main part of the program."""
        self._game_over = False
        self._not_play = True
        self._pipes = None

        self._window = window
        self._canvas = canvas
        self._widgets = Widgets(self._window, self._canvas)

        # Player: at 1 / 4 in the screen (width) and centres it (height)
        self._player = self._canvas.create_rectangle(0.25 * Intro.CW - Play._BIRD_R, Intro.CH / 2
                                                     - Play._BIRD_R, 0.25 * Intro.CW + Play._BIRD_R,
                                                     Intro.CH / 2 + Play._BIRD_R, fill='red',
                                                     width=Play.BORDER, outline='orange')
        self._p_speed = 0
        self._widgets.score_label()

        self._swoosh = threading.Thread(target=self.play_swoosh)
        self._swoosh.daemon = True

        self._window.bind('<space>', self._move_up)
        self._window.bind('<Button-1>', self._move_up)

    def play_swoosh(self):
        """Plays the swooshing sound constantly in the background."""
        while self._game_over is False:
            playsound.playsound("sfx_swooshing.wav")

    def _get_overlapping(self, pipe):
        """get the overlapping of an object and returns it."""
        return self._canvas.find_overlapping(*self._canvas.coords(pipe))

    def _move_up(self, _):
        """Move player up if space or left mouse button is pressed."""
        self._p_speed = Play._SPEED_UPWARDS
        playsound.playsound("sfx_wing.wav", False)
        if self._not_play:
            self._not_play = False
            self._pipes = Pipes(self._window, self._canvas)
            self._move_player()
            self._swoosh.start()

    def _summary(self):
        """Game over function: create text and destroys the window."""
        self._pipes.set_game_over()
        self._canvas.delete('all')
        self._widgets.destroy_label()
        self._widgets.new_green_rectangle()

        # Text centre is in the middle(width) and centre(height)
        self._widgets.new_text(Intro.CW / 2, Intro.CH / 2 - Intro.TEXT_D, text='GAME OVER',
                               fill='blanchedalmond', font='Courier 80 bold')
        self._widgets.new_text(Intro.CW / 2, Intro.CH / 2 + Intro.TEXT_D,
                               font='Courier 40', fill='DarkGoldenrod',
                               text=f'You scored: {self._widgets.get_score()}')
        # 3 seconds until window gets destroyed
        self._window.after(3000, self._destroy)

    def _destroy(self):
        """Destroy the window."""
        self._window.destroy()

    def _move_player(self):
        """Check if player is out or touches pipes and adds gravity."""
        pipe_set = self._pipes.get_pipes()
        for i in range(len(pipe_set)):
            # pipe_set[i][0] is upper pipe and pipe_set[i][1] is lower.
            # pipes[i][2] is a Boolean checking if the pipe has scored.
            if pipe_set[i][2] and self._canvas.coords(self._player)[Play.X1] \
                    >= self._canvas.coords(pipe_set[i][0])[Play.X2]:
                self._widgets.update_score()
                pipe_set[i][2] = False

            elif self._player in self._get_overlapping(pipe_set[i][0]) \
                    or self._player in self._get_overlapping((pipe_set[i][1])):
                self._game_over = True
                playsound.playsound("sfx_hit.wav")

        if self._canvas.coords(self._player)[Play.Y2] <= 0 or \
                self._canvas.coords(self._player)[Play.Y1] >= Intro.CH:
            self._game_over = True
            playsound.playsound("sfx_die.wav")

        if self._game_over:
            self._summary()

        else:
            self._p_speed += Play._GRAVITY
            self._canvas.move(self._player, 0, self._p_speed)
            # Calls itself again after 0.01 seconds.
            self._window.after(10, self._move_player)


class Intro:
    """Is the intro screen that the player gets too see."""

    _WELCOME_TEXT = 'Welcome to my Flappy Bird game.'
    _INTRO = 'Instructions: To play press start. Once you have clicked space or left button on the mouse,\n the bird ' \
             'moves up and the pipes start to come. The aim of the game is to get through\nas many pipes as possible ' \
             'without hitting them and going off screen.'
    CW = 1200  # Canvas width
    CH = 0.5*CW  # Canvas height
    TEXT_D = 30  # Text distance

    def __init__(self):
        """Run the intro and call Play once start has been pressed."""
        self._window = tk.Tk()
        self._window.title("Flappy Bird")
        self._canvas = tk.Canvas(self._window, height=Intro.CH, width=Intro.CW, bg='lightblue')
        self._widgets = Widgets(self._window, self._canvas)
        self._canvas.grid(row=0, column=0)
        self._widgets.new_green_rectangle()

        # Text centre in the middle (centre) and at a quarter height
        self._widgets.new_text(Intro.CW / 2, Intro.CH / 4 + Intro.TEXT_D,
                               fill='DarkGoldenrod', font='Courier 15',
                               text=Intro._INTRO)
        self._widgets.new_text(Intro.CW / 2, Intro.CH / 4 - Intro.TEXT_D, font='Courier 30 bold',
                               fill='blanchedalmond', text=Intro._WELCOME_TEXT)

        self._widgets.start_button()
        self._window.lift()
        self._window.mainloop()


class Menu:
    """First plays a game then ask if the user wants to play again."""

    _YES = 'yes'
    _NO = 'no'

    def __init__(self):
        """The method that runs the menu."""
        self._play_again = None
        while self._play_again != Menu._NO:
            self._play_again = None
            Intro()
            while self._play_again not in [Menu._NO, Menu._YES]:
                self._play_again = input("Would you like to play again? Yes or No?: ").lower().strip()

        print('\nThank you for playing my Flappy Bird game')


if __name__ == '__main__':
    Menu()
