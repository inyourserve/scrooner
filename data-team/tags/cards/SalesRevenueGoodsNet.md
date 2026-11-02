# Tag card: SalesRevenueGoodsNet

Written 2026-11-02 by the FSN expert. Family: revenue (pre-ASC 606). See cards/revenue.md.

## Meaning
- **What it is:** revenue from goods (products), net of returns and allowances. Pre-ASC 606.
- **Period type:** duration.
- **Balance:** credit.
- **Status:** absent from current taxonomies (revenue.md §1).

## Who uses it
- On the IS face for 39 EDGAR names in our top-100 extract, 2009–2019 (825 lines; DI).
- Labels: "Product" (181), "Product sales" (83), "Products" (76), **"Sales" (60)**.

## How it behaves
- **Usually a component.** MSFT FY2016 10-K 0001193125-16-662209 … Q3 FY2018: "Product" `SalesRevenueGoodsNet` + custom "Service and other" = "Total revenue" `SalesRevenueNet` (calc weight +1 each).
- At a goods-only company labelled "Sales" it can be the total. Only the calc tree tells the two apart.

## Misuse seen
- The FSN pilot (run 41490670432) treats it as a revenue total beside `SalesRevenueNet`, giving `conflicting_values_in_filing` for MSFT FY2014–FY2017 (e.g. 72,948 vs 86,833 for FY2014).
- **Rule:** a revenue candidate that is a calc child of another revenue candidate in the same filing is a component, never the total (PROPOSALS.md P-2).
