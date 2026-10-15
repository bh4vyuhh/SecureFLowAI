"""
SecureFlow AI - Span Conflict Resolution Engine
================================================================================
File: ai-service/app/engine/resolver.py

Negotiates overlapping character index conflicts between deterministic regex rules,
live credentials, and contextual NER entities.
Algorithm: Greedy Interval Merging with strictly enforced enterprise priority:
  PRIORITY: Checksum Rules (CREDIT_CARD, IBAN, SSN, ABA) > Credentials (API_KEY, PRIVATE_KEY) > Contextual NER (PERSON, ORG, LOC).
"""

from typing import List, Dict, Any


# Strictly ordered priority tier (lower number = higher priority)
ENTITY_PRIORITY = {
    # High Priority: Verified Mathematical Checksums & Credentials
    "CREDIT_CARD": 1,
    "IBAN": 1,
    "US_SSN": 1,
    "ABA_ROUTING": 1,
    "PRIVATE_KEY": 2,
    "API_KEY": 2,
    "SWIFT_BIC": 3,
    
    # Secondary Priority: Contextual Tokens
    "PERSON": 4,
    "ORG": 5,
    "LOCATION": 6
}


def spans_overlap(span_a: Dict[str, Any], span_b: Dict[str, Any]) -> bool:
    """
    Returns True if two entity spans overlap in character indices.
    [start_a, end_a) and [start_b, end_b)
    """
    return max(span_a["start"], span_b["start"]) < min(span_a["end"], span_b["end"])


def resolve_entity_conflicts(entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Resolves overlapping span conflicts using greedy interval filtering:
      1. Sort entities by priority (highest priority first), then by span length (longer first).
      2. Keep entities that do not overlap with any previously accepted higher-priority entity.
      3. Sort final non-overlapping entity spans by start offset ascending.
    """
    if not entities:
        return []

    # Sort key:
    # 1. priority rank (ascending: 1 is best)
    # 2. negative span length (longer span first)
    # 3. start index
    def sort_key(ent: Dict[str, Any]):
        prio = ENTITY_PRIORITY.get(ent["entity_type"], 10)
        span_len = ent["end"] - ent["start"]
        return (prio, -span_len, ent["start"])

    sorted_entities = sorted(entities, key=sort_key)
    accepted_entities: List[Dict[str, Any]] = []

    for candidate in sorted_entities:
        has_conflict = False
        for accepted in accepted_entities:
            if spans_overlap(candidate, accepted):
                has_conflict = True
                break
        
        if not has_conflict:
            accepted_entities.append(candidate)

    # Return ordered strictly by character start index
    return sorted(accepted_entities, key=lambda e: (e["start"], e["end"]))
