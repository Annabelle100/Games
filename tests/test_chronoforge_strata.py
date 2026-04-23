import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.chronoforge_strata import LatticeOfTidesGame, RuleViolation, TideState, VectorType


class TestLatticeOfTides(unittest.TestCase):
    def setUp(self):
        self.game = LatticeOfTidesGame(3, seed=7)

    def test_setup_has_24_sectors_with_two_water(self):
        self.assertEqual(len(self.game.sectors), 24)
        self.assertTrue(all(s.water == 2 for s in self.game.sectors))

    def test_place_beacon_costs_foam(self):
        p = self.game.players[0]
        start = p.foam
        self.game.place_beacon(0, 3)
        self.assertIn(3, p.beacons)
        self.assertEqual(p.foam, start - 1)

    def test_siphon_cannot_be_on_harbor(self):
        harbor = self.game.players[0].harbor
        with self.assertRaises(RuleViolation):
            self.game.place_siphon(0, harbor)

    def test_claim_requires_beacon(self):
        with self.assertRaises(RuleViolation):
            self.game.claim_sector(0, 5)

    def test_convert_foam_to_drift(self):
        p = self.game.players[0]
        self.game.convert_foam_to_drift(0)
        self.assertEqual(p.foam, 0)
        self.assertEqual(p.drift, 2)

    def test_push_moves_water_clockwise_from_beacon(self):
        self.game.place_beacon(0, 4)
        self.game.place_vector(0, VectorType.PUSH)
        before_src = self.game.sectors[4].water
        before_dst = self.game.sectors[5].water
        self.game.execute_phase()
        self.assertEqual(self.game.sectors[4].water, before_src - 1)
        self.assertEqual(self.game.sectors[5].water, before_dst + 1)

    def test_null_cancels_next_slot(self):
        self.game.place_beacon(0, 4)
        self.game.place_vector(0, VectorType.NULL)
        self.game.place_vector(0, VectorType.PUSH)
        src = self.game.sectors[4].water
        self.game.execute_phase()
        self.assertEqual(self.game.sectors[4].water, src)

    def test_recover_spent_vector(self):
        p = self.game.players[0]
        self.game.place_vector(0, VectorType.PUSH)
        self.game.balance_phase()
        ready_before = p.ready_vectors[VectorType.PUSH]
        self.game.recover_spent_vector(0, VectorType.PUSH)
        self.assertEqual(p.ready_vectors[VectorType.PUSH], ready_before + 1)

    def test_balance_advances_tide(self):
        self.assertEqual(self.game.tide, TideState.LOW)
        self.game.balance_phase()
        self.assertEqual(self.game.tide, TideState.CREST)

    def test_harmonized_sector_and_scoring(self):
        p = self.game.players[0]
        self.game.place_beacon(0, 8)
        p.siphons.append(9)
        self.game.sectors[8].water = 3
        self.game.sectors[8].foam = 1
        self.assertEqual(self.game.harmonized_sectors(0), 1)
        self.assertGreaterEqual(self.game.score_player(0), 3)


if __name__ == "__main__":
    unittest.main()
