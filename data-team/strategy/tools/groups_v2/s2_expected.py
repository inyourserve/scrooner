"""S2's named results (data-team/strategy/team/S2-group-audit.md sections 3-7) as expected groups for AT-4.1c (symmetric difference check)."""
E = {}
def add(g, s):
    for t in s.split(): E[t] = g
add("insurer", "AFL UNM CINF CNA LNC L PGR TRV GL HIG MTG CB RGA RNR AFG PRU AIZ FNF ESNT FAF PRI VOYA KNSL ACT")
add("managed_care", "HUM UNH CNC ELV MOH CI OSCR")
add("insurance_broker", "MRSH BRO AON AJG RYAN ERIE WTW")
add("asset_manager", "KKR BEN IVZ AMG TROW VCTR BLK SEIC ARES APO BX CG TPG AMP")
add("broker_dealer", "GS MS JEF SF RJF SCHW IBKR SNEX FRHC LPLA HOOD")
add("exchange", "ICE CME NDAQ CBOE TW MKTX")
add("crypto_digital", "COIN CRCL GLXY MSTR IREN HUT WULF BMNR")
add("lender_nonbank", "CACC OMF AFRM RKT")
add("bank", "AXP SYF SOFI CBC")
add("midstream", "WMB OKE ET EPD KMI WES TRGP DTM AM CQP LNG VG MPLX PAA")
add("corporate", "WM RSG CLH CWST WCN MORN EVR HLI")
add("reit_mortgage", "NLY AGNC")
add("reit_equity", "TRNO INVH SBAC AMT CCI EQIX DLR IRM LAMR RYN WY LINE HST RHP")
add("bdc", "ARCC BXSL")
add("energy", "DINO")
add("excluded", "EAI PS XOM")
