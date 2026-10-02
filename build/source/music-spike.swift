// Slice 2 spike: does ground-window sit right against a REAL vibrant sidebar?
//
// A CSS preview cannot answer this. `glass` is a backdrop-filter stand-in that
// samples the page, while a macOS sidebar samples the desktop behind the window.
// So the sidebar must be judged in a real SwiftUI window, which is all this is.
//
// Deliberately standalone: Spinner carries no App Kit Swift tokens, and coupling
// two repos for a throwaway is worse than hardcoding eleven measured values.
//
//   swift build/source/music-spike.swift
//
// Values are the measured sRGB from build/source/music-capture.md.

import AppKit
import SwiftUI

extension Color {
    // (light, dark) -- the same order App Kit's generated dyn() helper uses.
    static func dyn(_ l: String, _ d: String) -> Color {
        func rgb(_ h: String) -> (Double, Double, Double) {
            let v = h.dropFirst()
            func c(_ i: Int) -> Double {
                let s = v.index(v.startIndex, offsetBy: i)
                let e = v.index(s, offsetBy: 2)
                return Double(Int(v[s..<e], radix: 16)!) / 255
            }
            return (c(0), c(2), c(4))
        }
        return Color(nsColor: NSColor(name: nil) { appearance in
            let (r, g, b) = rgb(appearance.bestMatch(from: [.darkAqua, .aqua]) == .darkAqua ? d : l)
            return NSColor(srgbRed: r, green: g, blue: b, alpha: 1)
        })
    }
    static let groundWindow = dyn("#FFFFFF", "#1F1F20")
    static let musicInk = dyn("#272727", "#DDDDDD")
    static let musicInkSoft = dyn("#767676", "#9A9A9A")
    static let musicAccent = dyn("#FA233B", "#FA2E48")
    static let musicSelect = dyn("#DC1229", "#CC132D")
    static let musicHover = dyn("#F0F0F0", "#2C2C2D")
}

struct MiniPlayerSpike: View {
    var body: some View {
        HStack(spacing: 11) {
            ForEach(["shuffle", "backward.fill", "pause.fill", "forward.fill", "repeat"], id: \.self) {
                Image(systemName: $0).foregroundStyle(Color.musicInk)
            }
            ZStack(alignment: .bottom) {
                // The line belongs to the capsule's bottom edge, not the text's,
                // so this stack has to be the full 54 tall and the text centred
                // inside it. First attempt let the text set the height and the
                // line struck through the subtitle.
                Color.clear.frame(height: 54)
                HStack(spacing: 8) {
                    RoundedRectangle(cornerRadius: 3).fill(Color(red: 0.79, green: 0.28, blue: 0.18))
                        .frame(width: 34, height: 34)
                    VStack(alignment: .leading, spacing: 2) {
                        Text("Nights").font(.system(size: 15, weight: .semibold))
                            .foregroundStyle(Color.musicInk)
                        Text("Frank Ocean \u{2014} Blonde").font(.system(size: 13))
                            .foregroundStyle(Color.musicInkSoft)
                    }
                    Spacer()
                }
                .frame(height: 54)
                GeometryReader { g in
                    ZStack(alignment: .leading) {
                        Capsule().fill(Color.musicInkSoft.opacity(0.35))
                        Capsule().fill(Color.musicInkSoft).frame(width: g.size.width * 0.54)
                    }
                }
                .frame(height: 1)
                .padding(.bottom, 2)
            }
            HStack(spacing: 14) {
                ForEach(["quote.bubble", "list.bullet", "speaker.wave.2.fill"], id: \.self) {
                    Image(systemName: $0).foregroundStyle(Color.musicInk)
                }
            }
        }
        .padding(.leading, 15)
        .padding(.trailing, 20)
        // The whole point of running this in SwiftUI: a REAL material, not a
        // backdrop-filter. If this reads wrong against the scrolled content
        // behind it, the CSS preview could never have told us.
        .background(.regularMaterial, in: Capsule())
        .overlay(Capsule().strokeBorder(.white.opacity(0.12), lineWidth: 0.5))
        .shadow(color: .black.opacity(0.18), radius: 12, y: 4)
    }
}

struct SpikeView: View {
    @State private var selection: String? = "Home"
    // A key WINDOW is not a focused LIST. The first run of this spike sampled a
    // grey selection and concluded .tint does not reach it -- but the system
    // accent on this Mac is blue and .tint's colour is red, so grey was neither:
    // it was the unfocused style, because nothing had put focus in the List.
    @FocusState private var listFocused: Bool
    private let nav = [("Search", "magnifyingglass"), ("Home", "house.fill"), ("New", "square.grid.2x2"), ("Radio", "dot.radiowaves.left.and.right")]
    private let library = ["Songs", "Recently Added", "Albums", "Artists"]

