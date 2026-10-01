// Dump an app's accessibility tree with frames in POINTS.
// Music does not populate AXWindows and is invisible to System Events, but
// AXMainWindow is reachable -- enter through that.
// usage: swift ax-dump.swift <App Name> [maxDepth]
import AppKit
import ApplicationServices

let appName = CommandLine.arguments[1]
let maxDepth = CommandLine.arguments.count > 2 ? Int(CommandLine.arguments[2])! : 6
guard let p = NSWorkspace.shared.runningApplications
        .first(where: { $0.localizedName == appName })?.processIdentifier else {
    FileHandle.standardError.write("not running\n".data(using:.utf8)!); exit(1)
}
func attr(_ el: AXUIElement, _ a: String) -> CFTypeRef? {
    var v: CFTypeRef?
    return AXUIElementCopyAttributeValue(el, a as CFString, &v) == .success ? v : nil
}
func str(_ el: AXUIElement, _ a: String) -> String? { attr(el, a) as? String }
func frame(_ el: AXUIElement) -> (CGPoint, CGSize)? {
    guard let pv = attr(el, kAXPositionAttribute as String),
          let sv = attr(el, kAXSizeAttribute as String) else { return nil }
    var pt = CGPoint.zero, sz = CGSize.zero
    AXValueGetValue(pv as! AXValue, .cgPoint, &pt)
    AXValueGetValue(sv as! AXValue, .cgSize, &sz)
    return (pt, sz)
}
func walk(_ el: AXUIElement, _ depth: Int, _ originX: CGFloat, _ originY: CGFloat) {
    guard depth <= maxDepth else { return }
    let role = str(el, kAXRoleAttribute as String) ?? "?"
    let title = str(el, kAXTitleAttribute as String) ?? str(el, kAXDescriptionAttribute as String) ?? ""
    let value = str(el, kAXValueAttribute as String) ?? ""
    var geo = ""
    if let (pt, sz) = frame(el) {
        geo = String(format: "x=%.1f y=%.1f w=%.1f h=%.1f",
                     pt.x - originX, pt.y - originY, sz.width, sz.height)
    }
    let label = [title, value].filter{ !$0.isEmpty }.joined(separator: " / ")
    let pad = String(repeating: "  ", count: depth)
    print("\(pad)\(role)  \(geo)\(label.isEmpty ? "" : "  \"\(label.prefix(60))\"")")
    if let kids = attr(el, kAXChildrenAttribute as String) as? [AXUIElement] {
        for k in kids { walk(k, depth + 1, originX, originY) }
    }
}
let app = AXUIElementCreateApplication(p)
guard let wv = attr(app, kAXMainWindowAttribute as String) else {
    FileHandle.standardError.write("no AXMainWindow\n".data(using:.utf8)!); exit(2)
}
let win = wv as! AXUIElement
let (wp, ws) = frame(win) ?? (.zero, .zero)
print("window  \(Int(ws.width))x\(Int(ws.height))pt at (\(Int(wp.x)),\(Int(wp.y)))  -- child frames are window-relative")
walk(win, 0, wp.x, wp.y)
