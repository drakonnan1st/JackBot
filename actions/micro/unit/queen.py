"""Everything related to queen abilities and distribution goes here"""
from sc2.constants import EFFECT_INJECTLARVA, QUEENSPAWNLARVATIMER


class QueensAbilities:
    """Can be improved(Defense not utility)"""

    def __init__(self, main):
        self.controller = main
        self.queens = self.bases = self.enemies = None

    async def should_handle(self):
        """Injection and creep spread, can be expanded so it accepts transfusion"""
        local_controller = self.controller
        self.queens = local_controller.queens
        self.bases = local_controller.townhalls
        self.enemies = local_controller.enemies.not_structure
        return self.queens and self.bases

    async def handle(self):
        """Assign a queen to each base to make constant injections and the extras for creep spread"""
        local_controller = self.controller
        if not (local_controller.floating_buildings_bm and local_controller.supply_used >= 199):
            action = local_controller.add_action
            for queen in self.queens.idle:
                queen_position = queen.position
                queen_energy = queen.energy
                if self.enemies.closer_than(10, queen_position):
                    action(queen.attack(self.enemies.closest_to(queen_position)))
                    continue
                selected = self.bases.closest_to(queen.position)
                if queen_energy >= 25 and not selected.has_buff(QUEENSPAWNLARVATIMER):
                    action(queen(EFFECT_INJECTLARVA, selected))
                    continue
                elif queen_energy >= 25:
                    await local_controller.place_tumor(queen)
            for hatch in self.bases.ready.noqueue:
                if not self.queens.closer_than(4, hatch):
                    for queen in self.queens.idle:
                        if not self.bases.closer_than(4, queen):
                            action(queen.move(hatch.position))
                            break
            return True
