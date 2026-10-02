// Slice 8: the four Music components as SwiftUI, compiled against the REAL
// generated tokens.
//
// Every component in App Kit before this one shipped a SwiftUI recipe in its
// README; Shelf, HeroCard, TrackList and MiniPlayer shipped CSS only, which is
// backwards for a system whose stated target is SwiftUI apps on the Mac.
//
// This file is the source of those recipes, not a copy of them: the README
// snippets are lifted from here AFTER it compiles and renders, so a recipe that
// does not build cannot reach the docs.
//
//   swiftc build/source/music-components-spike.swift swift/AppKit.swift -o <bin>
//   <bin> --selfshot <out.png>
//
// It compiles against swift/AppKit.swift rather than redeclaring the measured
// values, which also makes it the first check that the generated Swift builds.

import AppKit
import SwiftUI

// MARK: - ArtworkCard

/// Square artwork over a caption block of CONSTANT height. Card height minus
/// card width measured 37pt at every width, so the caption does not scale.
struct ArtworkCard: View {
    let art: Color
    let title: String
    let subtitle: String
    var width: CGFloat = 188
    var action: () -> Void = {}

    var body: some View {
        Button(action: action) { card }
            .buttonStyle(.plain)
            // One label for the pair: VoiceOver should say "Episode 740,
            // Soulection playgroup", not read two separate static texts.
            .accessibilityElement(children: .ignore)
            .accessibilityLabel("\(title), \(subtitle)")
            .accessibilityAddTraits(.isButton)
    }

    private var card: some View {
        VStack(alignment: .leading, spacing: 0) {
            RoundedRectangle(cornerRadius: 6, style: .continuous)
                .fill(art)
                .frame(width: width, height: width)   // square
            VStack(alignment: .leading, spacing: 0) {
                Text(title).font(.footnote).foregroundStyle(Color.Kit.musicInk)
                    .lineLimit(1)
                Text(subtitle).font(.caption2).foregroundStyle(Color.Kit.musicInkSoft)
                    .lineLimit(1)
            }
            .padding(.top, 6)
            .frame(height: 37, alignment: .top)       // constant, not derived
        }
        .frame(width: width)
    }
}

// MARK: - HeroCard

/// Full-bleed artwork at 3:4 with the caption INSIDE the card. The ratio is the
/// spec; the size is not.
struct HeroCard: View {
    let art: LinearGradient
    let eyebrow: String
    let title: String
    var width: CGFloat = 258
    var action: () -> Void = {}

    var body: some View {
        Button(action: action) { card }
            .buttonStyle(.plain)
            .accessibilityElement(children: .ignore)
            .accessibilityLabel("\(eyebrow), \(title)")
            .accessibilityAddTraits(.isButton)
    }

    private var card: some View {
        ZStack(alignment: .bottomLeading) {
            art
            // The scrim is ours, not Music's: Music's heroes are commissioned to
            // carry white text, an adopting app's artwork is not.
            LinearGradient(stops: [
                .init(color: .black.opacity(0.78), location: 0.00),
                .init(color: .black.opacity(0.70), location: 0.16),
                .init(color: .black.opacity(0.30), location: 0.34),
                .init(color: .black.opacity(0.00), location: 0.56),
            ], startPoint: .bottom, endPoint: .top)
            VStack(alignment: .leading, spacing: 2) {
                Text(eyebrow).font(.caption2).foregroundStyle(.white.opacity(0.82))
                Text(title).font(.system(size: 15, weight: .semibold)).foregroundStyle(.white)
                    .lineLimit(1)
            }
            .padding(18)
        }
        .frame(width: width, height: width / 0.75)    // 3:4
        .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
    }
}

// MARK: - Shelf

