from sc2.constants import OVERLORD


class TrainOverlord:
    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """We still get supply blocked when ultralisk come out, can be improved"""
        if not self.ai.supply_cap >= 200 and self.ai.supply_left < 8:
            if self.ai.can_train(OVERLORD):
                base_amount = len(self.ai.townhalls)  # so it just calculate once per loop
                if (
                    len(self.ai.workers.ready) == 14
                    or (len(self.ai.overlords) == 2 and base_amount == 1)
                    or (base_amount == 2 and not self.ai.pools)
                ):
                    return False
                if (base_amount in (1, 2) and self.ai.already_pending(OVERLORD)) or (
                    self.ai.already_pending(OVERLORD) >= 2
                ):
                    return False
                return True
            return False
        return False

    async def handle(self, iteration):
        self.ai.actions.append(self.ai.larvae.random.train(OVERLORD))
        return True