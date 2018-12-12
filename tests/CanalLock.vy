gate1: public(bool) # False = Up (stopping water), True = Down (letting water through)
gate2: public(bool) # False = Up (stopping water), True = Down (letting water through)

@public
def raise_gate(pick_gate1: bool):
    if pick_gate1:
        self.gate1 = False # Raise up, stopping the flow of water
    else:
        self.gate2 = False # Raise up, stopping the flow of water

@public
def lower_gate(pick_gate1: bool):
    if pick_gate1: # Gate 2 cannot
        # Both gates can not be lowered at the same time
        assert not self.gate2
        self.gate1 = True # Lower down, allowing the flow of water
    else:
        # Both gates can not be lowered at the same time
        assert not self.gate1
        self.gate2 = True # Lower down, allowing the flow of water
