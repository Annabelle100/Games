# Chronoforge Strata

A brand-new tabletop strategy game built around **time-layered construction** and **causality conflicts**.

## Core Concept
Players are rival Architects shaping a floating world made of unstable "time-stone."  
Every action is taken in one of three time layers:
- **Past Layer** (foundation)
- **Present Layer** (active world)
- **Future Layer** (planned world)

Pieces can affect other layers in asymmetric ways. You can set up structures in the Future that only become usable later, or rewrite weak foundations in the Past to destabilize an opponent in the Present. This creates a strategic system based on **cross-time dependency**, not territory control alone.

---

## Players
- **2 to 5 players**
- Best with 3–4 for diplomacy and layered prediction

---

## Materials Needed

### Board and Shared Components
1. **1 Hex board with 91 cells** (9-row hex map)
2. **3 transparent Time Sheets** (Past, Present, Future) that overlay the same board
3. **120 Strata Cubes** (resource cubes in 4 colors)
   - 30 Ore (gray)
   - 30 Flux (blue)
   - 30 Fiber (green)
   - 30 Ember (red)
4. **45 Instability tokens**
5. **30 Resonance rings** (small rings placed around pieces to show active links)
6. **1 Round tracker**
7. **1 First Architect marker**

### Per Player Components (5 sets)
Each player gets:
1. **1 Architect Core** (main command piece)
2. **9 Keystone pieces** (structural nodes)
3. **6 Relay pieces** (link / transport units)
4. **5 Refractor pieces** (rule-bending units)
5. **12 Influence markers**
6. **1 player aid card**

### Cards
1. **36 Blueprint cards** (modular actions)
2. **30 Event cards** (global effects)
3. **20 Secret Objective cards**

---

## Setup
1. Place the hex board in the center.
2. Place the three Time Sheets stacked in order: Past (bottom), Present (middle), Future (top).
3. Shuffle Blueprint, Event, and Secret Objective decks separately.
4. Each player:
   - Takes one full piece set and markers.
   - Places their Architect Core in the Present Layer on any outer-ring hex (clockwise order).
   - Draws 3 Blueprint cards.
   - Draws 1 Secret Objective.
   - Receives starting resources: 2 Ore, 1 Flux, 1 Fiber, 0 Ember.
5. Put all Instability tokens and Resonance rings in supply.
6. Set round tracker to Round 1.

---

## Winning the Game
The game ends at the end of Round 10, or immediately if a player completes **all 3 Apex Conditions**.

### Apex Conditions
A player must satisfy all three simultaneously:
1. **Anchor Condition**: control at least 4 Keystone-connected hexes in the Present.
2. **Continuity Condition**: maintain at least 2 active links between Past↔Present and 2 between Present↔Future.
3. **Identity Condition**: Architect Core is stable (not destabilized) and has at least 3 Influence markers adjacent.

If nobody triggers instant win, highest **Apex Score** at end of Round 10 wins:
- 2 points per controlled Keystone hex (Present)
- 3 points per completed continuity link pair
- 1 point per unspent Ember
- Secret Objective points (4–8)

Tiebreaker: fewer Instability tokens on your network, then turn order reverse (later player wins tie).

---

## Turn Structure (per Round)
Each round has 5 phases:

1. **Forecast Phase**
2. **Draft Phase**
3. **Action Phase**
4. **Cascade Phase**
5. **Stability Check Phase**

### 1) Forecast Phase
- Reveal 1 Event card affecting all players for this round.
- Some events target only one layer; others alter transfer costs or collapse thresholds.

### 2) Draft Phase
- Each player draws 2 Blueprint cards.
- Choose 1 to keep, pass 1 left.
- After one pass, keep received card.
- Hand limit: 5 cards (discard excess).

### 3) Action Phase
In clockwise order, players each take **2 Actions**, then repeat for **3 cycles** (total 6 actions each round).

Possible actions:
1. **Mine**: collect 1 resource from a hex you influence in Present.
2. **Build**: place Keystone or Relay in any layer by paying listed cost.
3. **Shift**: move one non-Core piece to an adjacent hex in same layer.
4. **Project**: place a ghost marker of a piece in Future (cost Flux).
5. **Retrofit**: alter one Past-layer piece type (Keystone ↔ Relay) by paying Ore + Fiber.
6. **Resonate**: create link between two of your pieces in adjacent layers on same hex (use Resonance ring).
7. **Invoke Blueprint**: play a Blueprint card for its unique effect.
8. **Stabilize**: remove 1 Instability token from your network by spending any 2 resources.

#### Action Limits
- You may take the same action multiple times except Invoke Blueprint (max 1 per cycle).
- Architect Core cannot move.
- You cannot build on an occupied hex in same layer.

### 4) Cascade Phase
Resolve all Future ghost markers:
- If projected piece is still legal and paid in full, it materializes in Present.
- If blocked or unpaid, place 1 Instability token on owner and discard the ghost marker.

Then resolve Past edits:
- Any Retrofit from this round attempts to "propagate" to Present copies on same hex.
- If propagation conflicts with existing piece type, conflict creates Instability on both owners.

### 5) Stability Check Phase
For each player:
- If they have **5+ Instability tokens**, their network is destabilized:
  - Remove one random non-Core piece in Present.
  - Discard one random Blueprint card.
  - Then reduce Instability by 2.

Advance round marker, pass First Architect marker clockwise.

---

## Layer Interaction Rules (Unique Engine)

### A. Continuity Links
A continuity link requires:
- same owner
- same hex coordinate
- connected pieces in adjacent layers
- Resonance ring present

A full chain (Past→Present→Future) grants:
- +1 influence range from that hex
- one free Shift per round from that chain origin

### B. Causality Pressure
Each time a player edits Past where another player has Present control on same hex:
- Place 1 pressure marker on that opponent.
- At 3 pressure markers, opponent must either spend 2 Flux or gain 1 Instability.
- Pressure then resets to 0.

### C. Echo Occupancy
If two players occupy same hex coordinate in different layers, they are in Echo Occupancy.
- Echo Occupancy enables trade, sabotage, or resonance theft via Blueprint effects.
- No combat dice; conflicts are deterministic via costs and layer precedence.

Layer precedence for forced resolution:
1. Past (structural authority)
2. Present (positional authority)
3. Future (intent authority)

---

## Blueprint Card Framework (Examples)
- **Paradox Clamp**: cancel one opposing Future materialization on a matching hex.
- **Harmonic Bridge**: create two resonance links for one action.
- **Ashen Ledger**: convert all Ember to score now; gain equal Instability.
- **Root Rewrite**: perform a second Retrofit this cycle for free.
- **Silent Corridor**: your Relays ignore occupancy when shifting this cycle.

---

## Secret Objective Examples
- **Threefold Spine**: build one full Past→Present→Future chain in 3 separate hexes.
- **Beneath Notice**: win with 0 Instability at game end.
- **Borrowed Tomorrow**: materialize at least 6 Future projections during game.

---

## Why This Game Is Distinct
Chronoforge Strata is intentionally designed around:
- **Layered simultaneity** (same map, multiple times)
- **Deterministic non-combat conflict**
- **Cross-round causality edits** (Past retrofits affecting Present)
- **Requirement to balance growth with temporal stability**

The strategic depth comes from creating a resilient multi-layer network while pressuring others through causality, not by directly eliminating units.
