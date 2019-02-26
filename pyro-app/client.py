import Pyro4

uri = input("What is the URI of the greeting object?").strip()
server_ref = Pyro4.Proxy(uri)

greeting_maker = Pyro4.Proxy("PYRONAME:example.greeting")

name = input("What is your name?").strip()
# response = server_ref.get_fortune(name)

first = input("Your first input? ").strip()
second = input("Your second input? ").strip()
response = greeting_maker.sum_numbers(name, first, second)

print(response)
