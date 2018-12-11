from hypothesis import note, settings
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant


class DieHardProblem(RuleBasedStateMachine):
    small = 0
    big = 0

    @rule()
    def fill_small(self):
        self.small = 3

    @rule()
    def fill_big(self):
        self.big = 5

    @rule()
    def empty_small(self):
        self.small = 0

    @rule()
    def empty_big(self):
        self.big = 0

    @rule()
    def pour_small_into_big(self):
        old_big = self.big
        self.big = min(5, self.big + self.small)
        self.small = self.small - (self.big - old_big)

    @rule()
    def pour_big_into_small(self):
        old_small = self.small
        self.small = min(3, self.small + self.big)
        self.big = self.big - (self.small - old_small)

    @invariant()
    def physics_of_jugs(self):
        assert 0 <= self.small <= 3
        assert 0 <= self.big <= 5

    @invariant()
    def die_hard_problem_not_solved(self):
        note("> small: {s} big: {b}".format(s=self.small, b=self.big))
        assert self.big != 4


# The default of 200 is sometimes not enough for Hypothesis to find
# a falsifying example.
with settings(max_examples=2000):
    DieHardTest = DieHardProblem.TestCase
