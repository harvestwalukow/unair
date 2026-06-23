import { shape, text } from "@oai/artifact-tool";
import { jsx, jsxs } from "@oai/artifact-tool/presentation-jsx/jsx-runtime";

const COLORS = {
  navy: "#0F2747",
  blue: "#1F5AA6",
  teal: "#0B7A75",
  slate: "#5B6777",
  light: "#F5F7FA",
  line: "#D9E0E8",
  ink: "#1B2430",
  white: "#FFFFFF",
};

const titleStyle = { fontSize: 28, fontWeight: 700, color: COLORS.navy };
const subStyle = { fontSize: 12, color: COLORS.slate };
const sectionStyle = { fontSize: 13, fontWeight: 700, color: COLORS.blue };
const bodyStyle = { fontSize: 14, color: COLORS.ink };
const metricStyle = { fontSize: 23, fontWeight: 700, color: COLORS.navy };
const labelStyle = { fontSize: 11, color: COLORS.slate };

const col = (props, ...children) => jsxs("column", { ...props, children });
const row = (props, ...children) => jsxs("row", { ...props, children });

export async function slide01(presentation, ctx) {
  const slide = presentation.slides.add();
  slide.background.fill = { color: COLORS.white };

  const tree = col(
    { padding: 42, gap: 18 },
    shape({ geometry: "rect", width: 1196, height: 8, fill: { color: COLORS.blue }, line: { color: COLORS.blue } }),
    col(
      { gap: 4 },
      text("AXA Indonesia | Step 5 Loss Ratio & Profitability Review", { style: titleStyle }),
      text("Case study portfolio review | Policy-level aggregation of premium and claim data", { style: subStyle }),
    ),
    col(
      { gap: 6 },
      text(
        "Portfolio remains profitable in nominal underwriting terms, but profitability is uneven and concentrated in a few loss-making pockets.",
        { style: { fontSize: 18, fontWeight: 700, color: COLORS.ink } },
      ),
      text(
        "Net loss ratio at portfolio level is 58.5%, while segment-level stress appears in COB 4, Branch K, Channel B, and Product0221.",
        { style: bodyStyle },
      ),
    ),
    row(
      { gap: 14 },
      col(
        { gap: 4 },
        text("IDR 1.964T", { style: metricStyle }),
        text("Net premium", { style: labelStyle }),
      ),
      col(
        { gap: 4 },
        text("58.54%", { style: metricStyle }),
        text("Portfolio net loss ratio", { style: labelStyle }),
      ),
      col(
        { gap: 4 },
        text("IDR 358.7B", { style: metricStyle }),
        text("Net underwriting result", { style: labelStyle }),
      ),
      col(
        { gap: 4 },
        text("21.77%", { style: metricStyle }),
        text("Premium ceded ratio", { style: labelStyle }),
      ),
    ),
    row(
      { gap: 28 },
      col(
        { gap: 10, width: 560 },
        text("Where value is concentrated", { style: sectionStyle }),
        text("1. Channel D is the strongest scaled segment with 17.60% net loss ratio and IDR 411.4B net underwriting result.", { style: bodyStyle }),
        text("2. COB 3 is the best-performing class with 6.03% net loss ratio, although the policy base is smaller than major classes.", { style: bodyStyle }),
        text("3. Reinsurance provides claim relief in nominal terms, but lower net premium means net loss ratio can still exceed gross loss ratio.", { style: bodyStyle }),
      ),
      shape({ geometry: "rect", width: 2, height: 214, fill: { color: COLORS.line }, line: { color: COLORS.line } }),
      col(
        { gap: 10, width: 560 },
        text("Where management attention is needed", { style: sectionStyle }),
        text("1. COB 4 is loss-making at 106.55% net loss ratio with -IDR 91.7B net underwriting result.", { style: bodyStyle }),
        text("2. Branch K and Channel B are the two largest loss pockets, both above 100% net loss ratio.", { style: bodyStyle }),
        text("3. Product0221 is the most material loss-making product in the filtered ranking at 120.59% net loss ratio.", { style: bodyStyle }),
      ),
    ),
    text("Source: Step 5 notebook result | Large-claim analysis shown separately as sensitivity, not as forecast", {
      style: { fontSize: 10, color: COLORS.slate },
    }),
  );

  slide.compose(tree);
  return slide;
}
