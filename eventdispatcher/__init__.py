class Dispatcher:
    listeners = {}

    def register(self, eventname, listener):
        if eventname not in self.listeners:
            self.listeners[eventname] = []
        self.listeners[eventname].append(listener)

    def dispatch(self, eventname, event):
        if eventname not in self.listeners:
            return
        for listener in self.listeners[eventname]:
            listener.on_event(event)
