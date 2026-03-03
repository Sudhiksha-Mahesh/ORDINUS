"""
CSP-style backtracking scheduler for timetable generation.
Modular so heuristics can be added later.
"""
from dataclasses import dataclass


@dataclass
class SlotAssignment:
    """One (day, slot) -> (subject_id, faculty_id)."""

    day: int
    slot: int
    subject_id: int
    faculty_id: int


@dataclass
class SubjectDemand:
    """Subject that must be placed with remaining hours."""

    subject_id: int
    faculty_id: int
    hours_remaining: int


def _faculty_available_at(
    faculty_id: int,
    day: int,
    slot: int,
    availability: dict[int, set[tuple[int, int]]],
) -> bool:
    """Check if faculty is available at (day, slot)."""
    if faculty_id not in availability:
        return False
    return (day, slot) in availability[faculty_id]


def backtrack_schedule(
    working_days: int,
    slots_per_day: int,
    subject_demands: list[SubjectDemand],
    faculty_availability: dict[int, list[tuple[int, int]]],  # faculty_id -> [(day, slot), ...]
) -> list[SlotAssignment] | None:
    """
    Fill grid (days x slots) with subject slots.
    Constraints: faculty available at (day, slot); weekly hours satisfied.
    Returns list of SlotAssignment or None if no solution.
    """
    # Build sets for O(1) lookup
    availability: dict[int, set[tuple[int, int]]] = {
        fid: set(av) for fid, av in faculty_availability.items()
    }
    total_slots = working_days * slots_per_day
    total_hours = sum(d.hours_remaining for d in subject_demands)
    if total_hours > total_slots:
        return None

    # Mutable copy of demands: hours_remaining per (subject_id, faculty_id)
    demands_map: dict[tuple[int, int], int] = {}
    for d in subject_demands:
        key = (d.subject_id, d.faculty_id)
        demands_map[key] = demands_map.get(key, 0) + d.hours_remaining
    demand_list = [
        SubjectDemand(subj_id, fac_id, hrs)
        for (subj_id, fac_id), hrs in demands_map.items()
    ]
    # Try most-constrained first (most hours) to improve backtracking success
    demand_list.sort(key=lambda x: -x.hours_remaining)
    result: list[SlotAssignment] = []

    def solve(cell_index: int) -> bool:
        if cell_index >= total_slots:
            return all(d.hours_remaining == 0 for d in demand_list)
        day = cell_index // slots_per_day
        slot = cell_index % slots_per_day

        for d in demand_list:
            if d.hours_remaining <= 0:
                continue
            if not _faculty_available_at(d.faculty_id, day, slot, availability):
                continue
            # Place
            d.hours_remaining -= 1
            result.append(
                SlotAssignment(day=day, slot=slot, subject_id=d.subject_id, faculty_id=d.faculty_id)
            )
            if solve(cell_index + 1):
                return True
            # Backtrack
            d.hours_remaining += 1
            result.pop()
        # No demand fits this cell; leave empty and continue (valid if total_hours < total_slots)
        return solve(cell_index + 1)

    if solve(0):
        return result
    return None
