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

struct SpikeView: View {
    @State private var selection: String? = "Home"
    private let nav = [("Search", "magnifyingglass"), ("Home", "house.fill"), ("New", "square.grid.2x2"), ("Radio", "dot.radiowaves.left.and.right")]
    private let library = ["Songs", "Recently Added", "Albums", "Artists"]

    var body: some View {
        NavigationSplitView {
            // The point of the spike: .listStyle(.sidebar) gives real vibrancy,
            // sampling the desktop behind the window. No background is set here
            // on purpose -- setting one would defeat the thing being tested.
            List(selection: $selection) {
                ForEach(nav, id: \.0) { name, icon in
                    Label(name, systemImage: icon)
                        .foregroundStyle(Color.musicAccent)
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
            .navigationSplitViewColumnWidth(min: 180, ideal: 270)
        } detail: {
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
app.run()
