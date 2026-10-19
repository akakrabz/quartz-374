"""Single-tape Turing machines as in Chapter 6.

delta: {(state, symbol): (new_state, write_symbol, move)} with move in {-1, +1}
(0 allowed for the 'stay put' variant). Missing transitions go to the reject
state (the book's convention for its examples). Moving left from cell 0 crashes.
"""

BLANK = "□"


class TM:
    def __init__(self, delta, start="start", accept="accept", reject="reject", blank=BLANK,
                 input_alphabet=None, halt=None):
        self.delta = dict(delta)
        self.start, self.accept, self.reject, self.blank = start, accept, reject, blank
        self.halt = halt  # for function-computing machines: a single halting state
        self.input_alphabet = input_alphabet

    def run(self, w, max_steps=100000, trace=False):
        """Returns (outcome, steps, tape_string, head). outcome in accept/reject/crash/halt/timeout.
        With trace=True also returns the list of configurations (state, tape, head)."""
        tape = list(w) if w else []
        head, q, steps = 0, self.start, 0
        confs = []

        def snapshot():
            t = "".join(tape).rstrip(self.blank)
            return (q, t, head)

        while True:
            if trace:
                confs.append(snapshot())
            if q == self.accept:
                out = "accept"
                break
            if q == self.reject:
                out = "reject"
                break
            if self.halt is not None and q == self.halt:
                out = "halt"
                break
            if steps >= max_steps:
                out = "timeout"
                break
            while head >= len(tape):
                tape.append(self.blank)
            a = tape[head]
            if (q, a) not in self.delta:
                q = self.reject
                steps += 1
                continue
            p, b, d = self.delta[(q, a)]
            tape[head] = b
            q = p
            head += d
            steps += 1
            if head < 0:
                out = "crash"
                break
        t = "".join(tape).rstrip(self.blank)
        if trace:
            return out, steps, t, head, confs
        return out, steps, t, head

    def accepts(self, w, max_steps=100000):
        return self.run(w, max_steps)[0] == "accept"

    __call__ = accepts
