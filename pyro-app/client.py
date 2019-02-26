import Pyro4

uri = input("What is the URI of the greeting object?").strip()
server_ref = Pyro4.Proxy(uri)