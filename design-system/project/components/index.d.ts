import type { ReactNode, ButtonHTMLAttributes } from "react";

/** Action button, an iOS 26 capsule. `tinted` (translucent) is the default; `filled` at most once per view. */
export function Button(props: ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "tinted" | "filled" | "gray" | "plain" | "glass" | "destructive" | "primary" | "secondary";
  /** The Notes highlight colours; accent by default. */
  tint?: "accent" | "purple" | "pink" | "orange" | "mint" | "blue";
  children: ReactNode;
}): JSX.Element;

/** Toggleable filter pill with an optional count. */
export function FilterPill(props: ButtonHTMLAttributes<HTMLButtonElement> & {
  selected?: boolean;
  count?: number | string;
  children: ReactNode;
}): JSX.Element;

/** 2 to 5 mutually exclusive views of the same content. */
export function SegmentedControl(props: {
  options: Array<string | { value: string; label: ReactNode }>;
  value?: string;
  defaultValue?: string;
  onChange?: (value: string) => void;
  label: string;
}): JSX.Element;

/** Short uppercase metadata tag. */
export function Badge(props: {
  tone?: "neutral" | "hollow" | "accent" | "ok" | "warn" | "bad";
  children: ReactNode;
}): JSX.Element;

/** Inline status callout with a glyph and a sentence. */
export function Flag(props: { tone?: "warn" | "bad" | "accent"; children: ReactNode }): JSX.Element;

/** One figure with a mono key, optional unit and 0..1 meter. */
export function StatTile(props: {
  label: string;
  value: ReactNode;
  unit?: string;
  meter?: number;
  attention?: boolean;
}): JSX.Element;