/// A horizontally scrolling row. The shelf owns the GAP; the card owns its size.
struct Shelf<Content: View>: View {
    let title: String
    var compact: Bool = false
    /// Leading inset of the content column: 40pt, the same line TrackList's
    /// pill starts on, measured from the Music window.
    var inset: CGFloat = 40
    var onMore: () -> Void = {}
    @ViewBuilder var content: Content

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(spacing: 6) {
                Text(title).font(.title3.bold()).foregroundStyle(Color.Kit.musicInk)
                Button(action: onMore) {
                    Image(systemName: "chevron.right")
                        .font(.system(size: 12, weight: .semibold))
                        .foregroundStyle(Color.Kit.musicInkSoft)
                }
                .buttonStyle(.plain)
                .accessibilityLabel("See all \(title)")
            }
            .padding(.leading, inset)
            ScrollView(.horizontal, showsIndicators: false) {
                // 20pt wide, 16pt once the window narrows. A breakpoint, not a scale.
                HStack(alignment: .top, spacing: compact ? 16 : 20) { content }
                    .scrollTargetLayout()
            }
            .scrollTargetBehavior(.viewAligned)       // the snap Music has
            // The cards rest 40pt in, level with TrackList's pill, but scroll
            // all the way under the edge -- which contentMargins gives and a
            // plain .padding does not.
            .contentMargins(.horizontal, inset, for: .scrollContent)
        }
    }
}

// MARK: - TrackList

struct Track: Identifiable {
    let id: Int
    let starred: Bool
    let art: Color
    let song: String
    let artist: String
    let time: String
}

/// Music's song table. The highlight is a rounded inset PILL, not a row fill.
struct TrackList: View {
    let rows: [Track]
    @Binding var selection: Int?
    var windowInactive: Bool = false
    var onPlay: (Int) -> Void = { _ in }
    @FocusState private var focused: Bool

    private func fill(_ id: Int) -> Color {
        guard id == selection else { return .clear }
        return windowInactive ? Color.Kit.musicSelectInactive : Color.Kit.musicSelect
    }
    private func ink(_ id: Int, soft: Bool) -> Color {
        if id == selection && !windowInactive { return Color.Kit.onMusicSelect }
        if id == selection && windowInactive { return soft ? Color.Kit.musicInkSoftOnFill : Color.Kit.musicInk }
        return soft ? Color.Kit.musicInkSoft : Color.Kit.musicInk
    }

    var body: some View {
        VStack(spacing: 0) {
            ForEach(rows) { r in
                HStack(spacing: 12) {
                    Text(r.starred ? "\u{2605}" : " ")
                        .foregroundStyle(Color.Kit.warn).frame(width: 16)
                    RoundedRectangle(cornerRadius: 4, style: .continuous)
                        .fill(r.art).frame(width: 40, height: 40)
                    Text(r.song).foregroundStyle(ink(r.id, soft: false))
                    Spacer()
                    Text(r.artist).foregroundStyle(ink(r.id, soft: true))
                        .frame(width: 160, alignment: .leading)
                    Text(r.time).foregroundStyle(ink(r.id, soft: true))
                        .monospacedDigit().frame(width: 48, alignment: .trailing)
                }
                .font(.subheadline)
                .padding(.horizontal, 12)
                // 45pt pill inside a 56pt row: 5.5pt above and below.
                .frame(height: 45)
                .background(RoundedRectangle(cornerRadius: 6, style: .continuous).fill(fill(r.id)))
                .padding(.horizontal, 40)   // the measured inset
                .frame(height: 56)
                .contentShape(Rectangle())
                .onTapGesture { selection = r.id }
                .accessibilityElement(children: .combine)
                .accessibilityAddTraits(r.id == selection ? [.isSelected] : [])
            }
        }
        // One focus target for the whole table, with the arrows moving inside
        // it -- a row-per-tab-stop would be 200 stops on a real playlist. This
        // mirrors the keyboard model the web component documents.
        .focusable()
        .focused($focused)
        .onMoveCommand { direction in
            guard let current = selection ?? rows.first?.id,
                  let i = rows.firstIndex(where: { $0.id == current }) else { return }
            switch direction {
            case .up:   selection = rows[max(0, i - 1)].id
            case .down: selection = rows[min(rows.count - 1, i + 1)].id
            default:    break
            }
        }
        // Return plays, which is what Music does.
        .onKeyPress(.return) {
            if let s = selection { onPlay(s); return .handled }
            return .ignored
        }
        .accessibilityLabel("Tracks")
    }
}

