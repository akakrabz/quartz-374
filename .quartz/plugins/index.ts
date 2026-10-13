import { componentRegistry } from "../../quartz/components/registry"

export type { NotePropertiesComponentOptions, NotePropertiesOptions } from "@quartz-community/note-properties"
export type { CreatedModifiedDateOptions } from "@quartz-community/created-modified-date"
export type { SyntaxHighlightingOptions } from "@quartz-community/syntax-highlighting"
export type { ObsidianFlavoredMarkdownOptions } from "@quartz-community/obsidian-flavored-markdown"
export type { GfmOptions } from "@quartz-community/github-flavored-markdown"
export type { TableOfContentsTransformerOptions, TocEntry } from "@quartz-community/table-of-contents"
export type { CrawlLinksOptions } from "@quartz-community/crawl-links"
export type { DescriptionOptions } from "@quartz-community/description"
export type { Args, LatexOptions } from "@quartz-community/latex"
export type { ContentDetails, ContentIndexMap } from "@quartz-community/content-index"
export type { FontFileEntry, FontSpecification, GoogleFontFile, ProcessedFontResult, QuartzFontRegistry, FontsOptions } from "@quartz-community/quartz-fonts"
export type { ContentPageOptions, ContentBodyOptions } from "@quartz-community/content-page"
export type { FolderPageOptions } from "@quartz-community/folder-page"
export type { TagPageOptions } from "@quartz-community/tag-page"
export type { SearchField, SearchOptions } from "@quartz-community/search"
export type { ExplorerOptions } from "@quartz-community/explorer"
export type { BreadcrumbOptions } from "@quartz-community/breadcrumbs"
export type { ContentMetaOptions } from "@quartz-community/content-meta"
export type { D3Config, GraphOptions } from "@quartz-community/graph"
export type { BacklinksOptions } from "@quartz-community/backlinks"
export type { FooterOptions } from "@quartz-community/footer"
export { NotePropertiesComponent } from "@quartz-community/note-properties"
export { tokenClassifierTransformer } from "@quartz-community/syntax-highlighting"
export { Spacer } from "@quartz-community/spacer"
export { TableOfContents } from "@quartz-community/table-of-contents"
export { FontsEmitter } from "@quartz-community/quartz-fonts"
export { ContentBody } from "@quartz-community/content-page"
export { FolderPage, FolderContent } from "@quartz-community/folder-page"
export { TagPage, TagContent } from "@quartz-community/tag-page"
export { PageTitle } from "@quartz-community/page-title"
export { Search } from "@quartz-community/search"
export { Darkmode } from "@quartz-community/darkmode"
export { ReaderMode } from "@quartz-community/reader-mode"
export { Explorer } from "@quartz-community/explorer"
export { Breadcrumbs } from "@quartz-community/breadcrumbs"
export { ArticleTitle } from "@quartz-community/article-title"
export { ContentMeta } from "@quartz-community/content-meta"
export { TagList } from "@quartz-community/tag-list"
export { Graph } from "@quartz-community/graph"
export { Backlinks } from "@quartz-community/backlinks"
export { Footer } from "@quartz-community/footer"

