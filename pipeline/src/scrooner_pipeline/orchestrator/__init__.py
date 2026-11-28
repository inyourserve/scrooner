"""Pipeline orchestration (PIPELINE.md section 3, merge step M4): event log, planner, resumable workers.

State lives in migration 0136's tables (ops.pipeline_event, ops.work_item, ops.work_item_stage, ops.work_dead_letter,
ops.company_served_version, ops.certify_request). Nothing here is switched on until the founder applies that migration
and sets the repo variable that enables the workflow.
"""
