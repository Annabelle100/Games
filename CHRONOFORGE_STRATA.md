# Lattice of Tides

**Lattice of Tides** is an original strategy game where players do not move armies across territory.  
Instead, they program a shared kinetic ocean-machine by placing commands into a rotating ring of phases. The board state transforms each cycle according to the command lattice, so strategy comes from timing, sequencing, and interference.

## Players
- **2–6 players**
- Best with 4

## Materials Needed

### Shared Materials
1. **1 Circular board** with 24 coast sectors and a 6-slot phase ring in the center.
2. **1 Tide wheel** with three states: Low, Crest, Break.
3. **90 Water tokens**.
4. **72 Foam tokens**.
5. **48 Drift tokens**.
6. **1 Cycle marker**.
7. **1 First Navigator marker**.

### Per Player (up to 6 sets)
1. **1 Harbor piece**.
2. **10 Beacon pieces**.
3. **8 Siphon pieces**.
4. **8 Vector tiles** (command tiles):
   - 3 Push
   - 2 Pull
   - 1 Split
   - 1 Mirror
   - 1 Null
5. **12 Claim markers**.
6. **1 reference card**.

## Core Idea (Why It Is New)
- Pieces do not attack or capture each other directly.
- Players place **commands** into a public phase ring.
- At resolution, the ring executes in order and physically moves token flows around the circle.
- Control comes from building **stable flow equations** at your Harbors while disrupting opponents’ equations by changing sequence math.

This is not territory conquest, deck combat, worker placement, trick-taking, or hidden-role play.

## Setup
1. Place the circular board and phase ring.
2. Set Tide wheel to **Low**.
3. Put 2 Water tokens in every coast sector.
4. Each player chooses a color and takes one player set.
5. In reverse turn order, each player places their Harbor in an empty coast sector.
6. Give each player 2 random Vector tiles from their own set into hand (keep rest face up near player).
7. Each player gains 2 Foam and 1 Drift from supply.
8. Randomly choose first player and give First Navigator marker.
9. Set cycle marker to 1.

## Objective and Endgame
Game ends after **9 cycles**, or immediately when one player has **5 Harmonized Sectors**.

### Harmonized Sector
A coast sector is Harmonized for a player when:
1. The player has a Beacon in that sector.
2. Sector contains exactly **3 Water** and exactly **1 Foam**.
3. The sector is adjacent to a sector containing the player’s Siphon.

### Scoring (if no instant win)
- 3 points per Harmonized Sector.
- 2 points per Siphon that is adjacent to 2+ sectors with your Claim markers.
- 1 point per unspent Drift.
- 1 point per pair of your Beacons separated by exactly 3 sectors around the ring.

Tiebreakers:
1. Most sectors with exactly 3 Water (regardless of Foam).
2. Fewest spent Vector tiles.
3. Latest in turn order.

## Turn Structure (Each Cycle)
Each cycle has 4 phases:

1. **Program Phase**
2. **Execute Phase**
3. **Construct Phase**
4. **Balance Phase**

### 1) Program Phase
In turn order, each player may place exactly one Vector tile into an empty phase slot (6 slots total).  
If all slots fill before all players place, remaining players gain 1 Drift.

If a player declines to place, they gain 1 Foam.

### 2) Execute Phase
Resolve slots 1→6:
- **Push**: move 1 Water clockwise from each sector where placer has a Beacon.
- **Pull**: move 1 Water counterclockwise toward each sector where placer has a Siphon.
- **Split**: choose one of your sectors with 2+ Water; move half (rounded down) one step each direction.
- **Mirror**: repeat the previous resolved slot, but direction is inverted.
- **Null**: cancel the next unresolved slot.

Each moved Water that enters a sector with 4+ Water creates 1 Foam there and immediately removes 1 Water.

### 3) Construct Phase
Each player may perform **two different actions**:
- Place Beacon (cost: 1 Foam)
- Place Siphon (cost: 1 Drift + 1 Foam)
- Claim sector with your marker (requires your Beacon there)
- Convert 2 Foam into 1 Drift
- Recover one spent Vector tile

Restrictions:
- Max 1 of your piece type per sector.
- Harbor sector cannot hold Siphon.
- You cannot take same action twice in this phase.

### 4) Balance Phase
1. Advance Tide wheel (Low→Crest→Break→Low).
2. Apply tide effect:
   - **Low**: every sector with 0 Water gains 1 Water.
   - **Crest**: every sector with 5+ Water loses 2 Water.
   - **Break**: each player must remove one Claim marker or spend 1 Drift.
3. Clear phase ring; placed Vector tiles become spent.
4. Pass First Navigator marker clockwise.
5. Advance cycle marker.

## Special Interaction Rules

### Resonant Arc
If a player has Beacons in three consecutive sectors, they form a Resonant Arc:
- Their Push commands move +1 additional Water from the middle sector.

### Shear Lock
If two players both have pieces in the same sector and Null is resolved there, both gain 1 Drift and that sector cannot receive Water for the remainder of Execute Phase.

### Quiet Harbor
If a Harbor’s sector has exactly 1 Water during Balance Phase, that player may recover one additional spent Vector tile.

## Why It Stays Strategic
- You forecast the full command timeline before resolution.
- Timing and slot order matters more than raw piece count.
- You can win by precision-engineering target states, not by eliminating opponents.

---

## Engine Implementation (in this repo)
The Python engine in `src/chronoforge_strata.py` currently implements:
- Program actions (place/decline vectors)
- Execute actions (Push, Pull, Split, Mirror, Null)
- Construct actions (beacon, siphon, claim, convert, recover)
- Balance/tide progression and spent-vector handling
- Harmonized-sector checks, scoring, endgame, and winner selection
