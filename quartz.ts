import { loadQuartzConfig, loadQuartzLayout } from "./quartz/plugins/loader/config-loader"
import * as ExternalPlugin from "./.quartz/plugins"

// Order the Explorer ("Course map") by file/folder *name* instead of by title,
// so the numeric prefixes (0-toolkit, 1-models-of-computation, 01-…, 02-…) fix
// the order while the visible titles stay clean.
//
// NOTE: this function is serialized with .toString() and re-run in the browser,
// so it must stay self-contained (no imports, no outer variables).
ExternalPlugin.Explorer({
  sortFn: (a, b) => {
    if (a.isFolder !== b.isFolder) {
      return a.isFolder ? -1 : 1
    }
    // practice/: the difficulty and topic lists come first, in this order
    const first: Record<string, number> = { easy: 1, medium: 2, hard: 3, topics: 4 }
    const ra = first[a.slugSegment ?? ""] ?? 99
    const rb = first[b.slugSegment ?? ""] ?? 99
    if (ra !== rb) {
      return ra - rb
    }
    return (a.slugSegment ?? "").localeCompare(b.slugSegment ?? "", undefined, {
      numeric: true,
      sensitivity: "base",
    })
  },
})

const config = await loadQuartzConfig()
export default config
export const layout = await loadQuartzLayout()