// MARK: - SidebarList

/// A Mac source list with Music's RED selection, which is the part
/// `.listStyle(.sidebar)` will not give you: sidebar selection draws the system
/// accent and `.tint()` does not override it (measured: #007AFF against a tint
/// of #CC132D). So the rows draw their own background and the List supplies
/// only the vibrancy.
struct SidebarRow: Identifiable {
    let id: String
    let label: String
    let symbol: String
}

struct SidebarList: View {
    let sections: [(String?, [SidebarRow])]
    @Binding var selection: String?
    var windowInactive: Bool = false

    private func fill(_ id: String) -> Color {
        guard id == selection else { return .clear }
        return windowInactive ? Color.Kit.musicSelectInactive : Color.Kit.musicSelect
    }
    private func ink(_ id: String) -> Color {
        id == selection && !windowInactive ? Color.Kit.onMusicSelect : Color.Kit.musicInk
    }
    /// Music tints the SYMBOL and leaves the label in normal ink, which is why
    /// the row is built from Text and Image rather than a Label: a
    /// .foregroundStyle on a Label would tint both.
    private func glyph(_ id: String) -> Color {
        if id == selection { return windowInactive ? Color.Kit.musicInkSoftOnFill : Color.Kit.onMusicSelect }
        return Color.Kit.musicAccent
    }

    var body: some View {
        List(selection: $selection) {
            ForEach(sections.indices, id: \.self) { i in
                let (header, rows) = sections[i]
                Section {
                    ForEach(rows) { r in
                        HStack(spacing: 8) {
                            Image(systemName: r.symbol)
                                .foregroundStyle(glyph(r.id)).frame(width: 16)
                            Text(r.label).foregroundStyle(ink(r.id))
                            Spacer(minLength: 0)
                        }
                        .frame(height: 32)                       // measured
                        .padding(.horizontal, 8)
                        .background(RoundedRectangle(cornerRadius: 6, style: .continuous).fill(fill(r.id)))
                        .listRowInsets(EdgeInsets())
                        .listRowBackground(Color.clear)          // let the row's own fill show
                        .tag(r.id)
                    }
                } header: {
                    if let header { Text(header).foregroundStyle(Color.Kit.musicInkSoft) }
                }
            }
        }
        .listStyle(.sidebar)        // the vibrancy; set NO background
        .scrollContentBackground(.hidden)
    }
}

// MARK: - MiniPlayer

/// The floating transport capsule: 700x54, stadium radius, real material.
struct MiniPlayer: View {
    let art: Color
    let title: String
    let subtitle: String
    var progress: Double = 0.54
    var playing: Bool = true
    var shuffle: Bool = false
    var repeatOn: Bool = false
    var onPlayPause: () -> Void = {}
    var onPrevious: () -> Void = {}
    var onNext: () -> Void = {}
    var onShuffle: () -> Void = {}
    var onRepeat: () -> Void = {}
    var onLyrics: () -> Void = {}
    var onQueue: () -> Void = {}
    var onVolume: () -> Void = {}

    private func control(_ symbol: String, _ label: String, _ act: @escaping () -> Void) -> some View {
        Button(action: act) {
            Image(systemName: symbol).foregroundStyle(Color.Kit.musicInk)
        }
        .buttonStyle(.plain)
        .accessibilityLabel(label)
    }

    /// A toggle says whether it is ON, which a plain button cannot. The accent
    /// is the only visual signal otherwise, so without this the state is
    /// colour-only and invisible to VoiceOver.
    private func toggle(_ symbol: String, _ label: String, _ on: Bool,
                        _ act: @escaping () -> Void) -> some View {
        Button(action: act) {
            Image(systemName: symbol)
                .foregroundStyle(on ? Color.Kit.musicAccent : Color.Kit.musicInk)
        }
        .buttonStyle(.plain)
        .accessibilityLabel(label)
        .accessibilityValue(on ? "On" : "Off")
        .accessibilityAddTraits(on ? [.isSelected] : [])
    }

