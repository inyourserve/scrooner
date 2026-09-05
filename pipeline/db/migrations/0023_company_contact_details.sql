-- Company contact details (2026-08-29 zero-new-fetch coverage pass, items
-- 5/6). Same additive pattern as 0005_company_master_schema.sql -- extends
-- core.company with fields already sitting in each company's already-
-- fetched raw.sec_submissions base payload (ein/addresses/phone), the same
-- source identity.py already parses for sic_code/stateOfIncorporation/etc.
--
-- NOT sourced from XBRL/core.fact: checked live first (2026-08-29) that
-- dei:EntityTaxIdentificationNumber and dei:EntityAddress*/CityAreaCode/
-- LocalPhoneNumber are ALL absent from core.concept entirely (zero rows)
-- -- SEC's bulk Company Facts API (raw.sec_companyfacts, which feeds
-- core.fact/core.concept) only aggregates facts that carry a quantitative
-- unit; these are text-typed dei cover-page fields with no unit, so they
-- never enter that payload at all, not merely filtered out downstream.
-- The real source is the separate submissions.json endpoint
-- (raw.sec_submissions), confirmed live to carry ein/addresses/phone for
-- all 10 golden companies (TSM/ENB correctly show ein="000000000", no
-- real US EIN for a foreign private issuer -- honest, not fabricated).

alter table core.company add column if not exists ein text;
alter table core.company add column if not exists business_address_line1 text;
alter table core.company add column if not exists business_address_city text;
alter table core.company add column if not exists business_address_state text;
alter table core.company add column if not exists business_address_zip text;
alter table core.company add column if not exists business_phone text;
