class Motor:
    # Initialize the Motor Class
    def __init__(self, name):
        self.name = name
        self.home = 0
        self.limit_a = 100
        self.limit_b = -100
        self.speed = 1
        self.current_pos = self.get_pos()

    # Query motor for position and return
    def get_pos(self):
        current_pos = 0
        return current_pos

    # Move motor in "negative" direction
    def negative(self):
        print("Moving {} stage left/down".format(self.name))
        # Check if limit will be hit
        temp_pos = self.current_pos - self.speed
        if temp_pos <= self.limit_b:
            print("Limit Reached")
        else:
            self.current_pos -= self.speed

    # Move motor in "positive" direction
    def positive(self):
        print("Moving {} stage right/up".format(self.name))
        # Check if limit will be hit
        temp_pos = self.current_pos + self.speed
        if temp_pos >= self.limit_a:
            print("Limit Reached")
        else:
            self.current_pos += self.speed

    def go_home(self):
        print("Going home")
        if self.current_pos != self.home:
            self.current_pos = self.home

    # def change_speed(self, new_speed):



def main():
    loop = True
    y_stage = Motor("Y-Stage")
    x_stage = Motor("X-Stage")

    while loop:
        action = input("COMMANDS:\n"
                       "Y-Stage Up/Down/Home: [yu/yd/yh]\n"
                       "X-Stage Up/Down/Home: [xu/xd/xh]\n"
                       "Get Current Position: [ypos/xpos]\n"
                       "Quit: [qu]\n")
        if action == "yu":
            y_stage.positive()
        elif action == "yd":
            y_stage.negative()
        elif action == "yh":
            y_stage.go_home()
        elif action == "xu":
            x_stage.positive()
        elif action == "xd":
            x_stage.negative()
        elif action == "xh":
            x_stage.go_home()
        elif action == "ypos":
            print(y_stage.current_pos)
        elif action == "xpos":
            print(x_stage.current_pos)
        elif action == "qu":
            loop = False
            print("Exiting Program.")
        else:
            print("~~~Incorrect Input~~~")
        print()


if __name__ == "__main__":
    main()