import Foundation

enum BatchCSV {
    static func data(_ results: [BatchURLResult]) -> Data {
        func field(_ input: String) -> String {
            // Prevent spreadsheet formula execution when an invalid URL starts with =, +, -, or @.
            let value = ["=", "+", "-", "@", "\t", "\r"].contains(String(input.prefix(1))) ? "'" + input : input
            return "\"" + value.replacingOccurrences(of: "\"", with: "\"\"") + "\""
        }
        let rows = results.map { [field($0.url), String($0.risk_score), field($0.risk_level)].joined(separator: ",") }
        return Data(("\u{FEFF}url,risk_score,risk_level\r\n" + rows.joined(separator: "\r\n")).utf8)
    }
}
