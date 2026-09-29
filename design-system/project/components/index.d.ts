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
