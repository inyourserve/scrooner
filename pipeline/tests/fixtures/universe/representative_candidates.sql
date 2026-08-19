-- Representative official-source-shaped rows for Day 6 database validation.
-- These exercise policy branches; they are not a claim of a live production
-- universe snapshot.

insert into core.company
    (cik, company_name, status, status_as_of, status_reason, sic_code)
values
    ('0000320193', 'Apple Inc.', 'active', '2026-08-18', 'fixture', '3571'),
    ('0001652044', 'Alphabet Inc.', 'active', '2026-08-18', 'fixture', '7370'),
    ('0001046179', 'Taiwan Semiconductor Manufacturing Co Ltd', 'active', '2026-08-18', 'fixture', '3674'),
    ('0000019617', 'JPMorgan Chase & Co', 'active', '2026-08-18', 'fixture', '6021'),
    ('0001811210', 'Blank Check Candidate', 'active', '2026-08-18', 'fixture', '6770'),
    ('0000884394', 'Registered Fund Candidate', 'active', '2026-08-18', 'fixture', null),
    ('0009000001', 'OTC Candidate', 'active', '2026-08-18', 'fixture', '2834'),
    ('0009000002', 'Stale Candidate', 'stale', '2026-08-18', 'fixture', '7372'),
    ('0009000003', 'Delisted Candidate', 'delisted', '2026-08-18', 'fixture', '2511');

insert into core.listing (company_id, ticker, exchange, security_type, security_type_source)
values
    ((select id from core.company where cik = '0000320193'), 'AAPL', 'Nasdaq', 'Common Stock', 'openfigi'),
    ((select id from core.company where cik = '0001652044'), 'GOOG', 'Nasdaq', 'Common Stock', 'openfigi'),
    ((select id from core.company where cik = '0001652044'), 'GOOGL', 'Nasdaq', 'Common Stock', 'openfigi'),
    ((select id from core.company where cik = '0001046179'), 'TSM', 'NYSE', 'ADR', 'openfigi'),
    ((select id from core.company where cik = '0000019617'), 'JPM', 'NYSE', 'Common Stock', 'openfigi'),
    ((select id from core.company where cik = '0000019617'), 'JPM-PD', 'NYSE', 'Preferred Stock', 'openfigi'),
    ((select id from core.company where cik = '0001811210'), 'SPAC', 'NYSE', 'Common Stock', 'openfigi'),
    ((select id from core.company where cik = '0000884394'), 'FUND', 'NYSE Arca', 'ETP', 'openfigi'),
    ((select id from core.company where cik = '0009000001'), 'OTCC', 'OTC', 'Common Stock', 'openfigi'),
    ((select id from core.company where cik = '0009000002'), 'STALE', 'Nasdaq', 'Common Stock', 'openfigi'),
    ((select id from core.company where cik = '0009000003'), 'GONE', 'NYSE', 'Common Stock', 'openfigi');

insert into core.filing
    (company_id, accession_number, form, filing_date, period_of_report, is_amendment)
values
    ((select id from core.company where cik = '0000320193'), 'fixture-aapl', '10-K', '2026-01-01', '2025-12-31', false),
    ((select id from core.company where cik = '0001652044'), 'fixture-goog', '10-K', '2026-01-01', '2025-12-31', false),
    ((select id from core.company where cik = '0001046179'), 'fixture-tsm', '20-F', '2026-01-01', '2025-12-31', false),
    ((select id from core.company where cik = '0000019617'), 'fixture-jpm', '10-K', '2026-01-01', '2025-12-31', false),
    ((select id from core.company where cik = '0001811210'), 'fixture-spac', '10-K', '2026-01-01', '2025-12-31', false),
    ((select id from core.company where cik = '0000884394'), 'fixture-fund', 'N-1A', '2026-01-01', '2025-12-31', false),
    ((select id from core.company where cik = '0009000001'), 'fixture-otc', '10-K', '2026-01-01', '2025-12-31', false),
    ((select id from core.company where cik = '0009000002'), 'fixture-stale', '10-K', '2023-01-01', '2022-12-31', false),
    ((select id from core.company where cik = '0009000003'), 'fixture-delisted', '10-K', '2023-01-01', '2022-12-31', false);
