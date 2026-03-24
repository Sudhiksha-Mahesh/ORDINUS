"""
Genetic Algorithm based timetable generator for Ordinus.

This module is intentionally **pure** (no DB access) so it's compatible with FastAPI and easy to test.

Chromosome: full timetable for one class.
Gene: one slot assignment (day, slot) -> theory subject | lab | extra class.

Hard rules we try to satisfy during construction/mutation (and penalize when violated):
- Theory: 3 hours/week, max 1 hour/day, exactly 1 faculty.
- Lab: 4 hours/week, scheduled as 2 blocks × 2 consecutive slots, exactly 2 faculty in each lab cell.
- Extra classes: hours_per_week, scheduled as single slots with assigned faculty.
- Faculty: no double booking (across classes via faculty_used_elsewhere), respect availability.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Literal, TypeAlias

import random

SlotType: TypeAlias = Literal["theory", "lab", "extra"]
DaySlot: TypeAlias = tuple[int, int]  # (day, slot)

# Slot cell: (type, ref_id, faculty_ids)
# - type: "theory" | "lab" | "extra"
# - ref_id: subject_id for theory/lab, extra_class_id for extra
# - faculty_ids: tuple of faculty ids (theory/extra: 1, lab: 2)
SlotCell: TypeAlias = tuple[SlotType, int, tuple[int, ...]]
Chromosome: TypeAlias = list[list[SlotCell | None]]  # rows=days, cols=slots

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Fitness function settings
BASE_FITNESS = 1000.0

PENALTY_FACULTY_DOUBLE_BOOKING = 200
PENALTY_FACULTY_UNAVAILABLE_SLOT = 150
PENALTY_LAB_NOT_CONSECUTIVE = 120
PENALTY_THEORY_MORE_THAN_1_PER_DAY = 100
PENALTY_WEEKLY_HOURS_NOT_MET = 150
PENALTY_LAB_MISSING_TWO_STAFF = 150
PENALTY_EXTRA_CLASS_HOURS_MISSING = 80
PENALTY_EMPTY_SLOT = 10
PENALTY_LAB_SEPARATED_BY_BREAK = 180

# GA defaults
DEFAULT_SEED = 42
POPULATION_SIZE = 80
GENERATIONS = 300
TOURNAMENT_SIZE = 5
MUTATION_RATE = 0.15


@dataclass(frozen=True, slots=True)
class TheoryDemand:
    subject_id: int
    faculty_id: int
    name: str


@dataclass(frozen=True, slots=True)
class LabDemand:
    subject_id: int
    faculty_ids: tuple[int, int]  # exactly 2
    name: str


@dataclass(frozen=True, slots=True)
class ExtraDemand:
    extra_class_id: int
    faculty_id: int | None
    name: str
    hours_per_week: int


def _make_empty_grid(working_days: int, slots_per_day: int) -> Chromosome:
    return [[None for _ in range(slots_per_day)] for _ in range(working_days)]


def _copy_grid(grid: Chromosome) -> Chromosome:
    # deep copy rows; cells are tuples/None so safe to reuse
    return [row[:] for row in grid]


def _rng(seed: int | None) -> random.Random:
    return random.Random(DEFAULT_SEED if seed is None else seed)


def _faculty_available_at(
    faculty_id: int,
    day: int,
    slot: int,
    availability: dict[int, set[DaySlot]],
) -> bool:
    # If faculty missing from availability map => treat as available everywhere (caller can enforce otherwise).
    slots = availability.get(faculty_id)
    if slots is None:
        return True
    return (day, slot) in slots


def _cell_faculty_ids(cell: SlotCell | None) -> tuple[int, ...]:
    return cell[2] if cell else ()


def _iter_cells(grid: Chromosome) -> Iterable[tuple[int, int, SlotCell]]:
    for d, row in enumerate(grid):
        for s, cell in enumerate(row):
            if cell is not None:
                yield d, s, cell


def _count_weekly(grid: Chromosome, slot_type: SlotType, ref_id: int) -> int:
    return sum(1 for _, _, cell in _iter_cells(grid) if cell[0] == slot_type and cell[1] == ref_id)


def _theory_counts_by_day(grid: Chromosome, subject_id: int) -> list[int]:
    out = [0] * len(grid)
    for d, row in enumerate(grid):
        out[d] = sum(1 for cell in row if cell and cell[0] == "theory" and cell[1] == subject_id)
    return out


def _find_lab_blocks(grid: Chromosome, subject_id: int) -> list[list[DaySlot]]:
    """
    Returns consecutive blocks (within a day) of this lab subject.
    Each block is list[(day, slot), ...] in increasing slot order.
    """
    blocks: list[list[DaySlot]] = []
    for day, row in enumerate(grid):
        slot = 0
        while slot < len(row):
            cell = row[slot]
            if not cell or cell[0] != "lab" or cell[1] != subject_id:
                slot += 1
                continue
            start = slot
            while slot < len(row) and row[slot] and row[slot][0] == "lab" and row[slot][1] == subject_id:
                slot += 1
            blocks.append([(day, s) for s in range(start, slot)])
    return blocks


def _lab_count_in_day(grid: Chromosome, subject_id: int, day: int) -> int:
    return sum(1 for cell in grid[day] if cell and cell[0] == "lab" and cell[1] == subject_id)


def _break_separates_lab(break_after_slots: list[int], start_slot: int) -> bool:
    """True if a break after (1-based) slot (start_slot+1) would sit between the two lab slots."""
    return (start_slot + 1) in break_after_slots


def _lab_blocks_valid(grid: Chromosome, subject_id: int) -> bool:
    """Valid iff there are exactly two blocks and each block is exactly 2 consecutive slots."""
    blocks = _find_lab_blocks(grid, subject_id)
    return len(blocks) == 2 and all(len(b) == 2 for b in blocks)


def _clear_lab(grid: Chromosome, subject_id: int) -> None:
    for d, row in enumerate(grid):
        for s in range(len(row)):
            cell = row[s]
            if cell and cell[0] == "lab" and cell[1] == subject_id:
                row[s] = None


def _clear_lab_run_at(grid: Chromosome, day: int, slot: int) -> None:
    """
    If (day, slot) contains a lab cell, clear the entire consecutive run for that lab on that day.
    This prevents leaving singleton lab cells when overwriting one slot of a 2-slot block.
    """
    row = grid[day]
    cell = row[slot]
    if not cell or cell[0] != "lab":
        return
    subject_id = cell[1]
    # expand left/right
    left = slot
    while left - 1 >= 0 and row[left - 1] and row[left - 1][0] == "lab" and row[left - 1][1] == subject_id:
        left -= 1
    right = slot
    while right + 1 < len(row) and row[right + 1] and row[right + 1][0] == "lab" and row[right + 1][1] == subject_id:
        right += 1
    for s in range(left, right + 1):
        row[s] = None


def _place_if_valid(
    grid: Chromosome,
    day: int,
    slot: int,
    cell: SlotCell,
    availability: dict[int, set[DaySlot]],
) -> bool:
    if grid[day][slot] is not None:
        return False
    # availability must hold for all faculty
    for fid in cell[2]:
        if not _faculty_available_at(fid, day, slot, availability):
            return False
    grid[day][slot] = cell
    return True


def _place_lab_block(
    grid: Chromosome,
    demand: LabDemand,
    day: int,
    start_slot: int,
    availability: dict[int, set[DaySlot]],
    break_after_slots: list[int] | None = None,
) -> bool:
    slots_per_day = len(grid[day])
    if start_slot < 0 or start_slot + 1 >= slots_per_day:
        return False
    # Labs must not be separated by breaks: do not place a lab block where a break falls between its two slots.
    if break_after_slots and _break_separates_lab(break_after_slots, start_slot):
        return False
    # Per-day rule: this lab can only occupy 2 slots/day (one 2-slot block per day).
    if _lab_count_in_day(grid, demand.subject_id, day) > 0:
        return False
    cell: SlotCell = ("lab", demand.subject_id, demand.faculty_ids)
    # prevent merging into >2 consecutive slots for same lab
    if start_slot - 1 >= 0:
        left = grid[day][start_slot - 1]
        if left and left[0] == "lab" and left[1] == demand.subject_id:
            return False
    if start_slot + 2 < slots_per_day:
        right = grid[day][start_slot + 2]
        if right and right[0] == "lab" and right[1] == demand.subject_id:
            return False
    if grid[day][start_slot] is not None or grid[day][start_slot + 1] is not None:
        return False
    for fid in cell[2]:
        if not _faculty_available_at(fid, day, start_slot, availability):
            return False
        if not _faculty_available_at(fid, day, start_slot + 1, availability):
            return False
    grid[day][start_slot] = cell
    grid[day][start_slot + 1] = cell
    return True


def _force_place_if_available(
    grid: Chromosome,
    day: int,
    slot: int,
    cell: SlotCell,
    availability: dict[int, set[DaySlot]],
    *,
    allow_overwrite: bool,
) -> bool:
    existing = grid[day][slot]
    if not allow_overwrite and existing is not None:
        return False
    # Never overwrite lab cells when placing other items during repair;
    # otherwise we break the required 2-consecutive lab block structure.
    if allow_overwrite and existing is not None and existing[0] == "lab":
        return False
    for fid in cell[2]:
        if not _faculty_available_at(fid, day, slot, availability):
            return False
    grid[day][slot] = cell
    return True


def _force_place_lab_block(
    grid: Chromosome,
    demand: LabDemand,
    day: int,
    start_slot: int,
    availability: dict[int, set[DaySlot]],
    *,
    allow_overwrite: bool,
    break_after_slots: list[int] | None = None,
) -> bool:
    slots_per_day = len(grid[day])
    if start_slot < 0 or start_slot + 1 >= slots_per_day:
        return False
    if break_after_slots and _break_separates_lab(break_after_slots, start_slot):
        return False
    cell: SlotCell = ("lab", demand.subject_id, demand.faculty_ids)
    # Per-day rule: only one block/day for this lab. When overwriting, we still must not
    # create two separate blocks for the same lab on the same day.
    if not allow_overwrite and _lab_count_in_day(grid, demand.subject_id, day) > 0:
        return False
    if allow_overwrite and _lab_count_in_day(grid, demand.subject_id, day) > 0:
        # Allow overwrite only if existing lab cells (if any) are exactly the target slots.
        for s in range(slots_per_day):
            if s in (start_slot, start_slot + 1):
                continue
            c = grid[day][s]
            if c and c[0] == "lab" and c[1] == demand.subject_id:
                return False
    # prevent merging into >2 consecutive slots for same lab (even when overwriting)
    if start_slot - 1 >= 0:
        left = grid[day][start_slot - 1]
        if left and left[0] == "lab" and left[1] == demand.subject_id:
            return False
    if start_slot + 2 < slots_per_day:
        right = grid[day][start_slot + 2]
        if right and right[0] == "lab" and right[1] == demand.subject_id:
            return False
    for fid in cell[2]:
        if not _faculty_available_at(fid, day, start_slot, availability):
            return False
        if not _faculty_available_at(fid, day, start_slot + 1, availability):
            return False
    if not allow_overwrite and (grid[day][start_slot] is not None or grid[day][start_slot + 1] is not None):
        return False
    if allow_overwrite:
        # If we are overwriting any lab cell (even from another lab), clear its whole run
        # so we don't leave a single orphaned lab slot behind.
        _clear_lab_run_at(grid, day, start_slot)
        _clear_lab_run_at(grid, day, start_slot + 1)
    grid[day][start_slot] = cell
    grid[day][start_slot + 1] = cell
    return True


def _remove_subject(grid: Chromosome, slot_type: SlotType, ref_id: int) -> None:
    for d, row in enumerate(grid):
        for s in range(len(row)):
            cell = row[s]
            if cell and cell[0] == slot_type and cell[1] == ref_id:
                row[s] = None


def _repair_chromosome(
    grid: Chromosome,
    working_days: int,
    slots_per_day: int,
    theory_demands: list[TheoryDemand],
    lab_demands: list[LabDemand],
    extra_demands: list[ExtraDemand],
    availability: dict[int, set[DaySlot]],
    rng: random.Random,
    break_after_slots: list[int] | None = None,
) -> Chromosome:
    """
    Repair tries to enforce weekly counts and lab 2×2 structure.
    It keeps valid placements when possible and re-fills missing ones.
    Labs are never placed so that a break separates the two slots.
    """
    repaired = _copy_grid(grid)

    # Clear anything outside bounds (defensive)
    repaired = repaired[:working_days]
    for i in range(len(repaired)):
        repaired[i] = repaired[i][:slots_per_day]
        if len(repaired[i]) < slots_per_day:
            repaired[i].extend([None] * (slots_per_day - len(repaired[i])))
    while len(repaired) < working_days:
        repaired.append([None] * slots_per_day)

    # Ensure lab cells have 2 staff and are in 2×2 blocks.
    # Run multiple passes because later lab placements (with eviction) can break earlier labs.
    valid_lab_starts_repair = [s for s in range(slots_per_day - 1) if not (break_after_slots and _break_separates_lab(break_after_slots, s))]
    if not valid_lab_starts_repair:
        valid_lab_starts_repair = list(range(slots_per_day - 1))

    for _pass in range(3):
        for lab in lab_demands:
            # Remove malformed lab cells (wrong staff count)
            for d, s, cell in list(_iter_cells(repaired)):
                if cell[0] == "lab" and cell[1] == lab.subject_id and len(cell[2]) != 2:
                    repaired[d][s] = None

            blocks = _find_lab_blocks(repaired, lab.subject_id)
            # If any block is not length 2, clear it (we will re-place)
            for block in blocks:
                if len(block) != 2:
                    for d, s in block:
                        repaired[d][s] = None

            # Count after cleanup and place missing lab blocks
            placed = _count_weekly(repaired, "lab", lab.subject_id)
            # lab needs exactly 4 cells => two blocks; only use start slots not separated by a break
            while placed < 4:
                # Prefer non-overwrite placement first, then allow eviction.
                candidates = [(d, s) for d in range(working_days) for s in valid_lab_starts_repair]
                rng.shuffle(candidates)
                success = False
                used_days = {d for d in range(working_days) if _lab_count_in_day(repaired, lab.subject_id, d) > 0}
                for day, start in candidates:
                    if day in used_days:
                        continue
                    if _force_place_lab_block(repaired, lab, day, start, availability, allow_overwrite=False, break_after_slots=break_after_slots):
                        placed += 2
                        success = True
                        break
                if success:
                    continue
                # Evict two slots if needed
                for day, start in candidates:
                    if day in used_days:
                        continue
                    if _force_place_lab_block(repaired, lab, day, start, availability, allow_overwrite=True, break_after_slots=break_after_slots):
                        placed = _count_weekly(repaired, "lab", lab.subject_id)
                        success = True
                        break
                if not success:
                    break

            # If we somehow exceeded (due to crossover), trim extras
            if placed > 4:
                coords = [(d, s) for d, s, cell in _iter_cells(repaired) if cell[0] == "lab" and cell[1] == lab.subject_id]
                rng.shuffle(coords)
                for d, s in coords[4:]:
                    repaired[d][s] = None

            # Hard enforce: lab must be exactly two 2-slot blocks (no singles split across days).
            # If not satisfied, wipe this lab and re-place two clean blocks (with eviction if needed).
            if not _lab_blocks_valid(repaired, lab.subject_id):
                _clear_lab(repaired, lab.subject_id)
                # Place two blocks on two different days when possible (to avoid 4 consecutive).
                days = list(range(working_days))
                rng.shuffle(days)
                placed_blocks = 0
                for day in days:
                    if placed_blocks >= 2:
                        break
                    starts = list(valid_lab_starts_repair)
                    rng.shuffle(starts)
                    for start in starts:
                        if _force_place_lab_block(repaired, lab, day, start, availability, allow_overwrite=True, break_after_slots=break_after_slots):
                            placed_blocks += 1
                            break
                # If still not valid (tight constraints), allow retry without day restriction.
                attempts = 0
                while attempts < 200 and not _lab_blocks_valid(repaired, lab.subject_id):
                    _clear_lab(repaired, lab.subject_id)
                    placed_blocks = 0
                    candidates = [(d, s) for d in range(working_days) for s in valid_lab_starts_repair]
                    rng.shuffle(candidates)
                    for day, start in candidates:
                        if placed_blocks >= 2:
                            break
                        if _force_place_lab_block(repaired, lab, day, start, availability, allow_overwrite=True, break_after_slots=break_after_slots):
                            placed_blocks += 1
                    attempts += 1

        # If all labs are valid, no need for more passes
        if all(_lab_blocks_valid(repaired, lab.subject_id) for lab in lab_demands):
            break

    # Theory: enforce max 1/day and weekly=3
    for th in theory_demands:
        # Remove theory cells with wrong faculty length
        for d, s, cell in list(_iter_cells(repaired)):
            if cell[0] == "theory" and cell[1] == th.subject_id:
                if len(cell[2]) != 1 or cell[2][0] != th.faculty_id:
                    repaired[d][s] = None

        per_day = _theory_counts_by_day(repaired, th.subject_id)
        # If >1 in a day, remove extras randomly
        for day, cnt in enumerate(per_day):
            if cnt <= 1:
                continue
            coords = [s for s, c in enumerate(repaired[day]) if c and c[0] == "theory" and c[1] == th.subject_id]
            rng.shuffle(coords)
            for s in coords[1:]:
                repaired[day][s] = None

        placed = _count_weekly(repaired, "theory", th.subject_id)
        cell: SlotCell = ("theory", th.subject_id, (th.faculty_id,))
        # Place missing theory on distinct days if possible
        while placed < 3:
            per_day_now = _theory_counts_by_day(repaired, th.subject_id)
            eligible_days = [d for d in range(working_days) if per_day_now[d] == 0]
            if not eligible_days:
                break
            rng.shuffle(eligible_days)
            success = False
            for day in eligible_days:
                slots = list(range(slots_per_day))
                rng.shuffle(slots)
                # try empty first
                for slot in slots:
                    if _force_place_if_available(repaired, day, slot, cell, availability, allow_overwrite=False):
                        placed += 1
                        success = True
                        break
                if success:
                    break
                # then evict if needed
                for slot in slots:
                    if _force_place_if_available(repaired, day, slot, cell, availability, allow_overwrite=True):
                        placed = _count_weekly(repaired, "theory", th.subject_id)
                        success = True
                        break
                if success:
                    break
            if not success:
                break
        # Trim excess
        if placed > 3:
            coords = [(d, s) for d, s, c in _iter_cells(repaired) if c[0] == "theory" and c[1] == th.subject_id]
            rng.shuffle(coords)
            for d, s in coords[3:]:
                repaired[d][s] = None

    # Extra: enforce weekly hours
    for ex in extra_demands:
        cell: SlotCell = ("extra", ex.extra_class_id, (ex.faculty_id,) if ex.faculty_id else ())
        # Remove malformed extras
        for d, s, c in list(_iter_cells(repaired)):
            if c[0] == "extra" and c[1] == ex.extra_class_id:
                if ex.faculty_id:
                    if len(c[2]) != 1 or c[2][0] != ex.faculty_id:
                        repaired[d][s] = None
                else:
                    if len(c[2]) != 0:
                        repaired[d][s] = None

        placed = _count_weekly(repaired, "extra", ex.extra_class_id)
        while placed < ex.hours_per_week:
            candidates = [(d, s) for d in range(working_days) for s in range(slots_per_day)]
            rng.shuffle(candidates)
            success = False
            # try without eviction
            for day, slot in candidates:
                if _force_place_if_available(repaired, day, slot, cell, availability, allow_overwrite=False):
                    placed += 1
                    success = True
                    break
            if success:
                continue
            # then with eviction
            for day, slot in candidates:
                if _force_place_if_available(repaired, day, slot, cell, availability, allow_overwrite=True):
                    placed = _count_weekly(repaired, "extra", ex.extra_class_id)
                    success = True
                    break
            if not success:
                break
        if placed > ex.hours_per_week:
            coords = [(d, s) for d, s, c in _iter_cells(repaired) if c[0] == "extra" and c[1] == ex.extra_class_id]
            rng.shuffle(coords)
            for d, s in coords[ex.hours_per_week:]:
                repaired[d][s] = None

    return repaired


def generate_initial_population(
    working_days: int,
    slots_per_day: int,
    theory_demands: list[TheoryDemand],
    lab_demands: list[LabDemand],
    extra_demands: list[ExtraDemand],
    faculty_availability: dict[int, set[DaySlot]],
    population_size: int = POPULATION_SIZE,
    seed: int | None = DEFAULT_SEED,
    break_after_slots: list[int] | None = None,
) -> list[Chromosome]:
    """
    Generate an initial population that **tries** to satisfy structural rules:
    - labs placed as 2 consecutive blocks (never separated by a break),
    - theory spread across days.

    If total required slots exceed capacity, returns [].
    """
    total_required = len(theory_demands) * 3 + len(lab_demands) * 4 + sum(e.hours_per_week for e in extra_demands)
    capacity = working_days * slots_per_day
    if total_required > capacity:
        return []

    valid_lab_starts = [s for s in range(slots_per_day - 1) if not (break_after_slots and _break_separates_lab(break_after_slots, s))]
    if not valid_lab_starts:
        valid_lab_starts = list(range(slots_per_day - 1))

    rng = _rng(seed)
    population: list[Chromosome] = []
    for _ in range(population_size):
        grid = _make_empty_grid(working_days, slots_per_day)

        # Place labs first (harder); only at start slots not separated by a break
        labs = lab_demands[:]
        rng.shuffle(labs)
        for lab in labs:
            blocks_needed = 2
            attempts = 0
            while blocks_needed > 0 and attempts < 500:
                day = rng.randrange(working_days)
                start = rng.choice(valid_lab_starts)
                if _place_lab_block(grid, lab, day, start, faculty_availability, break_after_slots=break_after_slots):
                    blocks_needed -= 1
                attempts += 1

        # Place theory (3 per week, max 1/day)
        theory = theory_demands[:]
        rng.shuffle(theory)
        for th in theory:
            cell: SlotCell = ("theory", th.subject_id, (th.faculty_id,))
            placed = 0
            attempts = 0
            while placed < 3 and attempts < 400:
                day = rng.randrange(working_days)
                if _theory_counts_by_day(grid, th.subject_id)[day] >= 1:
                    attempts += 1
                    continue
                slot = rng.randrange(slots_per_day)
                if _place_if_valid(grid, day, slot, cell, faculty_availability):
                    placed += 1
                attempts += 1

        # Place extras
        extras = extra_demands[:]
        rng.shuffle(extras)
        for ex in extras:
            cell: SlotCell = ("extra", ex.extra_class_id, (ex.faculty_id,) if ex.faculty_id else ())
            placed = 0
            attempts = 0
            while placed < ex.hours_per_week and attempts < 600:
                day = rng.randrange(working_days)
                slot = rng.randrange(slots_per_day)
                if _place_if_valid(grid, day, slot, cell, faculty_availability):
                    placed += 1
                attempts += 1

        population.append(_repair_chromosome(grid, working_days, slots_per_day, theory_demands, lab_demands, extra_demands, faculty_availability, rng, break_after_slots=break_after_slots))
    return population


def calculate_fitness(
    chromosome: Chromosome,
    theory_demands: list[TheoryDemand],
    lab_demands: list[LabDemand],
    extra_demands: list[ExtraDemand],
    faculty_availability: dict[int, set[DaySlot]],
    faculty_used_elsewhere: dict[DaySlot, set[int]] | None = None,
    break_after_slots: list[int] | None = None,
) -> float:
    """
    Fitness score starts at 1000 and subtracts penalties.
    """
    penalty = 0.0

    # faculty double booking (across classes)
    if faculty_used_elsewhere:
        for day, slot, cell in _iter_cells(chromosome):
            used = faculty_used_elsewhere.get((day, slot))
            if not used:
                continue
            for fid in cell[2]:
                if fid in used:
                    penalty += PENALTY_FACULTY_DOUBLE_BOOKING

    # faculty availability
    for day, slot, cell in _iter_cells(chromosome):
        for fid in cell[2]:
            if not _faculty_available_at(fid, day, slot, faculty_availability):
                penalty += PENALTY_FACULTY_UNAVAILABLE_SLOT

    # theory rules
    for th in theory_demands:
        per_day = _theory_counts_by_day(chromosome, th.subject_id)
        for c in per_day:
            if c > 1:
                penalty += PENALTY_THEORY_MORE_THAN_1_PER_DAY * (c - 1)
        if sum(per_day) != 3:
            penalty += PENALTY_WEEKLY_HOURS_NOT_MET

    # lab rules
    for lab in lab_demands:
        # weekly total
        if _count_weekly(chromosome, "lab", lab.subject_id) != 4:
            penalty += PENALTY_WEEKLY_HOURS_NOT_MET

        # 2 consecutive blocks of length 2
        blocks = _find_lab_blocks(chromosome, lab.subject_id)
        # each lab should produce exactly 2 blocks and each must be length 2
        if len(blocks) != 2 or any(len(b) != 2 for b in blocks):
            penalty += PENALTY_LAB_NOT_CONSECUTIVE
        # Per-day: lab occupies only 2 slots/day (so the two blocks must be on different days)
        for day in range(len(chromosome)):
            if _lab_count_in_day(chromosome, lab.subject_id, day) > 2:
                penalty += PENALTY_LAB_NOT_CONSECUTIVE

        # exactly 2 staff per lab cell
        for _, _, cell in _iter_cells(chromosome):
            if cell[0] == "lab" and cell[1] == lab.subject_id:
                if len(cell[2]) != 2:
                    penalty += PENALTY_LAB_MISSING_TWO_STAFF

        # labs must not be separated by breaks
        if break_after_slots:
            for block in _find_lab_blocks(chromosome, lab.subject_id):
                if len(block) == 2:
                    start_slot = block[0][1]
                    if _break_separates_lab(break_after_slots, start_slot):
                        penalty += PENALTY_LAB_SEPARATED_BY_BREAK

    # extras weekly hours
    for ex in extra_demands:
        if _count_weekly(chromosome, "extra", ex.extra_class_id) != ex.hours_per_week:
            penalty += PENALTY_EXTRA_CLASS_HOURS_MISSING

    # empty slots (soft)
    empty = sum(1 for row in chromosome for cell in row if cell is None)
    penalty += PENALTY_EMPTY_SLOT * empty

    return BASE_FITNESS - penalty


def selection(
    population: list[Chromosome],
    fitnesses: list[float],
    tournament_size: int = TOURNAMENT_SIZE,
    k: int | None = None,
    seed: int | None = None,
) -> list[Chromosome]:
    """
    Tournament selection.
    """
    rng = _rng(seed)
    n = len(population)
    if n == 0:
        return []
    k = n if k is None else k
    selected: list[Chromosome] = []
    for _ in range(k):
        idxs = rng.sample(range(n), min(tournament_size, n))
        best_idx = max(idxs, key=lambda i: fitnesses[i])
        selected.append(_copy_grid(population[best_idx]))
    return selected


def crossover(parent1: Chromosome, parent2: Chromosome, seed: int | None = None) -> Chromosome:
    """
    Swap random days between two timetables (as specified).
    """
    rng = _rng(seed)
    days = len(parent1)
    if days == 0:
        return _copy_grid(parent1)
    child = _copy_grid(parent1)
    num_swap = rng.randint(1, max(1, days - 1))
    for d in rng.sample(range(days), num_swap):
        child[d] = parent2[d][:]
    return child


def mutation(
    chromosome: Chromosome,
    working_days: int,
    slots_per_day: int,
    theory_demands: list[TheoryDemand],
    lab_demands: list[LabDemand],
    extra_demands: list[ExtraDemand],
    faculty_availability: dict[int, set[DaySlot]],
    mutation_rate: float = MUTATION_RATE,
    seed: int | None = None,
    break_after_slots: list[int] | None = None,
) -> Chromosome:
    """
    Mutation: randomly change slot assignments while trying to keep structural rules.
    """
    rng = _rng(seed)
    grid = _copy_grid(chromosome)

    if rng.random() > mutation_rate:
        return grid

    # Pick one of a few structured mutation operators
    op = rng.random()
    if op < 0.35:
        # swap two slots (keeps counts)
        d1, s1 = rng.randrange(working_days), rng.randrange(slots_per_day)
        d2, s2 = rng.randrange(working_days), rng.randrange(slots_per_day)
        grid[d1][s1], grid[d2][s2] = grid[d2][s2], grid[d1][s1]
    elif op < 0.70 and lab_demands and slots_per_day >= 2:
        # move one lab block (only to start slots not separated by a break)
        lab = rng.choice(lab_demands)
        blocks = [b for b in _find_lab_blocks(grid, lab.subject_id) if len(b) == 2]
        valid_lab_starts = [s for s in range(slots_per_day - 1) if not (break_after_slots and _break_separates_lab(break_after_slots, s))]
        if not valid_lab_starts:
            valid_lab_starts = list(range(slots_per_day - 1))
        if blocks:
            block = rng.choice(blocks)
            # clear old
            for d, s in block:
                grid[d][s] = None
            # try place new
            attempts = 0
            while attempts < 80:
                day = rng.randrange(working_days)
                start = rng.choice(valid_lab_starts)
                if _place_lab_block(grid, lab, day, start, faculty_availability, break_after_slots=break_after_slots):
                    break
                attempts += 1
    else:
        # move a single theory/extra occurrence to a random empty slot
        coords_filled = [(d, s) for d in range(working_days) for s in range(slots_per_day) if grid[d][s] is not None]
        coords_empty = [(d, s) for d in range(working_days) for s in range(slots_per_day) if grid[d][s] is None]
        if coords_filled and coords_empty:
            d1, s1 = rng.choice(coords_filled)
            cell = grid[d1][s1]
            if cell and cell[0] in ("theory", "extra"):
                d2, s2 = rng.choice(coords_empty)
                # for theory ensure still max 1/day (soft; repair will fix)
                if cell[0] == "theory":
                    subj_id = cell[1]
                    if _theory_counts_by_day(grid, subj_id)[d2] >= 1:
                        return _repair_chromosome(grid, working_days, slots_per_day, theory_demands, lab_demands, extra_demands, faculty_availability, rng, break_after_slots=break_after_slots)
                if all(_faculty_available_at(fid, d2, s2, faculty_availability) for fid in cell[2]):
                    grid[d1][s1] = None
                    grid[d2][s2] = cell

    # Repair after mutation to keep rule compliance high
    return _repair_chromosome(grid, working_days, slots_per_day, theory_demands, lab_demands, extra_demands, faculty_availability, rng, break_after_slots=break_after_slots)


def run_genetic_algorithm(
    working_days: int,
    slots_per_day: int,
    theory_demands: list[TheoryDemand],
    lab_demands: list[LabDemand],
    extra_demands: list[ExtraDemand],
    faculty_availability: dict[int, set[DaySlot]],
    faculty_used_elsewhere: dict[DaySlot, set[int]] | None = None,
    population_size: int = POPULATION_SIZE,
    generations: int = GENERATIONS,
    tournament_size: int = TOURNAMENT_SIZE,
    mutation_rate: float = MUTATION_RATE,
    seed: int | None = DEFAULT_SEED,
    break_after_slots: list[int] | None = None,
) -> Chromosome | None:
    """
    Run GA and return the best chromosome for this class.
    Labs are never placed so that a break separates the two slots of a lab block.
    """
    rng = _rng(seed)
    pop = generate_initial_population(
        working_days=working_days,
        slots_per_day=slots_per_day,
        theory_demands=theory_demands,
        lab_demands=lab_demands,
        extra_demands=extra_demands,
        faculty_availability=faculty_availability,
        population_size=population_size,
        seed=seed,
        break_after_slots=break_after_slots,
    )
    if not pop:
        return None

    best: Chromosome | None = None
    best_fit = -1e18

    for gen in range(generations):
        # keep determinism but avoid identical RNG streams per generation
        gen_seed = rng.randint(0, 2**31 - 1)
        gen_rng = _rng(gen_seed)

        fitnesses = [
            calculate_fitness(c, theory_demands, lab_demands, extra_demands, faculty_availability, faculty_used_elsewhere, break_after_slots=break_after_slots)
            for c in pop
        ]
        for i, f in enumerate(fitnesses):
            if f > best_fit:
                best_fit = f
                best = _copy_grid(pop[i])

        selected = selection(pop, fitnesses, tournament_size=tournament_size, k=len(pop), seed=gen_rng.randint(0, 2**31 - 1))
        next_pop: list[Chromosome] = []
        for i in range(0, len(selected) - 1, 2):
            child = crossover(selected[i], selected[i + 1], seed=gen_rng.randint(0, 2**31 - 1))
            child = _repair_chromosome(child, working_days, slots_per_day, theory_demands, lab_demands, extra_demands, faculty_availability, gen_rng, break_after_slots=break_after_slots)
            next_pop.append(child)
        if len(selected) % 2 == 1:
            next_pop.append(selected[-1])

        for i in range(len(next_pop)):
            next_pop[i] = mutation(
                next_pop[i],
                working_days=working_days,
                slots_per_day=slots_per_day,
                theory_demands=theory_demands,
                lab_demands=lab_demands,
                extra_demands=extra_demands,
                faculty_availability=faculty_availability,
                mutation_rate=mutation_rate,
                seed=gen_rng.randint(0, 2**31 - 1),
                break_after_slots=break_after_slots,
            )

        # elitism: keep best
        if best is not None:
            next_pop[0] = _copy_grid(best)
        pop = next_pop

    return best


def chromosome_to_display_format(
    chromosome: Chromosome,
    subject_id_to_name: dict[int, str],
    extra_id_to_name: dict[int, str],
    faculty_id_to_name: dict[int, str],
) -> dict[str, list[dict[str, Any]]]:
    """
    Output format:
    {
      "Monday": [{"name": "...", "faculty": ["..."]}, ...],
      ...
    }
    """
    result: dict[str, list[dict[str, Any]]] = {}
    for day, row in enumerate(chromosome):
        day_name = DAY_NAMES[day] if day < len(DAY_NAMES) else f"Day{day + 1}"
        result[day_name] = []
        for cell in row:
            if cell is None:
                result[day_name].append({"name": "Free", "faculty": []})
                continue
            slot_type, ref_id, faculty_ids = cell
            name = (
                subject_id_to_name.get(ref_id, "?")
                if slot_type in ("theory", "lab")
                else extra_id_to_name.get(ref_id, "?")
            )
            faculty_names = [faculty_id_to_name.get(fid, "?") for fid in faculty_ids]
            result[day_name].append({"name": name, "faculty": faculty_names})
    return result


def chromosome_to_slot_assignments(chromosome: Chromosome, class_id: int) -> list[tuple[int, int, str, int, list[int]]]:
    """
    (day, slot, type, ref_id, faculty_ids) for persistence.
    """
    out: list[tuple[int, int, str, int, list[int]]] = []
    for day, row in enumerate(chromosome):
        for slot, cell in enumerate(row):
            if cell is None:
                continue
            out.append((day, slot, cell[0], cell[1], list(cell[2])))
    return out
