select 'concept' kind, name, combination_mode from analytics.canonical_concept
union all select 'metric', metric_name, status from analytics.metric_definition
