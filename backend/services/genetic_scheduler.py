"""
Genetic Algorithm timetable generator for Ordinus.

Chromosome: full timetable for one class.
Gene: one slot assignment (day, slot) -> subject or extra class.
Constraints: theory 3 hrs/week max 1/day, 1 faculty; lab 4 hrs as 2 blocks of 2, 2 faculty;
extra classes by hours_per_week; no faculty double-booking; respect availability.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

# Penalties (negative)
PENALTY_FACULTY_DOUBLE_BOOKING = -200
PENALTY_FACULTY_UNAVAILABLE_SLOT = -150
PENALTY_LAB_NOT_CONSECUTIVE = -120
PENALTY_THEORY_MORE_THAN_1_PER_DAY = -100
PENALTY_WEEKLY_HOURS_NOT_MET = -150
PENALTY_LAB_MISSING_TWO_STAFF = -150
PENALTY_EXTRA_CLASS_HOURS_MISSING = -80
PENALTY_EMPTY_SLOT = -10

DEFAULT_SEED = 42
POPULATION_SIZE = 80
GENERATIONS = 300
TOURNAMENT_SIZE = 5
MUTATION_RATE = 0.15

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Slot cell: (slot_type, ref_id, faculty_ids)
# slot_type: "theory" | "lab" | "extra"
# ref_id: subject_id for theory/lab, extra_class_id for extra
SlotCell = tuple[str, int, list[int]]
Chromosome = list[list[SlotCell | None]]


@dataclass
class TheoryDemand:
    """Theory subject: 3 hrs/week, max 1/day, 1 faculty."""

    subject_id: int
    faculty_id: int
    name: str


@dataclass
class LabDemand:
    """Lab subject: 4 hrs/week as 2 blocks of 2 consecutive slots, 2 faculty per session."""

    subject_id: int
    faculty_ids: list[int]  # exactly 2
    name: str


@dataclass
class ExtraDemand:
    """Extra class: hours_per_week, 1 slot per session, 1 faculty."""

    extra_class_id: int
    faculty_id: int
    name: str
    hours_per_week: int


def _make_empty_grid(working_days: int, slots_per_day: int) -> Chromosome:
    return [[None for _ in range(slots_per_day)] for _ in range(working_days)]


def _copy_grid(grid: Chromosome) -> Chromosome:
    return [[cell for cell in row] for row in grid]


def _faculty_available_at(
    faculty_id: int, day: int, slot: int, availability: dict[int, set[tuple[int, int]]]
) -> bool:
    if faculty_id not in availability:
        return True
    return (day, slot) in availability[faculty_id]


def generate_initial_population(
    working_days: int,
    slots_per_day: int,
    theory_demands: list[TheoryDemand],
    lab_demands: list[LabDemand],
    extra_demands: list[ExtraDemand],
    faculty_availability: dict[int, set[tuple[int, int]]],
    population_size: int = POPULATION_SIZE,
    seed: int | None = DEFAULT_SEED,
) -> list[Chromosome]:
    """Build population_size random timetables. Fills slots; may violate constraints."""
    if seed is not None:
        random.seed(seed)
    population: list[Chromosome] = []
    total_slots = working_days * slots_per_day

    # Flatten assignments: theory 3 each, lab 4 each (as 2 blocks we'll place later), extra by hours
    assignments: list[SlotCell] = []
    for d in theory_demands:
        for _ in range(3):
            assignments.append(("theory", d.subject_id, [d.faculty_id]))
    for d in lab_demands:
        for _ in range(4):  # 4 single-slot entries; fitness will penalize non-consecutive
            assignments.append(("lab", d.subject_id, list(d.faculty_ids)))
    for d in extra_demands:
        for _ in range(d.hours_per_week):
            assignments.append(("extra", d.extra_class_id, [d.faculty_id]))

    if len(assignments) > total_slots:
        return []

    cells = [(d, s) for d in range(working_days) for s in range(slots_per_day)]
    for _ in range(population_size):
        grid = _make_empty_grid(working_days, slots_per_day)
        random.shuffle(assignments)
        random.shuffle(cells)
        for i in range(len(assignments)):
            day, slot = cells[i]
            grid[day][slot] = assignments[i]
        population.append(grid)
    return population


def _theory_per_day(grid: Chromosome, subject_id: int) -> list[int]:
    per_day = [0] * len(grid)
    for day, row in enumerate(grid):
        for cell in row:
            if cell and cell[0] == "theory" and cell[1] == subject_id:
                per_day[day] += 1
    return per_day


def _lab_blocks(grid: Chromosome, subject_id: int) -> list[list[tuple[int, int]]]:
    """Consecutive (day, slot) blocks for this lab subject."""
    blocks: list[list[tuple[int, int]]] = []
    seen: set[tuple[int, int]] = set()
    for day, row in enumerate(grid):
        for slot in range(len(row)):
            if (day, slot) in seen:
                continue
            if not grid[day][slot] or grid[day][slot][0] != "lab" or grid[day][slot][1] != subject_id:
                continue
            block = [(day, slot)]
            seen.add((day, slot))
            while slot + 1 < len(row) and grid[day][slot + 1] and grid[day][slot + 1][0] == "lab" and grid[day][slot + 1][1] == subject_id:
                slot += 1
                block.append((day, slot))
                seen.add((day, slot))
            blocks.append(block)
    return blocks


def _extra_count(grid: Chromosome, extra_class_id: int) -> int:
    c = 0
    for row in grid:
        for cell in row:
            if cell and cell[0] == "extra" and cell[1] == extra_class_id:
                c += 1
    return c


def calculate_fitness(
    chromosome: Chromosome,
    theory_demands: list[TheoryDemand],
    lab_demands: list[LabDemand],
    extra_demands: list[ExtraDemand],
    faculty_availability: dict[int, set[tuple[int, int]]],
    faculty_used_elsewhere: dict[tuple[int, int], set[int]] | None = None,
) -> float:
    """Fitness = 1000 - penalties."""
    base_score = 1000.0
    penalty = 0.0

    # Faculty double-booking (same faculty in same (day, slot) elsewhere)
    if faculty_used_elsewhere:
        for day, row in enumerate(chromosome):
            for slot, cell in enumerate(row):
                if not cell:
                    continue
                key = (day, slot)
                if key in faculty_used_elsewhere:
                    for fid in cell[2]:
                        if fid in faculty_used_elsewhere[key]:
                            penalty += abs(PENALTY_FACULTY_DOUBLE_BOOKING)

    # Faculty unavailable
    for day, row in enumerate(chromosome):
        for slot, cell in enumerate(row):
            if not cell:
                continue
            for fid in cell[2]:
                if not _faculty_available_at(fid, day, slot, faculty_availability):
                    penalty += abs(PENALTY_FACULTY_UNAVAILABLE_SLOT)

    # Theory: max 1 per day, total 3
    for d in theory_demands:
        per_day = _theory_per_day(chromosome, d.subject_id)
        for c in per_day:
            if c > 1:
                penalty += abs(PENALTY_THEORY_MORE_THAN_1_PER_DAY) * (c - 1)
        if sum(per_day) != 3:
            penalty += abs(PENALTY_WEEKLY_HOURS_NOT_MET)

    # Lab: 2 blocks of 2 consecutive, 2 faculty per session
    for d in lab_demands:
        blocks = _lab_blocks(chromosome, d.subject_id)
        total = sum(len(b) for b in blocks)
        if total != 4:
            penalty += abs(PENALTY_WEEKLY_HOURS_NOT_MET)
        for block in blocks:
            if len(block) != 2:
                penalty += abs(PENALTY_LAB_NOT_CONSECUTIVE)
        for day, row in enumerate(chromosome):
            for slot, cell in enumerate(row):
                if cell and cell[0] == "lab" and cell[1] == d.subject_id:
                    if len(cell[2]) != 2:
                        penalty += abs(PENALTY_LAB_MISSING_TWO_STAFF)

    # Extra: weekly hours
    for d in extra_demands:
        if _extra_count(chromosome, d.extra_class_id) != d.hours_per_week:
            penalty += abs(PENALTY_EXTRA_CLASS_HOURS_MISSING)

    # Empty slots
    empty = sum(1 for row in chromosome for c in row if c is None)
    penalty += abs(PENALTY_EMPTY_SLOT) * empty

    return base_score - penalty


def selection(
    population: list[Chromosome],
    fitnesses: list[float],
    tournament_size: int = TOURNAMENT_SIZE,
    k: int | None = None,
    seed: int | None = None,
) -> list[Chromosome]:
    """Tournament selection."""
    if seed is not None:
        random.seed(seed)
    n = len(population)
    if n == 0:
        return []
    k = k or n
    selected: list[Chromosome] = []
    for _ in range(k):
        idxs = random.sample(range(n), min(tournament_size, n))
        best_idx = max(idxs, key=lambda i: fitnesses[i])
        selected.append(_copy_grid(population[best_idx]))
    return selected


def crossover(
    parent1: Chromosome,
    parent2: Chromosome,
    seed: int | None = None,
) -> Chromosome:
    """Swap random days between two timetables."""
    if seed is not None:
        random.seed(seed)
    days = len(parent1)
    if days == 0:
        return _copy_grid(parent1)
    child = _copy_grid(parent1)
    num_swap = random.randint(1, max(1, days - 1))
    for d in random.sample(range(days), num_swap):
        child[d] = [c for c in parent2[d]]
    return child


def mutation(
    chromosome: Chromosome,
    theory_demands: list[TheoryDemand],
    lab_demands: list[LabDemand],
    extra_demands: list[ExtraDemand],
    faculty_availability: dict[int, set[tuple[int, int]]],
    mutation_rate: float = MUTATION_RATE,
    seed: int | None = None,
) -> Chromosome:
    """Randomly change slot assignments."""
    if seed is not None:
        random.seed(seed)
    grid = _copy_grid(chromosome)
    all_demands: list[SlotCell] = []
    for d in theory_demands:
        for _ in range(3):
            all_demands.append(("theory", d.subject_id, [d.faculty_id]))
    for d in lab_demands:
        for _ in range(4):
            all_demands.append(("lab", d.subject_id, list(d.faculty_ids)))
    for d in extra_demands:
        for _ in range(d.hours_per_week):
            all_demands.append(("extra", d.extra_class_id, [d.faculty_id]))

    for day, row in enumerate(grid):
        for slot in range(len(row)):
            if random.random() > mutation_rate:
                continue
            if random.random() < 0.4 and all_demands:
                grid[day][slot] = random.choice(all_demands)
            elif random.random() < 0.5:
                grid[day][slot] = None
    return grid


def run_genetic_algorithm(
    working_days: int,
    slots_per_day: int,
    theory_demands: list[TheoryDemand],
    lab_demands: list[LabDemand],
    extra_demands: list[ExtraDemand],
    faculty_availability: dict[int, set[tuple[int, int]]],
    population_size: int = POPULATION_SIZE,
    generations: int = GENERATIONS,
    tournament_size: int = TOURNAMENT_SIZE,
    mutation_rate: float = MUTATION_RATE,
    seed: int | None = DEFAULT_SEED,
) -> Chromosome | None:
    """Run GA; return best chromosome."""
    if isinstance(faculty_availability.get(next(iter(faculty_availability.keys()), 0), set()), list):
        faculty_availability = {fid: set(av) for fid, av in faculty_availability.items()}

    pop = generate_initial_population(
        working_days, slots_per_day,
        theory_demands, lab_demands, extra_demands,
        faculty_availability, population_size=population_size, seed=seed,
    )
    if not pop:
        return None

    if seed is not None:
        random.seed(seed)

    best_chromosome: Chromosome | None = None
    best_fitness: float = -float("inf")

    for gen in range(generations):
        fitnesses = [
            calculate_fitness(c, theory_demands, lab_demands, extra_demands, faculty_availability, None)
            for c in pop
        ]
        for i, f in enumerate(fitnesses):
            if f > best_fitness:
                best_fitness = f
                best_chromosome = _copy_grid(pop[i])

        selected = selection(pop, fitnesses, tournament_size=tournament_size, k=len(pop), seed=None)
        next_pop: list[Chromosome] = []
        for i in range(0, len(selected) - 1, 2):
            next_pop.append(crossover(selected[i], selected[i + 1], seed=None))
        if len(selected) % 2 == 1:
            next_pop.append(selected[-1])
        for i in range(len(next_pop)):
            next_pop[i] = mutation(
                next_pop[i], theory_demands, lab_demands, extra_demands,
                faculty_availability, mutation_rate=mutation_rate, seed=None,
            )
        pop = next_pop
        if len(pop) < population_size and best_chromosome:
            while len(pop) < population_size:
                pop.append(_copy_grid(best_chromosome))

    return best_chromosome


def chromosome_to_display_format(
    chromosome: Chromosome,
    subject_id_to_name: dict[int, str],
    extra_id_to_name: dict[int, str],
    faculty_id_to_name: dict[int, str],
) -> dict[str, list[dict[str, Any]]]:
    """
    Return { "Monday": [ {"name": "Math", "faculty": ["Staff1"]}, ... ], ... }.
    """
    result: dict[str, list[dict[str, Any]]] = {}
    for day, row in enumerate(chromosome):
        day_name = DAY_NAMES[day] if day < len(DAY_NAMES) else f"Day{day + 1}"
        result[day_name] = []
        for cell in row:
            if not cell:
                result[day_name].append({"name": "Free", "faculty": []})
                continue
            slot_type, ref_id, faculty_ids = cell
            if slot_type == "theory" or slot_type == "lab":
                name = subject_id_to_name.get(ref_id, "?")
            else:
                name = extra_id_to_name.get(ref_id, "?")
            faculty_names = [faculty_id_to_name.get(fid, "?") for fid in faculty_ids]
            result[day_name].append({"name": name, "faculty": faculty_names})
    return result


def chromosome_to_slot_assignments(
    chromosome: Chromosome,
    class_id: int,
) -> list[tuple[int, int, str, int, list[int]]]:
    """(day, slot, type, ref_id, faculty_ids) for persistence."""
    out: list[tuple[int, int, str, int, list[int]]] = []
    for day, row in enumerate(chromosome):
        for slot, cell in enumerate(row):
            if cell:
                out.append((day, slot, cell[0], cell[1], list(cell[2])))
    return out