export const plugins: Record<string, Record<string, (...args: unknown[]) => void>> = {
  "quartz-community__note-properties": {
    NoteProperties: (...args: unknown[]) => { componentRegistry.setOptionOverrides("quartz-community__note-properties", args[0] as Record<string, unknown>); },
  },
  "quartz-community__created-modified-date": {
    CreatedModifiedDate: (...args: unknown[]) => { componentRegistry.setOptionOverrides("quartz-community__created-modified-date", args[0] as Record<string, unknown>); },
  },
  "quartz-community__syntax-highlighting": {
    SyntaxHighlighting: (...args: unknown[]) => { componentRegistry.setOptionOverrides("quartz-community__syntax-highlighting", args[0] as Record<string, unknown>); },
  },
  "quartz-community__obsidian-flavored-markdown": {
    ObsidianFlavoredMarkdown: (...args: unknown[]) => { componentRegistry.setOptionOverrides("quartz-community__obsidian-flavored-markdown", args[0] as Record<string, unknown>); },
  },
  "quartz-community__github-flavored-markdown": {
    GitHubFlavoredMarkdown: (...args: unknown[]) => { componentRegistry.setOptionOverrides("quartz-community__github-flavored-markdown", args[0] as Record<string, unknown>); },
  },
  "quartz-community__unlisted-pages": {
    UnlistedPages: (...args: unknown[]) => { componentRegistry.setOptionOverrides("quartz-community__unlisted-pages", args[0] as Record<string, unknown>); },
  },
  "quartz-community__table-of-contents": {
    TableOfContentsTransformer: (...args: unknown[]) => { componentRegistry.setOptionOverrides("quartz-community__table-of-contents", args[0] as Record<string, unknown>); },
  },
  "quartz-community__crawl-links": {
    CrawlLinks: (...args: unknown[]) => { componentRegistry.setOptionOverrides("quartz-community__crawl-links", args[0] as Record<string, unknown>); },
  },
  "quartz-community__description": {
    Description: (...args: unknown[]) => { componentRegistry.setOptionOverrides("quartz-community__description", args[0] as Record<string, unknown>); },
  },
  "quartz-community__latex": {
    Latex: (...args: unknown[]) => { componentRegistry.setOptionOverrides("quartz-community__latex", args[0] as Record<string, unknown>); },
  },
  "quartz-community__remove-draft": {
    RemoveDrafts: (...args: unknown[]) => { componentRegistry.setOptionOverrides("quartz-community__remove-draft", args[0] as Record<string, unknown>); },
  },
  "quartz-community__alias-redirects": {
    AliasRedirects: (...args: unknown[]) => { componentRegistry.setOptionOverrides("quartz-community__alias-redirects", args[0] as Record<string, unknown>); },
  },
  "quartz-community__content-index": {
    ContentIndex: (...args: unknown[]) => { componentRegistry.setOptionOverrides("quartz-community__content-index", args[0] as Record<string, unknown>); },
  },
  "quartz-community__favicon": {
    Favicon: (...args: unknown[]) => { componentRegistry.setOptionOverrides("quartz-community__favicon", args[0] as Record<string, unknown>); },
  },
  "quartz-community__quartz-fonts": {
    Fonts: (...args: unknown[]) => { componentRegistry.setOptionOverrides("quartz-community__quartz-fonts", args[0] as Record<string, unknown>); },
  },
  "quartz-community__content-page": {
    ContentPage: (...args: unknown[]) => { componentRegistry.setOptionOverrides("quartz-community__content-page", args[0] as Record<string, unknown>); },
  },
}

export const NoteProperties = plugins["quartz-community__note-properties"].NoteProperties
export const CreatedModifiedDate = plugins["quartz-community__created-modified-date"].CreatedModifiedDate
export const SyntaxHighlighting = plugins["quartz-community__syntax-highlighting"].SyntaxHighlighting
export const ObsidianFlavoredMarkdown = plugins["quartz-community__obsidian-flavored-markdown"].ObsidianFlavoredMarkdown
export const GitHubFlavoredMarkdown = plugins["quartz-community__github-flavored-markdown"].GitHubFlavoredMarkdown
export const UnlistedPages = plugins["quartz-community__unlisted-pages"].UnlistedPages
export const TableOfContentsTransformer = plugins["quartz-community__table-of-contents"].TableOfContentsTransformer
export const CrawlLinks = plugins["quartz-community__crawl-links"].CrawlLinks
export const Description = plugins["quartz-community__description"].Description
export const Latex = plugins["quartz-community__latex"].Latex
export const RemoveDrafts = plugins["quartz-community__remove-draft"].RemoveDrafts
export const AliasRedirects = plugins["quartz-community__alias-redirects"].AliasRedirects
export const ContentIndex = plugins["quartz-community__content-index"].ContentIndex
export const Favicon = plugins["quartz-community__favicon"].Favicon
export const Fonts = plugins["quartz-community__quartz-fonts"].Fonts
export const ContentPage = plugins["quartz-community__content-page"].ContentPage
