"""Everything related to a single unit in the game goes here"""
from typing import List, Optional, Set, Union
from s2clientprotocol import raw_pb2 as raw_pb
from sc2.ids.buff_id import BuffId
from . import unit_command
from .data import ALLIANCE, ATTRIBUTE, CLOAK_STATE, DISPLAY_TYPE, RACE, TARGET_TYPE, warpgate_abilities
from .game_data import GameData, UnitTypeData
from .ids.ability_id import AbilityId
from .ids.unit_typeid import UnitTypeId
from .position import Point2, Point3


class Unit:
    """Returns info and data from a single unit"""

    def __init__(self, proto_data, game_data):
        assert isinstance(proto_data, raw_pb.Unit)
        assert isinstance(game_data, GameData)
        self.proto = proto_data
        self._game_data = game_data
        self._weapons = self._ground_weapon = self._air_weapon = None

    @property
    def type_id(self) -> UnitTypeId:
        """Returns the unit id"""
        return UnitTypeId(self.proto.unit_type)

    @property
    def type_data(self) -> UnitTypeData:
        """Returns the unit data"""
        return self._game_data.units[self.proto.unit_type]

    @property
    def is_snapshot(self):
        """Checks if the unit was visible on a snapshot"""
        return self.proto.display_type == DISPLAY_TYPE.Snapshot.value

    @property
    def is_visible(self):
        """Checks if the unit is outside the FOW"""
        return self.proto.display_type == DISPLAY_TYPE.Visible.value

    @property
    def alliance(self) -> ALLIANCE:
        """Returns the unit alliance"""
        return self.proto.alliance

    @property
    def is_mine(self) -> bool:
        """Checks if the unit is mine"""
        return self.proto.alliance == ALLIANCE.Self.value

    @property
    def is_enemy(self) -> bool:
        """Checks if the unit is from the enemy"""
        return self.proto.alliance == ALLIANCE.Enemy.value

    @property
    def tag(self) -> int:
        """Return the unit tag"""
        return self.proto.tag

    @property
    def owner_id(self) -> int:
        """Returns the unit owner's id"""
        return self.proto.owner

    @property
    def position(self) -> Point2:
        """2d position of the unit."""
        return Point2((self.proto.pos.x, self.proto.pos.y))

    @property
    def position3d(self) -> Point3:
        """3d position of the unit."""
        return Point3.from_proto(self.proto.pos)

    def distance_to(self, point: Union["Unit", Point2, Point3]) -> Union[int, float]:
        """ Using the 2d distance between self and p. To calculate the 3d distance,
         use unit.position3d.distance_to(p) """
        return self.position.distance_to_point2(point.position)

    @property
    def facing(self) -> Union[int, float]:
        """Returns where the unit is facing"""
        return self.proto.facing

    @property
    def radius(self) -> Union[int, float]:
        """Returns the unit radius"""
        return self.proto.radius

    @property
    def detect_range(self) -> Union[int, float]:
        """Returns the unit detection range"""
        return self.proto.detect_range

    @property
    def radar_range(self) -> Union[int, float]:
        """Returns the unit radar range"""
        return self.proto.radar_range

    @property
    def build_progress(self) -> Union[int, float]:
        """Returns the structure building progress"""
        return self.proto.build_progress

    @property
    def is_ready(self) -> bool:
        """Checks if the unit is ready(not in the training queue)"""
        return self.build_progress == 1.0

    @property
    def cloak(self) -> CLOAK_STATE:
        """Returns if the unit is cloaked(not sure)"""
        return self.proto.cloak

    @property
    def is_blip(self) -> bool:
        """ Detected by sensor tower. """
        return self.proto.is_blip

    @property
    def is_powered(self) -> bool:
        """ Is powered by a pylon nearby. """
        return self.proto.is_powered

    @property
    def is_burrowed(self) -> bool:
        """Checks if the unit is burrowed"""
        return self.proto.is_burrowed

    @property
    def is_flying(self) -> bool:
        """Checks if the unit is flying"""
        return self.proto.is_flying

    @property
    def is_structure(self) -> bool:
        """Checks if the unit is a structure"""
        return ATTRIBUTE.Structure.value in self.type_data.attributes

    @property
    def is_light(self) -> bool:
        """Checks if the unit is from the light class"""
        return ATTRIBUTE.Light.value in self.type_data.attributes

    @property
    def is_armored(self) -> bool:
        """Checks if the unit is from the armored class"""
        return ATTRIBUTE.Armored.value in self.type_data.attributes

    @property
    def is_biological(self) -> bool:
        """Checks if the unit is from the biological class"""
        return ATTRIBUTE.Biological.value in self.type_data.attributes

    @property
    def is_mechanical(self) -> bool:
        """Checks if the unit is from the mechanical class"""
        return ATTRIBUTE.Mechanical.value in self.type_data.attributes

    @property
    def is_robotic(self) -> bool:
        """Checks if the unit is from the robotic class"""
        return ATTRIBUTE.Robotic.value in self.type_data.attributes

    @property
    def is_massive(self) -> bool:
        """Checks if the unit is from the massive class"""
        return ATTRIBUTE.Massive.value in self.type_data.attributes

    @property
    def is_psionic(self) -> bool:
        """Checks if the unit is from the psionic class"""
        return ATTRIBUTE.Psionic.value in self.type_data.attributes

    @property
    def is_mineral_field(self) -> bool:
        """Checks if the unit is a mineral field"""
        return self.type_data.has_minerals

    @property
    def is_vespene_geyser(self) -> bool:
        """Checks if the unit is a geyser"""
        return self.type_data.has_vespene

    @property
    def tech_alias(self) -> Optional[List[UnitTypeId]]:
        """ Building tech equality, e.g. OrbitalCommand is the same as CommandCenter
        For Hive, this returns [UnitTypeId.Hatchery, UnitTypeId.Lair]
        For SCV, this returns None """
        return self.type_data.tech_alias

    @property
    def unit_alias(self) -> Optional[UnitTypeId]:
        """ Building type equality, e.g. FlyingOrbitalCommand is the same as OrbitalCommand
        For flying OrbitalCommand, this returns UnitTypeId.OrbitalCommand
        For SCV, this returns None """
        return self.type_data.unit_alias

    @property
    def race(self) -> RACE:
        """Returns the unit race"""
        return RACE(self.type_data.proto.race)

    @property
    def health(self) -> Union[int, float]:
        """Returns the unit current health"""
        return self.proto.health

    @property
    def health_max(self) -> Union[int, float]:
        """Returns the unit max health"""
        return self.proto.health_max

    @property
    def health_percentage(self) -> Union[int, float]:
        """Returns the unit current health percentage"""
        if not self.proto.health_max:
            return 0
        return self.proto.health / self.proto.health_max

    @property
    def shield(self) -> Union[int, float]:
        """Returns the unit current shield"""
        return self.proto.shield

    @property
    def shield_max(self) -> Union[int, float]:
        """Returns the unit max shield"""
        return self.proto.shield_max

    @property
    def shield_percentage(self) -> Union[int, float]:
        """Returns the unit current shield percentage"""
        if not self.proto.shield_max:
            return 0
        return self.proto.shield / self.proto.shield_max

    @property
    def energy(self) -> Union[int, float]:
        """Returns the unit current energy"""
        return self.proto.energy

    @property
    def energy_max(self) -> Union[int, float]:
        """Returns the unit max energy"""
        return self.proto.energy_max

    @property
    def energy_percentage(self) -> Union[int, float]:
        """Returns the unit current energy percentage"""
        if not self.proto.energy_max:
            return 0
        return self.proto.energy / self.proto.energy_max

    @property
    def mineral_contents(self) -> int:
        """ How many minerals a mineral field has left to mine from """
        return self.proto.mineral_contents

    @property
    def vespene_contents(self) -> int:
        """ How much gas is remaining in a geyser """
        return self.proto.vespene_contents

    @property
    def has_vespene(self) -> bool:
        """ Checks if a geyser has any gas remaining (can't build extractors on empty geysers), useful for lategame """
        return bool(self.proto.vespene_contents)

    @property
    def weapons(self):
        """Gets the weapons of the unit"""
        if self._weapons:
            return self._weapons
        if hasattr(self.type_data.proto, "weapons"):
            self._weapons = self.type_data.proto.weapons
            return self._weapons
        return None

    @property
    def weapon_cooldown(self) -> Union[int, float]:
        """ Returns some time (more than game loops) until the unit can fire again,
        returns -1 for units that can't attack
         Usage:
        if unit.weapon_cooldown == 0:
            await self.do(unit.attack(target))
        elif unit.weapon_cooldown < 0:
            await self.do(unit.move(closest_allied_unit_because_cant_attack))
        else:
            await self.do(unit.move(retreatPosition))
        """
        if self.can_attack_ground or self.can_attack_air:
            return self.proto.weapon_cooldown
        return -1

    @property
    def cargo_size(self) -> Union[float, int]:
        """ How much cargo this unit uses up in cargo_space """
        return self.type_data.cargo_size

    @property
    def has_cargo(self) -> bool:
        """ If this unit has units loaded """
        return bool(self.proto.cargo_space_taken)

    @property
    def cargo_used(self) -> Union[float, int]:
        """ How much cargo space is used (some units take up more than 1 space) """
        return self.proto.cargo_space_taken

    @property
    def cargo_max(self) -> Union[float, int]:
        """ How much cargo space is totally available
        - CC: 5, Bunker: 4, Medivac: 8 and Bunker can only load infantry, CC only SCVs """
        return self.proto.cargo_space_max

    @property
    def passengers(self) -> Set["PassengerUnit"]:
        """ Units inside a Bunker, CommandCenter, Nydus, Medivac, WarpPrism, Overlord """
        return {PassengerUnit(unit, self._game_data) for unit in self.proto.passengers}

    @property
    def passengers_tags(self) -> Set[int]:
        """Returns the unit that are passengers tags"""
        return {unit.tag for unit in self.proto.passengers}

    @property
    def ground_weapon(self):
        """Gets the ground weapons of the unit"""
        if self._ground_weapon:
            return self._ground_weapon
        if self.weapons:
            self._ground_weapon = next(
                (weapon for weapon in self.weapons if weapon.type in {TARGET_TYPE.Ground.value, TARGET_TYPE.Any.value}),
                None,
            )
            return self._ground_weapon
        return None

    @property
    def air_weapon(self):
        """Gets the air weapons of the unit"""
        if self._air_weapon:
            return self._air_weapon
        if self.weapons:
            self._air_weapon = next(
                (weapon for weapon in self.weapons if weapon.type in {TARGET_TYPE.Air.value, TARGET_TYPE.Any.value}),
                None,
            )
            return self._air_weapon
        return None

    @property
    def can_attack_ground(self) -> bool:
        """Checks if the unit can attack ground"""
        if hasattr(self.type_data.proto, "weapons"):
            weapons = self.type_data.proto.weapons
            weapon = next(
                (weapon for weapon in weapons if weapon.type in {TARGET_TYPE.Ground.value, TARGET_TYPE.Any.value}), None
            )
            return weapon is not None
        return False

    @property
    def ground_dps(self) -> Union[int, float]:
        """ Does not include upgrades """
        if hasattr(self.type_data.proto, "weapons"):
            weapons = self.type_data.proto.weapons
            weapon = next(
                (weapon for weapon in weapons if weapon.type in {TARGET_TYPE.Ground.value, TARGET_TYPE.Any.value}), None
            )
            if weapon:
                return (weapon.damage * weapon.attacks) / weapon.speed
        return 0

    @property
    def ground_range(self) -> Union[int, float]:
        """ Does not include upgrades """
        return self.ground_weapon and self.ground_weapon.range

    @property
    def can_attack_air(self) -> bool:
        """ Does not include upgrades """
        return self.air_weapon

    @property
    def air_dps(self) -> Union[int, float]:
        """ Does not include upgrades """
        return self.air_weapon and (self.air_weapon.damage * self.air_weapon.attacks) / self.air_weapon.speed

    @property
    def air_range(self) -> Union[int, float]:
        """ Does not include upgrades """
        return self.air_weapon and self.air_weapon.range

    def target_in_range(self, target: "Unit", bonus_distance: Union[int, float] = 0) -> bool:
        """ Includes the target's radius when calculating distance to target """
        if self.can_attack_ground and not target.is_flying:
            unit_attack_range = self.ground_range
        elif self.can_attack_air and target.is_flying and (target.is_flying or target.type_id == UnitTypeId.COLOSSUS):
            unit_attack_range = self.air_range
        else:
            unit_attack_range = -1
        return self.distance_to(target) + bonus_distance <= self.radius + target.radius + unit_attack_range

    @property
    def armor(self) -> Union[int, float]:
        """ Does not include upgrades """
        return self.type_data.proto.armor

    @property
    def sight_range(self) -> Union[int, float]:
        """Returns the unit sight range"""
        return self.type_data.proto.sight_range

    @property
    def movement_speed(self) -> Union[int, float]:
        """Returns the unit movement speed"""
        return self.type_data.proto.movement_speed

    @property
    def is_carrying_minerals(self) -> bool:
        """ Checks if a worker (or MULE) is carrying (gold-)minerals. """
        return self.has_buff(BuffId.CARRYMINERALFIELDMINERALS) or self.has_buff(
            BuffId.CARRYHIGHYIELDMINERALFIELDMINERALS
        )

    @property
    def is_carrying_vespene(self) -> bool:
        """ Checks if a worker is carrying vespene. """
        return (
            self.has_buff(BuffId.CARRYHARVESTABLEVESPENEGEYSERGAS)
            or self.has_buff(BuffId.CARRYHARVESTABLEVESPENEGEYSERGASPROTOSS)
            or self.has_buff(BuffId.CARRYHARVESTABLEVESPENEGEYSERGASZERG)
        )

    @property
    def is_selected(self) -> bool:
        """Checks if the unit is selected"""
        return self.proto.is_selected

    @property
    def orders(self) -> List["UnitOrder"]:
        """Returns the list of unit orders"""
        return [UnitOrder.from_proto(o, self._game_data) for o in self.proto.orders]

    @property
    def noqueue(self) -> bool:
        """Checks if the structure has no queue"""
        return not self.orders

    @property
    def is_moving(self) -> bool:
        """Checks if the unit is moving"""
        return self.orders and self.orders[0].ability.id is AbilityId.MOVE

    @property
    def is_attacking(self) -> bool:
        """Checks if the unit is attacking"""
        return self.orders and self.orders[0].ability.id in (
            AbilityId.ATTACK,
            AbilityId.ATTACK_ATTACK,
            AbilityId.ATTACK_ATTACKTOWARDS,
            AbilityId.ATTACK_ATTACKBARRAGE,
            AbilityId.SCAN_MOVE,
        )

    @property
    def is_gathering(self) -> bool:
        """ Checks if a unit is on its way to a mineral field / vespene geyser to mine. """
        return self.orders and self.orders[0].ability.id is AbilityId.HARVEST_GATHER

    @property
    def is_returning(self) -> bool:
        """ Checks if a unit is returning from mineral field / vespene geyser to deliver resources to townhall. """
        return self.orders and self.orders[0].ability.id is AbilityId.HARVEST_RETURN

    @property
    def is_collecting(self) -> bool:
        """ Combines the two properties above. """
        return self.orders and self.orders[0].ability.id in {AbilityId.HARVEST_GATHER, AbilityId.HARVEST_RETURN}

    @property
    def is_constructing_scv(self) -> bool:
        """ Checks if the unit is an SCV that is currently building. """
        return self.orders and self.orders[0].ability.id in {
            AbilityId.TERRANBUILD_ARMORY,
            AbilityId.TERRANBUILD_BARRACKS,
            AbilityId.TERRANBUILD_BUNKER,
            AbilityId.TERRANBUILD_COMMANDCENTER,
            AbilityId.TERRANBUILD_ENGINEERINGBAY,
            AbilityId.TERRANBUILD_FACTORY,
            AbilityId.TERRANBUILD_FUSIONCORE,
            AbilityId.TERRANBUILD_GHOSTACADEMY,
            AbilityId.TERRANBUILD_MISSILETURRET,
            AbilityId.TERRANBUILD_REFINERY,
            AbilityId.TERRANBUILD_SENSORTOWER,
            AbilityId.TERRANBUILD_STARPORT,
            AbilityId.TERRANBUILD_SUPPLYDEPOT,
        }

    @property
    def is_repairing(self) -> bool:
        """Checks if the unit is repairing"""
        return self.orders and self.orders[0].ability.id in {
            AbilityId.EFFECT_REPAIR,
            AbilityId.EFFECT_REPAIR_MULE,
            AbilityId.EFFECT_REPAIR_SCV,
        }

    @property
    def order_target(self) -> Optional[Union[int, Point2]]:
        """ Returns the target tag (if it is a Unit) or Point2 (if it is a Position) from the first order,
         return None if the unit is idle """
        if self.orders:
            if isinstance(self.orders[0].target, int):
                return self.orders[0].target
            return Point2.from_proto(self.orders[0].target)
        return None

    @property
    def is_idle(self) -> bool:
        """Checks if the unit is idle"""
        return not self.orders

    @property
    def add_on_tag(self) -> int:
        """Returns the add-on tag"""
        return self.proto.add_on_tag

    @property
    def add_on_land_position(self) -> Point2:
        """ If unit is add-on (techlab or reactor),
         returns the position where a terran building has to land to connect to add-on """
        return self.position.offset(Point2((-2.5, 0.5)))

    @property
    def has_add_on(self) -> bool:
        """Checks if the structure has add-on"""
        return self.add_on_tag != 0

    @property
    def assigned_harvesters(self) -> int:
        """Returns the current quantity of workers assigned to this unit"""
        return self.proto.assigned_harvesters

    @property
    def ideal_harvesters(self) -> int:
        """Returns the ideal quantity of workers assigned to this unit"""
        return self.proto.ideal_harvesters

    @property
    def surplus_harvesters(self) -> int:
        """ Returns a positive number if it has too many harvesters mining,
         a negative number if it has too few mining """
        return -(self.proto.ideal_harvesters - self.proto.assigned_harvesters)

    @property
    def name(self) -> str:
        """Returns the unit name"""
        return self.type_data.name

    def train(self, unit, *args, **kwargs):
        """Make the unit train something if it can"""
        return self(self._game_data.units[unit.value].creation_ability.id, *args, **kwargs)

    def build(self, unit, *args, **kwargs):
        """Make the unit build something if it can"""
        return self(self._game_data.units[unit.value].creation_ability.id, *args, **kwargs)

    def research(self, upgrade, *args, **kwargs):
        """ Requires UpgradeId to be passed instead of AbilityId """
        return self(self._game_data.upgrades[upgrade.value].research_ability.id, *args, **kwargs)

    def has_buff(self, buff):
        """Checks if the unit has a buff"""
        assert isinstance(buff, BuffId)
        return buff.value in self.proto.buff_ids

    def warp_in(self, unit, placement, *args, **kwargs):
        """Make the unit warp-in something if it can"""
        normal_creation_ability = self._game_data.units[unit.value].creation_ability.id
        return self(warpgate_abilities[normal_creation_ability], placement, *args, **kwargs)

    def attack(self, *args, **kwargs):
        """Make the unit attack something if it can"""
        return self(AbilityId.ATTACK, *args, **kwargs)

    def gather(self, *args, **kwargs):
        """Make the unit gather a resource if it can"""
        return self(AbilityId.HARVEST_GATHER, *args, **kwargs)

    def return_resource(self, *args, **kwargs):
        """Make the unit return a resource if it can"""
        return self(AbilityId.HARVEST_RETURN, *args, **kwargs)

    def move(self, *args, **kwargs):
        """Make the unit move somewhere if it can"""
        return self(AbilityId.MOVE, *args, **kwargs)

    def scan_move(self, *args, **kwargs):
        """Make the unit scan somewhere if it can"""
        return self(AbilityId.SCAN_MOVE, *args, **kwargs)

    def hold_position(self, *args, **kwargs):
        """Make the unit hold position if it can"""
        return self(AbilityId.HOLDPOSITION, *args, **kwargs)

    def stop(self, *args, **kwargs):
        """Make the unit stop if it can"""
        return self(AbilityId.STOP, *args, **kwargs)

    def repair(self, *args, **kwargs):
        """Make the unit repair something if it can"""
        return self(AbilityId.EFFECT_REPAIR, *args, **kwargs)

    def __hash__(self):
        return hash(self.tag)

    def __call__(self, ability, *args, **kwargs):
        return unit_command.UnitCommand(ability, self, *args, **kwargs)

    def __repr__(self):
        return f"Unit(name={self.name !r}, tag={self.tag})"