/** A surface grouping related content on the ground. */
/** Detail card: uppercase caption title, surface one step off the ground. `tone` marks a slot: `act` needs the person, `live` is working, `empty` has nothing yet. */
export function Panel(props: { title?: ReactNode; meta?: ReactNode; tone?: "plain" | "act" | "live" | "empty"; children?: ReactNode }): JSX.Element;
/** One label and value row, inside `<dl className="dc-facts">`. A null or empty value reads "not recorded" in ink-faint. */
export function Fact(props: { label: ReactNode; value?: string | number | null; muted?: boolean; oneLine?: boolean }): JSX.Element;
/** Spaced mono capitals naming a figure or a slot; `act` when it needs the person. */
export function Eyebrow(props: { act?: boolean; children: ReactNode }): JSX.Element;
export interface ToolbarTool {
  /** The tooltip and accessible name. */
  title: string;
  icon: ReactNode;
  onClick?: () => void;
  /** Why the tool is unavailable; replaces the tooltip. */
  disabled?: string;
}
/** One row pinned above scrolling content: search, icon tools, one filled primary action, and a notice after an action. */
export function Toolbar(props: {
  searchLabel?: string;
  query?: string;
  onQueryChange?: (query: string) => void;
  tools?: ToolbarTool[];
  /** One filled Button. */
  primary?: ReactNode;
  notice?: ReactNode;
  noticeTone?: "neutral" | "bad";
  /** Leading controls, such as a SegmentedControl. */
  children?: ReactNode;
}): JSX.Element;
export interface SidebarItem {
  id: string;
  label: string;
  /** An SF-Symbol-shaped glyph, tinted music-accent. Omit when using thumb. */
  icon?: ReactNode;
  /** Artwork for playlist rows, which take a thumbnail instead of a glyph. */
  thumb?: string;
}
export interface SidebarSection {
  label?: string;
  /** A trailing text action on the section header, e.g. "Edit". */
  action?: string;
  onAction?: () => void;
  items: SidebarItem[];
}
/** A square artwork over a caption block of constant height. The caption does NOT scale with the card: measured 37pt at every width. Pass width; do not assume a fixed size, it tracks the available space in the real app. */
export function ArtworkCard(props: {
  art: string;
  title: string;
  subtitle?: string;
  /** Card width in px. The artwork is square and the caption adds 37px. */
  width?: number;
  onClick?: () => void;
  className?: string;
}): JSX.Element;
/** A horizontally scrolling row of cards with a title and an optional "see all". Owns the GAP (20px, 16px when compact) and lets the card own its size. Arrow keys scroll by one card pitch. */
export function Shelf(props: {
  title: string;
  onMore?: () => void;
  /** 16px gap instead of 20px. Music switches at a narrow window; where exactly is unmeasured. */
  compact?: boolean;
  children?: ReactNode;
  className?: string;
}): JSX.Element;
/** Full-bleed artwork at 3:4 with the caption over it. The ratio is the spec, not a size: measured 0.751 / 0.748 / 0.748 across three window widths. Carries a built-in bottom scrim so white text clears AA over any artwork. */
export function HeroCard(props: {
  art: string;
  title: string;
  /** A line above the title, e.g. "Made for You". */
  eyebrow?: string;
  /** Top-right slot, over the art with NO scrim -- it must be legible unaided. */
  badge?: ReactNode;
  /** A colour the app derived from the artwork. Shows while the art loads and behind a transparent one; nothing here reads the image. */
  tone?: string;
  /** Card width in px; height derives as width / 0.75. */
  width?: number;
  onClick?: () => void;
  className?: string;
}): JSX.Element;
export interface TrackColumn {
  key: string;
  /** Header text. Omit on every column to drop the header row. */
  label?: string;
  /** A grid track size: "40px", "1fr", "2fr". */
  width?: string;
  /** Render in ink-soft -- artist, time, and other secondary columns. */
  soft?: boolean;
  align?: "start" | "end";
  render?: (row: any) => ReactNode;
}
/** Music's song table: 56px rows whose highlight is a rounded pill inset 40px each side, NOT a full-bleed row fill. Columns are configuration; the measured playlist had seven and no Album. */
export function TrackList(props: {
  rows: Array<Record<string, any> & { id?: string | number }>;
  columns: TrackColumn[];
  selection?: string | number;
  onSelect?: (id: string | number) => void;
  onPlay?: (id: string | number) => void;
  /** Renders the grey inactive selection fill, as macOS does when the window is not key. */
  windowInactive?: boolean;
  label?: string;
  className?: string;
}): JSX.Element;
/** The floating glass transport capsule, 700x54 with a stadium radius. It floats over content, 19px up, centred on the CONTENT area and not the window. Presentation only: it reports playback, it does not own it. */
export function MiniPlayer(props: {
  art: string;
  title: string;
  subtitle?: string;
  favorite?: boolean;
  /** 0..1. Drives the hairline under the now-playing group. */
  progress?: number;
  playing?: boolean;
  shuffle?: boolean;
  repeat?: boolean;
  onPlayPause?: () => void;
  onPrev?: () => void;
  onNext?: () => void;
  onShuffle?: () => void;
  onRepeat?: () => void;
  /** Trailing icon cluster: lyrics, queue, volume. */
  actions?: ReactNode;
  /** Replace the text-glyph fallbacks with real SF Symbols. */
  playGlyph?: ReactNode;
  pauseGlyph?: ReactNode;
  prevGlyph?: ReactNode;
  nextGlyph?: ReactNode;
  shuffleGlyph?: ReactNode;
  repeatGlyph?: ReactNode;
  favoriteGlyph?: ReactNode;
  /** Capsule width in px; 700 by default, the measured value. */
  width?: number;
  className?: string;
}): JSX.Element;
/** A Mac source list: 32pt rows, 19pt section headers, a rounded selection fill. Pass windowInactive when the window is not key -- a monitor app is in that state most of the time. */
export function SidebarList(props: {
  sections: SidebarSection[];
  selection?: string;
  onSelect?: (id: string) => void;
  /** Renders the inactive selection fill, as macOS does when the window is not key. */
  windowInactive?: boolean;
  footer?: ReactNode;
  label?: string;
  className?: string;
}): JSX.Element;

/** Selectable row with optional thumbnail and trailing value. Place inside a `.dc-list` with role="listbox". */
export function ListRow(props: ButtonHTMLAttributes<HTMLButtonElement> & {
  title: ReactNode;
  subtitle?: ReactNode;
  trailing?: ReactNode;
  thumb?: ReactNode;
  selected?: boolean;
}): JSX.Element;

/** Inline text highlight in one of Apple Notes' five colours. */
export function Highlight(props: { color?: "purple" | "pink" | "orange" | "mint" | "blue"; children: ReactNode }): JSX.Element;

/** Bar chart, stacked when a row carries several values. Y axis on the trailing edge, starting at zero. */
export function BarChart(props: {
  data: Array<{ label: string; value?: number; values?: number[] }>;
  series?: Array<{ name: string }>;
  title?: string;
  /** The chart's main message in one sentence. Also its accessibility label. */
  summary?: string;
  unit?: string;
  /** Emphasis mode: the label(s) of the bar(s) that make the point. They take `color`, every other bar `chart-base`, and each bar shows its value. */
  highlight?: string | string[];
  /** Series slot for the highlighted bars, 1 (mint) to 5 (orange). Default 1. */
  color?: 1 | 2 | 3 | 4 | 5;
  /** Legend names in emphasis mode. */
  highlightName?: string;
  restName?: string;
}): JSX.Element;
