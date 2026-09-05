import { backendUrl, proxyBackend } from "@/lib/backend";
import { requireApiUser } from "@/lib/auth/require-user";

export const revalidate = 3600;

const PRESENTATION_OVERRIDES: Record<string, { display_name: string; short_definition: string; category: string; value_type: string }> = {
  dps_growth_3y_cagr: { display_name: "Dividend growth (3-year CAGR)", short_definition: "Annualized growth in dividends per share over the latest three-year period.", category: "Dividends", value_type: "percentage" },
  dps_growth_yoy: { display_name: "Dividend growth (year over year)", short_definition: "Change in dividends per share compared with the prior year.", category: "Dividends", value_type: "percentage" },
  net_cash: { display_name: "Net cash", short_definition: "Cash and cash equivalents minus total debt for the latest reported period.", category: "Balance sheet", value_type: "currency" },
  net_cash_per_share: { display_name: "Net cash per share", short_definition: "Net cash divided by diluted shares outstanding.", category: "Balance sheet", value_type: "currency" },
  payout_ratio: { display_name: "Dividend payout ratio", short_definition: "Dividends per share as a percentage of earnings per share.", category: "Dividends", value_type: "percentage" },
  pretax_margin: { display_name: "Pretax margin", short_definition: "Income before tax as a percentage of revenue.", category: "Profitability", value_type: "percentage" },
};

export async function GET() {
  const unauthorized = await requireApiUser();
  if (unauthorized) return unauthorized;
  const response = await proxyBackend(
    fetch(backendUrl("/v1/metrics"), {
      next: { revalidate: 3600 },
      headers: { accept: "application/json" },
    }),
  );
  const cacheControl = "private, max-age=300";
  if (!response.ok) {
    response.headers.set("Cache-Control", cacheControl);
    return response;
  }

  const payload: unknown = await response.json();
  const metrics = Array.isArray(payload)
    ? payload.map((metric) => {
        if (!metric || typeof metric !== "object" || !("metric_name" in metric)) return metric;
        const override = PRESENTATION_OVERRIDES[String(metric.metric_name)];
        return override ? { ...metric, ...override } : metric;
      })
    : payload;
  return Response.json(metrics, { headers: { "Cache-Control": cacheControl } });
}
