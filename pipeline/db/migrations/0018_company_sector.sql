-- Sector bucket columns (doc 10 Sec 12, doc 26 Sec 2.8, doc 28), Company
-- Master follow-on. Pure derivation from core.company.sic_code (already
-- captured, Company Master 4a) -- see
-- company_master/sector_bucket.py for the SIC-range-to-sector mapping
-- and its own documented reasoning.

alter table core.company add column if not exists sector text;
alter table core.company add column if not exists sector_reason text;
