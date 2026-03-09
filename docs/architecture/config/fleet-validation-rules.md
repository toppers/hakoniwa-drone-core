# Fleet Validation Rules

## Purpose

This document defines the validation rules for the new fleet config format.

The rules are intentionally split into two layers:

- schema checks: shape and required fields
- semantic checks: consistency across fields and files

The goal of Phase 1 is not completeness. The goal is to establish a numbered
rule set that can grow without breaking the structure of the validation design.

## Schema Checks

- `S-001`: The fleet config file must be a JSON object.
- `S-002`: A new-format fleet config must contain both top-level keys `types` and `drones`.
- `S-003`: `types` must be a JSON object.
- `S-004`: `drones` must be a JSON array.
- `S-005`: `drones` must contain at least one entry.
- `S-006`: Each entry in `drones` must be a JSON object.
- `S-007`: The allowed keys for each drone entry are `name`, `type`, `position_meter`, and `angle_degree`.
- `S-008`: Each drone entry must contain all required keys: `name`, `type`, `position_meter`, `angle_degree`.
- `S-009`: `position_meter` must be an array with exactly 3 numeric elements.
- `S-010`: `angle_degree` must be an array with exactly 3 numeric elements.
- `S-011`: Each entry in `types` must map to a string path.

## Semantic Checks

- `V-001`: If the new-format signature is detected, validation failure must be treated as an error. The loader must not fall back to the legacy format.
- `V-002`: Each drone `name` must be non-empty.
- `V-003`: Each drone `name` must be unique within the fleet file.
- `V-004`: Each drone `type` must exist in the `types` map.
- `V-005`: Each type path must be resolvable from the fleet file location.
- `V-006`: Instance-level keys are limited to the Phase 1 whitelist only. No ad hoc overrides are allowed.
- `V-007`: Each key in `types` must be non-empty.
- `V-008`: Each path value in `types` must be non-empty.
- `V-010`: Each numeric value in `position_meter` and `angle_degree` must be finite.

## Growth Policy

- New rules should be appended with new rule numbers.
- Existing rule numbers should remain stable once published.
- Schema rules should remain minimal.
- New validation effort should focus first on semantic consistency rather than broadening schema shape checks.

## Relationship To Other Documents

- Structural format: `fleet-schema.md`
- Path resolution rules: `fleet-path-resolver.md`
- Internal loading design: `fleet-internal-design.md`
- Validator implementation notes: `fleet-validator.md`
