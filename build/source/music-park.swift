// Move Music main window to a screen point via AX, no activation. Reopen a minimized window first:
//   osascript -e 'tell application "Music" to reopen'
import AppKit
import ApplicationServices

// usage: vdmove <x> <y>  -- move Music's main window to screen point (x, y) via AX, no activation
let x = Double(CommandLine.arguments[1])!
let y = Double(CommandLine.arguments[2])!
let p = NSWorkspace.shared.runningApplications.first(where: { $0.localizedName == "Music" })!.processIdentifier
let app = AXUIElementCreateApplication(p)
var v: CFTypeRef?
guard AXUIElementCopyAttributeValue(app, kAXMainWindowAttribute as CFString, &v) == .success else {
    print("no main window")
    exit(1)
}
let w = v as! AXUIElement
var pt = CGPoint(x: x, y: y)
let r = AXUIElementSetAttributeValue(w, kAXPositionAttribute as CFString, AXValueCreate(.cgPoint, &pt)!)
print("set position rc", r.rawValue)
var pv: CFTypeRef?
AXUIElementCopyAttributeValue(w, kAXPositionAttribute as CFString, &pv)
var out = CGPoint.zero
AXValueGetValue(pv as! AXValue, .cgPoint, &out)
print("now at", out.x, out.y)