class UnitOrder:
    """Single unit requirements to conclude an order"""

    @classmethod
    def from_proto(cls, proto, game_data):
        """Gets information from the sc2 protocol"""
        return cls(
            game_data.abilities[proto.ability_id],
            (proto.target_world_space_pos if proto.HasField("target_world_space_pos") else proto.target_unit_tag),
            proto.progress,
        )

    def __init__(self, ability, target, progress=None):
        self.ability = ability
        self.target = target
        self.progress = progress

    def __repr__(self):
        return f"UnitOrder({self.ability}, {self.target}, {self.progress})"


class PassengerUnit:
    """Single units that are passengers"""

    def __init__(self, proto_data, game_data):
        assert isinstance(game_data, GameData)
        self.proto = proto_data
        self._game_data = game_data

    def __repr__(self):
        return f"PassengerUnit(name={self.name !r}, tag={self.tag})"

    @property
    def type_id(self) -> UnitTypeId:
        """Returns unit id"""
        return UnitTypeId(self.proto.unit_type)

    @property
    def type_data(self) -> UnitTypeData:
        """Returns unit data"""
        return self._game_data.units[self.proto.unit_type]

    @property
    def name(self) -> str:
        """Returns unit name"""
        return self.type_data.name

    @property
    def race(self) -> RACE:
        """Returns unit race"""
        return RACE(self.type_data.proto.race)

    @property
    def tag(self) -> int:
        """Returns unit tag"""
        return self.proto.tag

    @property
    def is_structure(self) -> bool:
        """Checks if the unit is a structure"""
        return ATTRIBUTE.Structure.value in self.type_data.attributes

    @property
    def is_light(self) -> bool:
        """Checks if the unit is from the light class"""
        return ATTRIBUTE.Light.value in self.type_data.attributes

    @property
    def is_armored(self) -> bool:
        """Checks if the unit is from the armored class"""
        return ATTRIBUTE.Armored.value in self.type_data.attributes

    @property
    def is_biological(self) -> bool:
        """Checks if the unit is from the biological class"""
        return ATTRIBUTE.Biological.value in self.type_data.attributes

    @property
    def is_mechanical(self) -> bool:
        """Checks if the unit is from the mechanical class"""
        return ATTRIBUTE.Mechanical.value in self.type_data.attributes

    @property
    def is_robotic(self) -> bool:
        """Checks if the unit is from the robotic class"""
        return ATTRIBUTE.Robotic.value in self.type_data.attributes

    @property
    def is_massive(self) -> bool:
        """Checks if the unit is from the massive class"""
        return ATTRIBUTE.Massive.value in self.type_data.attributes

    @property
    def cargo_size(self) -> Union[float, int]:
        """ How much cargo this unit uses up in cargo_space """
        return self.type_data.cargo_size

    @property
    def can_attack_ground(self) -> bool:
        """Checks if the unit can attack ground"""
        if hasattr(self.type_data.proto, "weapons"):
            weapons = self.type_data.proto.weapons
            weapon = next(
                (weapon for weapon in weapons if weapon.type in [TARGET_TYPE.Ground.value, TARGET_TYPE.Any.value]), None
            )
            return weapon is not None
        return False

    @property
    def ground_dps(self) -> Union[int, float]:
        """ Does not include upgrades """
        if hasattr(self.type_data.proto, "weapons"):
            weapons = self.type_data.proto.weapons
            weapon = next(
                (weapon for weapon in weapons if weapon.type in [TARGET_TYPE.Ground.value, TARGET_TYPE.Any.value]), None
            )
            if weapon:
                return (weapon.damage * weapon.attacks) / weapon.speed
        return 0

    @property
    def ground_range(self) -> Union[int, float]:
        """ Does not include upgrades """
        if hasattr(self.type_data.proto, "weapons"):
            weapons = self.type_data.proto.weapons
            weapon = next(
                (weapon for weapon in weapons if weapon.type in [TARGET_TYPE.Ground.value, TARGET_TYPE.Any.value]), None
            )
            if weapon:
                return weapon.range
        return 0

    @property
    def can_attack_air(self) -> bool:
        """ Does not include upgrades """
        if hasattr(self.type_data.proto, "weapons"):
            weapons = self.type_data.proto.weapons
            weapon = next(
                (weapon for weapon in weapons if weapon.type in [TARGET_TYPE.Air.value, TARGET_TYPE.Any.value]), None
            )
            return weapon is not None
        return False

    @property
    def air_dps(self) -> Union[int, float]:
        """ Does not include upgrades """
        if hasattr(self.type_data.proto, "weapons"):
            weapons = self.type_data.proto.weapons
            weapon = next(
                (weapon for weapon in weapons if weapon.type in [TARGET_TYPE.Air.value, TARGET_TYPE.Any.value]), None
            )
            if weapon:
                return (weapon.damage * weapon.attacks) / weapon.speed
        return 0

    @property
    def air_range(self) -> Union[int, float]:
        """ Does not include upgrades """
        if hasattr(self.type_data.proto, "weapons"):
            weapons = self.type_data.proto.weapons
            weapon = next(
                (weapon for weapon in weapons if weapon.type in [TARGET_TYPE.Air.value, TARGET_TYPE.Any.value]), None
            )
            if weapon:
                return weapon.range
        return 0

    @property
    def armor(self) -> Union[int, float]:
        """ Does not include upgrades """
        return self.type_data.proto.armor

    @property
    def sight_range(self) -> Union[int, float]:
        """Returns unit sight range"""
        return self.type_data.proto.sight_range

    @property
    def movement_speed(self) -> Union[int, float]:
        """Returns unit movement speed"""
        return self.type_data.proto.movement_speed

    @property
    def health(self) -> Union[int, float]:
        """Returns unit current health"""
        return self.proto.health

    @property
    def health_max(self) -> Union[int, float]:
        """Returns unit max health"""
        return self.proto.health_max

    @property
    def health_percentage(self) -> Union[int, float]:
        """Returns unit current health percentage"""
        if not self.proto.health_max:
            return 0
        return self.proto.health / self.proto.health_max

    @property
    def shield(self) -> Union[int, float]:
        """Returns unit current shield"""
        return self.proto.shield

    @property
    def shield_max(self) -> Union[int, float]:
        """Returns unit max shield"""
        return self.proto.shield_max

    @property
    def shield_percentage(self) -> Union[int, float]:
        """Returns unit current shield percentage"""
        if not self.proto.shield_max:
            return 0
        return self.proto.shield / self.proto.shield_max

    @property
    def energy(self) -> Union[int, float]:
        """Returns unit current energy"""
        return self.proto.energy

    @property
    def energy_max(self) -> Union[int, float]:
        """Returns unit max energy"""
        return self.proto.energy_max

    @property
    def energy_percentage(self) -> Union[int, float]:
        """Returns unit current energy percentage"""
        if not self.proto.energy_max:
            return 0
        return self.proto.energy / self.proto.energy_max