    var body: some View {
        HStack(spacing: 11) {
            toggle("shuffle", "Shuffle", shuffle, onShuffle)
            control("backward.fill", "Previous", onPrevious)
            control(playing ? "pause.fill" : "play.fill", playing ? "Pause" : "Play", onPlayPause)
            control("forward.fill", "Next", onNext)
            toggle("repeat", "Repeat", repeatOn, onRepeat)

            ZStack(alignment: .bottom) {
                Color.clear.frame(height: 54)   // the line belongs to the CAPSULE's edge
                HStack(spacing: 8) {
                    RoundedRectangle(cornerRadius: 3, style: .continuous)
                        .fill(art).frame(width: 34, height: 34)
                    VStack(alignment: .leading, spacing: 2) {
                        Text(title).font(.system(size: 15, weight: .semibold))
                            .foregroundStyle(Color.Kit.musicInk)
                        Text(subtitle).font(.footnote).foregroundStyle(Color.Kit.musicInkSoft)
                    }
                    Spacer()
                }
                .frame(height: 54)
                GeometryReader { g in
                    ZStack(alignment: .leading) {
                        Capsule().fill(Color.Kit.musicInkSoft.opacity(0.35))
                        Capsule().fill(Color.Kit.musicInkSoft)
                            .frame(width: g.size.width * progress)
                    }
                }
                .frame(height: 1).padding(.bottom, 2)
                .accessibilityElement()
                .accessibilityLabel("Playback position")
                .accessibilityValue("\(Int(progress * 100)) percent")
            }

            HStack(spacing: 14) {
                control("quote.bubble", "Lyrics", onLyrics)
                control("list.bullet", "Queue", onQueue)
                control("speaker.wave.2.fill", "Volume", onVolume)
            }
        }
        .padding(.leading, 15).padding(.trailing, 20)
        .frame(width: 700, height: 54)
        .background(.regularMaterial, in: Capsule())
        .overlay(Capsule().strokeBorder(.white.opacity(0.12), lineWidth: 0.5))
        .shadow(color: .black.opacity(0.18), radius: 12, y: 4)
    }
}

// MARK: - Spike window

struct SpikeView: View {
    @State private var selection: Int? = 2
    private let tracks = [
        Track(id: 1, starred: true,  art: Color(red: 0.79, green: 0.28, blue: 0.18), song: "Nights",       artist: "Frank Ocean", time: "5:07"),
        Track(id: 2, starred: false, art: Color(red: 0.18, green: 0.43, blue: 0.79), song: "Solo",         artist: "Frank Ocean", time: "4:17"),
        Track(id: 3, starred: false, art: Color(red: 0.18, green: 0.60, blue: 0.43), song: "Pink + White", artist: "Frank Ocean", time: "3:04"),
    ]
    private func grad(_ a: Color, _ b: Color) -> LinearGradient {
        LinearGradient(colors: [a, b], startPoint: .topLeading, endPoint: .bottomTrailing)
    }

    @State private var navSelection: String? = "Home"
    private let nav: [(String?, [SidebarRow])] = [
        (nil, [SidebarRow(id: "Search", label: "Search", symbol: "magnifyingglass"),
               SidebarRow(id: "Home", label: "Home", symbol: "house.fill"),
               SidebarRow(id: "New", label: "New", symbol: "square.grid.2x2"),
               SidebarRow(id: "Radio", label: "Radio", symbol: "dot.radiowaves.left.and.right")]),
        ("Library", [SidebarRow(id: "Songs", label: "Songs", symbol: "music.note"),
                     SidebarRow(id: "Albums", label: "Albums", symbol: "square.stack"),
                     SidebarRow(id: "Artists", label: "Artists", symbol: "music.mic")]),
    ]

