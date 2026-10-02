// Drive Music for a capture without disturbing the user: activate, click, optionally one key,
// capture by window id inside the key window, then restore the cursor and frontmost app.
// HOLD=1 keeps the button down during the capture. Park the window first with music-park.swift.
// Build: swiftc -O build/source/music-drive.swift -o <bin>. Needs Accessibility trust for the host.
import AppKit
import CoreGraphics

// usage: drive <clickX> <clickY> <parkX> <parkY> <winId> <out.png> [keycode [shift]]
// Activates Music, clicks, optionally sends one key, captures the window by id,
// then restores the previously frontmost app and the real cursor position.
let a = CommandLine.arguments
let cx = Double(a[1])!, cy = Double(a[2])!, px = Double(a[3])!, py = Double(a[4])!
let winId = a[5], out = a[6]
let key: UInt16? = a.count > 7 ? UInt16(a[7]) : nil
let shift = a.count > 8 && a[8] == "shift"
let hold = ProcessInfo.processInfo.environment["HOLD"] == "1"

let savedCursor = CGEvent(source: nil)!.location
let prior = NSWorkspace.shared.frontmostApplication
let music = NSWorkspace.shared.runningApplications.first(where: { $0.localizedName == "Music" })!

func post(_ t: CGEventType, _ x: Double, _ y: Double) {
    CGEvent(mouseEventSource: nil, mouseType: t, mouseCursorPosition: CGPoint(x: x, y: y), mouseButton: .left)?.post(tap: .cghidEventTap)
}

music.activate(options: [.activateIgnoringOtherApps])
usleep(500_000)
post(.mouseMoved, cx, cy); usleep(120_000)
post(.leftMouseDown, cx, cy); usleep(80_000)
if !hold { post(.leftMouseUp, cx, cy); usleep(300_000); post(.mouseMoved, px, py); usleep(150_000) } else { usleep(400_000) }
if let k = key {
    for down in [true, false] {
        let e = CGEvent(keyboardEventSource: nil, virtualKey: CGKeyCode(k), keyDown: down)
        if shift { e?.flags = .maskShift }
        e?.post(tap: .cghidEventTap)
        usleep(60_000)
    }
    usleep(350_000)
}

let t = Process()
t.executableURL = URL(fileURLWithPath: "/usr/sbin/screencapture")
t.arguments = ["-o", "-x", "-l", winId, out]
try! t.run(); t.waitUntilExit()
if hold { post(.mouseMoved, cx, cy); post(.leftMouseUp, cx, cy); usleep(200_000) }

CGWarpMouseCursorPosition(savedCursor)
prior?.activate(options: [])
print("captured; restored cursor", savedCursor.x, savedCursor.y, "front", prior?.localizedName ?? "?")
