import { shape, text } from "@oai/artifact-tool";
import { jsx, jsxs } from "@oai/artifact-tool/presentation-jsx/jsx-runtime";

const COLORS = {
  navy: "#0F2747",
  blue: "#1F5AA6",
  teal: "#0B7A75",
  slate: "#5B6777",
  line: "#D9E0E8",
  ink: "#1B2430",
  white: "#FFFFFF",
};

const titleStyle = { fontSize: 28, fontWeight: 700, color: COLORS.navy };
const subStyle = { fontSize: 12, color: COLORS.slate };
const sectionStyle = { fontSize: 13, fontWeight: 700, color: COLORS.blue };
const bodyStyle = { fontSize: 13, color: COLORS.ink };
const bigStyle = { fontSize: 25, fontWeight: 700, color: COLORS.navy };

const col = (props, ...children) => jsxs("column", { ...props, children });
const row = (props, ...children) => jsxs("row", { ...props, children });

export async function slide02(presentation, ctx) {
  const slide = presentation.slides.add();
  slide.background.fill = { color: COLORS.white };

  const tree = col(
    { padding: 42, gap: 18 },
    shape({ geometry: "rect", width: 1196, height: 8, fill: { color: COLORS.teal }, line: { color: COLORS.teal } }),
    col(
      { gap: 4 },
      text("Large-claim sensitivity confirms that a small set of segments drives most downside in the portfolio.", { style: titleStyle }),
      text("Management implication: prioritize underwriting remediation and claim governance in the most volatile pockets first.", { style: subStyle }),
    ),
    row(
      { gap: 26 },
      col(
        { gap: 10, width: 560 },
        text("Segment scorecard", { style: sectionStyle }),
        text("Best scale segment", { style: { fontSize: 11, color: COLORS.slate } }),
        text("CHANNEL D | Net LR 17.60% | Net underwriting result IDR 411.4B", { style: bodyStyle }),
        shape({ geometry: "rect", width: 560, height: 1, fill: { color: COLORS.line }, line: { color: COLORS.line } }),
        text("Largest loss pocket", { style: { fontSize: 11, color: COLORS.slate } }),
        text("CHANNEL B | Net LR 116.16% | Net underwriting result -IDR 263.9B", { style: bodyStyle }),
        shape({ geometry: "rect", width: 560, height: 1, fill: { color: COLORS.line }, line: { color: COLORS.line } }),
        text("Most resilient branch", { style: { fontSize: 11, color: COLORS.slate } }),
        text("BRANCH H | Net LR 12.02% | Net underwriting result IDR 21.3B", { style: bodyStyle }),
        shape({ geometry: "rect", width: 560, height: 1, fill: { color: COLORS.line }, line: { color: COLORS.line } }),
        text("Highest-priority class", { style: { fontSize: 11, color: COLORS.slate } }),
        text("COB 4 | Net LR 106.55% | Claim relief only 3.82% of gross claim", { style: bodyStyle }),
        shape({ geometry: "rect", width: 560, height: 1, fill: { color: COLORS.line }, line: { color: COLORS.line } }),
        text("Trend by underwriting year", { style: { fontSize: 11, color: COLORS.slate } }),
        text("2021 was the weakest cohort at 68.77% net LR; 2022 improved materially; 2023 remained above 2022 at 38.24%.", { style: bodyStyle }),
      ),
      col(
        { gap: 12, width: 560 },
        text("Sensitivity to large claims", { style: sectionStyle }),
        text("58.54%  →  5.07%", { style: bigStyle }),
        text("Portfolio net loss ratio if large-claim impact is excluded in a sensitivity scenario", { style: bodyStyle }),
        shape({ geometry: "rect", width: 560, height: 1, fill: { color: COLORS.line }, line: { color: COLORS.line } }),
        text("105.1 ppt", { style: bigStyle }),
        text("Largest net LR reduction occurs in COB 4, improving from 106.55% to 1.43%", { style: bodyStyle }),
        shape({ geometry: "rect", width: 560, height: 1, fill: { color: COLORS.line }, line: { color: COLORS.line } }),
        text("Recommended actions", { style: { fontSize: 13, fontWeight: 700, color: COLORS.navy } }),
        text("1. Tighten underwriting terms and pricing for COB 4, Channel B, and Product0221.", { style: bodyStyle }),
        text("2. Review claim management and case reserving for large-loss cohorts, especially 2021 vintage business.", { style: bodyStyle }),
        text("3. Revisit reinsurance structure for segments with low claim relief despite high downside volatility.", { style: bodyStyle }),
      ),
    ),
    text("Source: Step 5 notebook result | Figures rounded for executive readability", {
      style: { fontSize: 10, color: COLORS.slate },
    }),
  );

  slide.compose(tree);
  return slide;
}