    var body: some View {
        NavigationSplitView {
            SidebarList(sections: nav, selection: $navSelection)
                .navigationSplitViewColumnWidth(min: 180, ideal: 260)
        } detail: {
        ZStack(alignment: .bottom) {
            ScrollView {
                VStack(alignment: .leading, spacing: 28) {
                    Shelf(title: "Top Picks for You") {
                        HeroCard(art: grad(Color(red: 1, green: 0.37, blue: 0.23), Color(red: 1, green: 0.70, blue: 0.0)),
                                 eyebrow: "Made for You", title: "Daniel Decena's Station")
                        HeroCard(art: grad(Color(red: 0.17, green: 0.33, blue: 0.39), Color(red: 0.06, green: 0.13, blue: 0.15)),
                                 eyebrow: "Updated Playlist", title: "New Music Mix")
                        HeroCard(art: grad(Color(red: 0.56, green: 0.18, blue: 0.89), Color(red: 0.29, green: 0.0, blue: 0.88)),
                                 eyebrow: "Station", title: "Soulection Radio")
                    }
                    Shelf(title: "Recently Played") {
                        ArtworkCard(art: Color(red: 0.76, green: 0.23, blue: 0.23), title: "Episode 740", subtitle: "Soulection playgroup")
                        ArtworkCard(art: Color(red: 0.55, green: 0.33, blue: 0.70), title: "Episode 741", subtitle: "Soulection playgroup")
                        ArtworkCard(art: Color(red: 0.20, green: 0.49, blue: 0.45), title: "Episode 743", subtitle: "Soulection playgroup")
                        ArtworkCard(art: Color(red: 0.78, green: 0.29, blue: 0.11), title: "Episode 745", subtitle: "Soulection playgroup")
                    }
                    VStack(alignment: .leading, spacing: 0) {
                        Text("Playlist").font(.title3.bold())
                            .foregroundStyle(Color.Kit.musicInk).padding(.leading, 40)
                        TrackList(rows: tracks, selection: $selection)
                    }
                    Color.clear.frame(height: 80)
                }
                .padding(.vertical, 28)
                .frame(maxWidth: .infinity, alignment: .leading)
            }
            MiniPlayer(art: Color(red: 0.79, green: 0.28, blue: 0.18),
                       title: "Nights", subtitle: "Frank Ocean \u{2014} Blonde", shuffle: true)
                .padding(.bottom, 19)
        }
        .background(Color.Kit.groundWindow)
        }
    }
}

// Top-level code is only allowed in main.swift, and this file is compiled
// alongside swift/AppKit.swift, so the launcher lives in @main instead.
@main
enum SpikeMain {
    static func main() {
        let app = NSApplication.shared
        app.setActivationPolicy(.regular)
        let win = NSWindow(contentRect: NSRect(x: 120, y: 120, width: 1180, height: 980),
                           styleMask: [.titled, .closable, .resizable, .fullSizeContentView],
                           backing: .buffered, defer: false)
        win.title = "App Kit Music components"
        win.titlebarAppearsTransparent = true
        win.contentView = NSHostingView(rootView: SpikeView())
        // Both appearances, because dyn() tokens are only half-verified by one.
        if CommandLine.arguments.contains("--light") {
            app.appearance = NSAppearance(named: .aqua)
            win.appearance = NSAppearance(named: .aqua)
        }
        win.makeKeyAndOrderFront(nil)
        app.activate(ignoringOtherApps: true)

        if CommandLine.arguments.contains("--selfshot") {
            let out = CommandLine.arguments.last ?? "/tmp/components.png"
            DispatchQueue.main.asyncAfter(deadline: .now() + 1.2) {
                NSApp.activate(ignoringOtherApps: true)
                win.makeKeyAndOrderFront(nil)
                DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
                    let key = win.isKeyWindow, active = NSApp.isActive
                    let p = Process()
                    p.executableURL = URL(fileURLWithPath: "/usr/sbin/screencapture")
                    p.arguments = ["-o", "-x", "-l", String(win.windowNumber), out]
                    try? p.run(); p.waitUntilExit()
                    FileHandle.standardError.write("isKeyWindow=\(key) isActive=\(active) wrote=\(out)\n".data(using: .utf8)!)
                    NSApp.terminate(nil)
                }
            }
        }
        app.run()
    }
}