    var body: some View {
        NavigationSplitView {
            // The point of the spike: .listStyle(.sidebar) gives real vibrancy,
            // sampling the desktop behind the window. No background is set here
            // on purpose -- setting one would defeat the thing being tested.
            List(selection: $selection) {
                ForEach(nav, id: \.0) { name, icon in
                    // Music tints only the symbol; the label stays normal ink.
                    Label {
                        Text(name)
                    } icon: {
                        Image(systemName: icon).foregroundStyle(Color.musicAccent)
                    }
                    .tag(name)
                }
                Section("Library") {
                    ForEach(library, id: \.self) { name in
                        Label(name, systemImage: "music.note")
                            .foregroundStyle(Color.musicAccent)
                            .tag(name)
                    }
                }
            }
            .listStyle(.sidebar)
            .focused($listFocused)
            .onAppear { DispatchQueue.main.async { listFocused = true } }
            // Open question for slice 3: sidebar selection draws the SYSTEM
            // accent, not music-accent, even with every label tinted. .tint on
            // the List is the documented lever; this spike exists to check
            // whether it actually reaches the selection fill.
            .tint(Color.musicSelect)
            .navigationSplitViewColumnWidth(min: 180, ideal: 270)
        } detail: {
            ZStack(alignment: .bottom) {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    Text("Home").font(.system(size: 34, weight: .bold))
                        .foregroundStyle(Color.musicInk)
                    Text("ground-window against a real vibrant sidebar")
                        .foregroundStyle(Color.musicInkSoft)

                    // 56pt rows with the measured 1238x45pt inset pill, 40pt in
                    // from each side, ~6pt radius.
                    ForEach(1..<7) { i in
                        HStack {
                            Text("\(i)").foregroundStyle(Color.musicInkSoft).frame(width: 28)
                            Text("Track \(i)").foregroundStyle(i == 3 ? .white : Color.musicInk)
                            Spacer()
                            Text("3:0\(i)").foregroundStyle(i == 3 ? .white : Color.musicInkSoft)
                        }
                        .padding(.horizontal, 12)
                        .frame(height: 45)
                        .background(
                            RoundedRectangle(cornerRadius: 6)
                                .fill(i == 3 ? Color.musicSelect : (i == 5 ? Color.musicHover : .clear))
                        )
                        .padding(.horizontal, 40)
                        .frame(height: 56)
                    }
                }
                .padding(28)
                .frame(maxWidth: .infinity, alignment: .leading)
            }
            .background(Color.groundWindow)

            // Slice 6's actual fidelity gate. The CSS preview answers geometry
            // and nothing else: `glass` there is a backdrop-filter that samples
            // the page, while this capsule samples what is behind it in a real
            // window. 700 x 54 at a stadium radius, 19pt up, centred on THIS
            // column rather than the window, which is what the AX frames say.
            MiniPlayerSpike()
                .frame(width: 700, height: 54)
                .padding(.bottom, 19)
            }
        }
        .frame(minWidth: 900, minHeight: 600)
    }
}

let app = NSApplication.shared
app.setActivationPolicy(.regular)
let win = NSWindow(
    contentRect: NSRect(x: 200, y: 200, width: 1100, height: 760),
    styleMask: [.titled, .closable, .resizable, .fullSizeContentView],
    backing: .buffered, defer: false)
win.title = "App Kit Music spike"
win.titlebarAppearsTransparent = true
win.contentView = NSHostingView(rootView: SpikeView())
win.makeKeyAndOrderFront(nil)
app.activate(ignoringOtherApps: true)

// Self-capture. A shell-launched binary loses focus to the terminal within a
// second or two, so three external capture attempts all caught this window
// unfocused and only ever showed the inactive selection. Capturing from inside
// the process, after re-asserting focus, is the only way to observe the ACTIVE
// state without a human clicking the window.
if CommandLine.arguments.contains("--selfshot") {
    let out = CommandLine.arguments.last ?? "/tmp/spike-self.png"
    DispatchQueue.main.asyncAfter(deadline: .now() + 1.2) {
        NSApp.activate(ignoringOtherApps: true)
        win.makeKeyAndOrderFront(nil)
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.8) {
            let key = win.isKeyWindow, active = NSApp.isActive
            let p = Process()
            p.executableURL = URL(fileURLWithPath: "/usr/sbin/screencapture")
            p.arguments = ["-o", "-x", "-l", String(win.windowNumber), out]
            try? p.run(); p.waitUntilExit()
            // Report the focus state WITH the shot: a capture of an unfocused
            // window is not evidence about the active selection.
            FileHandle.standardError.write(
                "isKeyWindow=\(key) isActive=\(active) wrote=\(out)\n".data(using: .utf8)!)
            NSApp.terminate(nil)
        }
    }
}
app.run()
