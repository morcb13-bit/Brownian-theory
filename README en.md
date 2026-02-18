# Brownian Motion Simulation
## Recreating Thermal Motion and Diffusion with Addition Alone

> *"The universe computes with addition alone."*

---

## Overview

This repository is a Brownian motion simulation using **addition only**.

No trigonometric functions, no differential equations, no probability density functions.
Just a **24-direction integer table and addition** to reproduce thermal motion, diffusion, and entropy increase.

---

## File Structure

```
.
├── README.md
├── brownian_motion.py          # Basic: density diffusion and entropy increase
├── brownian_linked_pair.py     # Foreign object: two linked points drifting
├── brownian_drifting_v3.py     # Drifting: lighter and more swaying
└── theory.md                   # Detailed explanation of implementation
```

---

## How to Run

```bash
pip install numpy matplotlib

# Basic Brownian motion
python brownian_motion.py

# Linked pair (foreign object) version
python brownian_linked_pair.py

# Enhanced drifting version
python brownian_drifting_v3.py
```

---

## Core: Three Chains of Addition

### 1. Thermal Motion
Randomly select from a 24-direction integer table and add to velocity.
This corresponds to "molecular collisions."

### 2. Diffusion
Distribute density to 8 neighbors at 10% each.
Replaces ∇²ρ = D・∂ρ/∂t (diffusion equation).

### 3. Direction Shift
Shift direction index by step count.
Vortex-like local order emerges naturally as a byproduct of addition.

---

## Linked Pair (Foreign Object)

Imagine two points at the tip of a fishing rod swaying in the river current.

- **Mass 8** (light) → easily carried by flow
- **Friction 0.98** (low) → continues drifting by inertia
- **Bidirectional coupling** → fluid moves object, object moves fluid

---

## Results

```
Entropy:        0.0 → 4.2~4.5 (reproducing 2nd law of thermodynamics)
Vortex/Order:   Emerges naturally as byproduct of direction shift
Trajectory:     Random walk (same pattern as pollen particles)
```

---

## Discussion

Google AI verification comment (2026-02-17):

> The reason time flows forward (arrow of time) is suggested to be
> not complex physical laws, but simply "the history of addition accumulation and distribution."

> The universe breathes (Brownian motion) with addition even when not actively computing.

---

## Status

```
[IDLING]
Computing core:  Running on addition only
Observation:     Mass-8 pair continues Brownian motion following 24-direction cycle
```

---

## Collaboration

- Claude (Implementation)
- Google AI (Verification)
- morcb13-bit

---

## Changelog

- 2026-02-17: Initial release
