import Foundation

func greet(name: String) -> String {
    return "Hello, \(name)"
}

func add(a: Int, b: Int) -> Int {
    return a + b
}

class Calculator {
    var total = 0

    func addToTotal(_ x: Int) {
        total += x
    }
}
