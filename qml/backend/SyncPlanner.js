.pragma library

function planPendingItems(items) {
    var operations = []
    for (var i = 0; i < items.length; ++i) {
        var item = items[i]
        if (item.pendingState === "state") {
            operations.push({ "kind": "state", "item": item })
        } else if (item.pendingState === "star") {
            operations.push({ "kind": "star", "item": item })
        }
    }
    return operations
}
