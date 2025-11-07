from symrc import Env

env = Env()
env.new("a")
env.new("b")

env.link("a", "b")
env.link("b", "a")

env.delete("a")
env.delete("b")

env.print_rc()
