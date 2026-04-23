from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple
import random


SECTOR_COUNT = 24
PHASE_RING_SLOTS = 6
MAX_CYCLES = 9


class TideState(str, Enum):
    LOW = "low"
    CREST = "crest"
    BREAK = "break"


class VectorType(str, Enum):
    PUSH = "push"
    PULL = "pull"
    SPLIT = "split"
    MIRROR = "mirror"
    NULL = "null"


@dataclass
class Sector:
    water: int = 0
    foam: int = 0


@dataclass
class PlayerState:
    player_id: int
    harbor: int
    foam: int = 2
    drift: int = 1
    beacons: List[int] = field(default_factory=list)
    siphons: List[int] = field(default_factory=list)
    claims: List[int] = field(default_factory=list)
    spent_vectors: List[VectorType] = field(default_factory=list)
    ready_vectors: Dict[VectorType, int] = field(
        default_factory=lambda: {
            VectorType.PUSH: 3,
            VectorType.PULL: 2,
            VectorType.SPLIT: 1,
            VectorType.MIRROR: 1,
            VectorType.NULL: 1,
        }
    )


@dataclass
class PhaseSlot:
    owner: int
    vector: VectorType
    cancelled: bool = False


class RuleViolation(ValueError):
    pass


class LatticeOfTidesGame:
    """Playable deterministic rules engine for Lattice of Tides."""

    def __init__(self, num_players: int, seed: Optional[int] = None) -> None:
        if not 2 <= num_players <= 6:
            raise ValueError("Lattice of Tides supports 2 to 6 players.")
        self.random = random.Random(seed)
        self.num_players = num_players
        self.cycle = 1
        self.first_navigator = 0
        self.tide = TideState.LOW

        self.sectors: List[Sector] = [Sector(water=2, foam=0) for _ in range(SECTOR_COUNT)]
        harbor_positions = self._harbor_positions(num_players)
        self.players: Dict[int, PlayerState] = {
            pid: PlayerState(player_id=pid, harbor=harbor_positions[pid])
            for pid in range(num_players)
        }
        self.phase_ring: List[PhaseSlot] = []

    @staticmethod
    def _harbor_positions(num_players: int) -> List[int]:
        step = SECTOR_COUNT // num_players
        return [(i * step) % SECTOR_COUNT for i in range(num_players)]

    @staticmethod
    def _cw(idx: int) -> int:
        return (idx + 1) % SECTOR_COUNT

    @staticmethod
    def _ccw(idx: int) -> int:
        return (idx - 1) % SECTOR_COUNT

    def _validate_player(self, player_id: int) -> None:
        if player_id not in self.players:
            raise RuleViolation(f"Unknown player id {player_id}.")

    def _validate_sector(self, sector_idx: int) -> None:
        if not 0 <= sector_idx < SECTOR_COUNT:
            raise RuleViolation(f"Invalid sector index {sector_idx}.")

    # -----------------------------
    # Program phase actions
    # -----------------------------
    def place_vector(self, player_id: int, vector: VectorType) -> None:
        self._validate_player(player_id)
        p = self.players[player_id]
        if len(self.phase_ring) >= PHASE_RING_SLOTS:
            raise RuleViolation("Phase ring is full.")
        if p.ready_vectors[vector] <= 0:
            raise RuleViolation(f"Player {player_id} has no ready {vector.value} vector.")
        self.phase_ring.append(PhaseSlot(owner=player_id, vector=vector))
        p.ready_vectors[vector] -= 1

    def decline_program(self, player_id: int) -> None:
        self._validate_player(player_id)
        self.players[player_id].foam += 1

    # -----------------------------
    # Construct phase actions
    # -----------------------------
    def place_beacon(self, player_id: int, sector_idx: int) -> None:
        self._validate_player(player_id)
        self._validate_sector(sector_idx)
        p = self.players[player_id]
        if p.foam < 1:
            raise RuleViolation("Need 1 foam to place a beacon.")
        if sector_idx in p.beacons:
            raise RuleViolation("Beacon already present in that sector.")
        p.foam -= 1
        p.beacons.append(sector_idx)

    def place_siphon(self, player_id: int, sector_idx: int) -> None:
        self._validate_player(player_id)
        self._validate_sector(sector_idx)
        p = self.players[player_id]
        if sector_idx == p.harbor:
            raise RuleViolation("Harbor sector cannot hold siphon.")
        if p.foam < 1 or p.drift < 1:
            raise RuleViolation("Need 1 foam and 1 drift to place a siphon.")
        if sector_idx in p.siphons:
            raise RuleViolation("Siphon already present in that sector.")
        p.foam -= 1
        p.drift -= 1
        p.siphons.append(sector_idx)

    def claim_sector(self, player_id: int, sector_idx: int) -> None:
        self._validate_player(player_id)
        self._validate_sector(sector_idx)
        p = self.players[player_id]
        if sector_idx not in p.beacons:
            raise RuleViolation("Need your beacon in a sector before claiming it.")
        if sector_idx in p.claims:
            raise RuleViolation("Sector already claimed by this player.")
        p.claims.append(sector_idx)

    def convert_foam_to_drift(self, player_id: int) -> None:
        self._validate_player(player_id)
        p = self.players[player_id]
        if p.foam < 2:
            raise RuleViolation("Need 2 foam to convert into 1 drift.")
        p.foam -= 2
        p.drift += 1

    def recover_spent_vector(self, player_id: int, vector: Optional[VectorType] = None) -> None:
        self._validate_player(player_id)
        p = self.players[player_id]
        if not p.spent_vectors:
            raise RuleViolation("No spent vectors to recover.")
        if vector is None:
            recovered = p.spent_vectors.pop()
        else:
            try:
                idx = p.spent_vectors.index(vector)
            except ValueError as exc:
                raise RuleViolation(f"Spent {vector.value} vector not available.") from exc
            recovered = p.spent_vectors.pop(idx)
        p.ready_vectors[recovered] += 1

    # -----------------------------
    # Execute phase
    # -----------------------------
    def execute_phase(self) -> None:
        prev_executed_vector: Optional[VectorType] = None
        null_pending = False
        for slot in self.phase_ring:
            if null_pending:
                slot.cancelled = True
                null_pending = False
                continue

            if slot.vector == VectorType.NULL:
                null_pending = True
                prev_executed_vector = VectorType.NULL
                continue

            if slot.vector == VectorType.MIRROR:
                if prev_executed_vector and prev_executed_vector != VectorType.NULL:
                    self._execute_vector(slot.owner, self._mirror_of(prev_executed_vector))
                    prev_executed_vector = VectorType.MIRROR
                continue

            self._execute_vector(slot.owner, slot.vector)
            prev_executed_vector = slot.vector

    def _mirror_of(self, vector: VectorType) -> VectorType:
        if vector == VectorType.PUSH:
            return VectorType.PULL
        if vector == VectorType.PULL:
            return VectorType.PUSH
        return vector

    def _execute_vector(self, player_id: int, vector: VectorType) -> None:
        p = self.players[player_id]
        if vector == VectorType.PUSH:
            for sector in list(p.beacons):
                bonus = 1 if self._has_resonant_arc_middle(player_id, sector) else 0
                self._move_water(sector, self._cw(sector), 1 + bonus)
        elif vector == VectorType.PULL:
            for sector in list(p.siphons):
                src = self._cw(sector)
                self._move_water(src, sector, 1)
        elif vector == VectorType.SPLIT:
            options = [s for s in p.beacons if self.sectors[s].water >= 2]
            if options:
                chosen = options[0]
                amount = self.sectors[chosen].water // 2
                self.sectors[chosen].water -= amount
                left = amount // 2
                right = amount - left
                self._deposit(self._cw(chosen), right)
                self._deposit(self._ccw(chosen), left)

    def _has_resonant_arc_middle(self, player_id: int, sector: int) -> bool:
        p = self.players[player_id]
        b = set(p.beacons)
        return self._ccw(sector) in b and sector in b and self._cw(sector) in b

    def _move_water(self, source: int, target: int, amount: int) -> None:
        moved = min(amount, self.sectors[source].water)
        if moved <= 0:
            return
        self.sectors[source].water -= moved
        self._deposit(target, moved)

    def _deposit(self, target: int, amount: int) -> None:
        self.sectors[target].water += amount
        if self.sectors[target].water >= 4:
            self.sectors[target].foam += 1
            self.sectors[target].water -= 1

    # -----------------------------
    # Balance phase and scoring
    # -----------------------------
    def balance_phase(self) -> None:
        self.tide = {
            TideState.LOW: TideState.CREST,
            TideState.CREST: TideState.BREAK,
            TideState.BREAK: TideState.LOW,
        }[self.tide]

        if self.tide == TideState.LOW:
            for sec in self.sectors:
                if sec.water == 0:
                    sec.water = 1
        elif self.tide == TideState.CREST:
            for sec in self.sectors:
                if sec.water >= 5:
                    sec.water = max(0, sec.water - 2)
        else:  # BREAK
            for p in self.players.values():
                if p.drift >= 1:
                    p.drift -= 1
                elif p.claims:
                    p.claims.pop()

        for p in self.players.values():
            if self.sectors[p.harbor].water == 1 and p.spent_vectors:
                self.recover_spent_vector(p.player_id)

        for slot in self.phase_ring:
            self.players[slot.owner].spent_vectors.append(slot.vector)
        self.phase_ring.clear()

        self.first_navigator = (self.first_navigator + 1) % self.num_players
        self.cycle += 1

    def harmonized_sectors(self, player_id: int) -> int:
        p = self.players[player_id]
        harmonized = 0
        for sector in p.beacons:
            sec = self.sectors[sector]
            adj = {self._cw(sector), self._ccw(sector)}
            if sec.water == 3 and sec.foam == 1 and any(a in p.siphons for a in adj):
                harmonized += 1
        return harmonized

    def score_player(self, player_id: int) -> int:
        p = self.players[player_id]
        harmonized_points = 3 * self.harmonized_sectors(player_id)
        siphon_points = 0
        for siphon in p.siphons:
            adj = {self._cw(siphon), self._ccw(siphon)}
            if len(adj & set(p.claims)) >= 2:
                siphon_points += 2

        beacon_positions = sorted(set(p.beacons))
        paired = 0
        seen_pairs: set[Tuple[int, int]] = set()
        for b in beacon_positions:
            other = (b + 3) % SECTOR_COUNT
            if other in beacon_positions:
                pair = tuple(sorted((b, other)))
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    paired += 1

        return harmonized_points + siphon_points + p.drift + paired

    def game_over(self) -> bool:
        return self.cycle > MAX_CYCLES or any(
            self.harmonized_sectors(pid) >= 5 for pid in self.players
        )

    def winner(self) -> Optional[int]:
        if not self.game_over():
            return None
        candidates = sorted(self.players.keys(), key=lambda pid: self.score_player(pid), reverse=True)
        top_score = self.score_player(candidates[0])
        top_players = [pid for pid in candidates if self.score_player(pid) == top_score]
        if len(top_players) == 1:
            return top_players[0]

        # tiebreaker 1: sectors with exactly 3 water
        def t1(pid: int) -> int:
            player_beacons = set(self.players[pid].beacons)
            return sum(1 for idx in player_beacons if self.sectors[idx].water == 3)

        best_t1 = max(t1(pid) for pid in top_players)
        top_players = [pid for pid in top_players if t1(pid) == best_t1]
        if len(top_players) == 1:
            return top_players[0]

        # tiebreaker 2: fewer spent vectors
        fewest_spent = min(len(self.players[pid].spent_vectors) for pid in top_players)
        top_players = [pid for pid in top_players if len(self.players[pid].spent_vectors) == fewest_spent]
        if len(top_players) == 1:
            return top_players[0]

        # tiebreaker 3: latest in turn order (highest id)
        return max(top_players)
