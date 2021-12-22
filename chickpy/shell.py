from cmd import Cmd

from chickpy.processor import Command


class ChickPrompt(Cmd):
    prompt = "chickpy> "
    intro = "Welcome to chickpy shell! Type ? to list commands"

    def onecmd(self, line):
        try:
            return super().onecmd(line)
        except Exception as e:
            print(f"{e}")
            return False  # don't stop

    def do_exit(self, inp):
        print("Bye")
        return True

    def help_exit(self):
        print("exit the application. Shorthand: x q Ctrl-D.")

    def default(self, inp):
        if inp == "x" or inp == "q":
            return self.do_exit(inp)

        print("Default: {}".format(inp))

    def help_run(self):
        print("Run a script")

    def do_run(self, script):
        Command.run(script)

    do_EOF = do_exit
    help_EOF = help_exit


if __name__ == "__main__":
    ChickPrompt().cmdloop()
