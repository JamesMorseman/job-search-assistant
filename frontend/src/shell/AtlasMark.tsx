import RadarSweepMark from "./RadarSweepMark";

/**
 * Shared ATLAS brand mark: the canonical RadarSweepMark primitive
 * (P7P5H) rendered with the "brand" tier and static motion, per the
 * ATLAS Logo System (Signal Cyan is prohibited inside the primary logo -
 * the mark uses Atlas Blue - and "the logo should not continuously
 * animate"; motion belongs to the product, not the identity). This is a
 * source-code reproduction only - no image asset is used or committed.
 */
export default function AtlasMark({ className }: { className?: string }) {
  return <RadarSweepMark tier="brand" motion="static" className={className} />;
}
