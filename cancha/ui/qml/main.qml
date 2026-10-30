import QtQuick

Window {
    id: root
    visible: true
    width: 1600; height: 900
    color: "black"
    title: "Cancha"

    property int row: 0
    property int col: 0
    property int mrow: 0

    Item {
        anchors.fill: parent
        focus: true

        Keys.onUpPressed: {
            if (bridge.view === "home" && row > 0) { row--; col = 0 }
            else if (bridge.view === "match" && mrow > 0) mrow--
        }
        Keys.onDownPressed: {
            if (bridge.view === "home" && row < Math.min(bridge.rails.length, 2)) { row++; col = 0 }
            else if (bridge.view === "match" && mrow < bridge.servers.length - 1) mrow++
        }
        Keys.onLeftPressed: {
            if (bridge.view === "home" && col > 0) col--
        }
        Keys.onRightPressed: {
            if (bridge.view === "home") {
                var n = row === 0 ? bridge.filters.length : bridge.rails[row-1].events.length
                if (col < n - 1) col++
            }
        }
        Keys.onReturnPressed: activate()
        Keys.onEnterPressed: activate()
        Keys.onEscapePressed: { if (bridge.view === "match") bridge.goHome() }

        function activate() {
            if (bridge.view === "home") {
                if (row === 0) bridge.setFilter(col)
                else {
                    var ev = bridge.rails[row-1].events[col]
                    if (ev) bridge.openMatch(ev.id)
                }
            } else {
                bridge.playServer(mrow)
            }
        }

        // ---------- HOME ----------
        Column {
            anchors.fill: parent
            visible: bridge.view === "home"
            spacing: 0

            Rectangle {
                width: parent.width; height: 300
                color: "#0a0f1e"
                Row {
                    anchors.centerIn: parent
                    spacing: 60
                    opacity: 0.3
                    Image { width: 180; height: 180; fillMode: Image.PreserveAspectFit; source: bridge.hero.flagA || "" }
                    Image { width: 180; height: 180; fillMode: Image.PreserveAspectFit; source: bridge.hero.flagB || "" }
                }
                Column {
                    anchors.left: parent.left; anchors.right: parent.right
                    anchors.bottom: parent.bottom; anchors.margins: 70
                    anchors.bottomMargin: 26
                    spacing: 6
                    Text { text: (bridge.hero.badge || "") + "  ·  " + (bridge.hero.sub || ""); color: "#f5c518"; font.pixelSize: 16; font.bold: true }
                    Text { text: (bridge.hero.title || "Loading…").toUpperCase(); color: "white"; font.pixelSize: 52; font.bold: true }
                    Text { text: bridge.hero.count || ""; color: "#999"; font.pixelSize: 15 }
                }
            }

            Row {
                padding: 0
                spacing: 12
                Repeater {
                    model: bridge.filters
                    delegate: Rectangle {
                        width: pillText.width + 44; height: 52
                        y: 18; x: index === 0 ? 70 : 0
                        color: root.row === 0 && root.col === index ? "#f5c518" : "#141821"
                        radius: 8
                        border.width: root.row === 0 && root.col === index ? 0 : 0
                        Text {
                            id: pillText
                            anchors.centerIn: parent
                            text: (modelData || "").toUpperCase()
                            color: root.row === 0 && root.col === index ? "black" : "white"
                            font.pixelSize: 17; font.bold: true
                        }
                        MouseArea {
                            anchors.fill: parent; hoverEnabled: true
                            onEntered: { root.row = 0; root.col = index }
                            onClicked: bridge.setFilter(index)
                        }
                    }
                }
            }

            Repeater {
                model: bridge.rails.slice(0, 2)
                delegate: Column {
                    property int railNum: index + 1
                    spacing: 10
                    Text {
                        x: 70
                        text: (modelData.title || "").toUpperCase()
                        color: "white"; font.pixelSize: 19; font.bold: true
                    }
                    Row {
                        spacing: 16
                        Repeater {
                            model: modelData.events.slice(0, 4)
                            delegate: Column {
                                width: 340
                                spacing: 8
                                Rectangle {
                                    width: 340; height: 150
                                    color: "#1a2030"; radius: 6
                                    border.color: "#f5c518"; border.width: (root.row === railNum && root.col === index) ? 4 : 0
                                    Row {
                                        anchors.centerIn: parent
                                        spacing: 24
                                        Image { width: 72; height: 72; fillMode: Image.PreserveAspectFit; source: modelData.flagA || "" }
                                        Image { width: 72; height: 72; fillMode: Image.PreserveAspectFit; source: modelData.flagB || "" }
                                    }
                                    Rectangle {
                                        x: 8; y: 8; width: badgeText.width + 20; height: 26
                                        color: "white"; radius: 3
                                        Text { id: badgeText; anchors.centerIn: parent; text: modelData.badge || ""; color: "black"; font.pixelSize: 12; font.bold: true }
                                    }
                                }
                                Text { text: (modelData.title || "").toUpperCase(); color: "white"; font.pixelSize: 15; font.bold: true; elide: Text.ElideRight; width: 340 }
                                Text { text: (modelData.sub || "") + " · " + (modelData.count || ""); color: "#999"; font.pixelSize: 13 }
                                MouseArea {
                                    anchors.fill: parent; hoverEnabled: true
                                    onEntered: { root.row = railNum; root.col = index }
                                    onClicked: bridge.openMatch(modelData.id)
                                }
                            }
                        }
                    }
                }
            }
        }

        // ---------- MATCH ----------
        Column {
            anchors.fill: parent
            visible: bridge.view === "match"
            spacing: 18
            Rectangle { width: parent.width; height: 200; color: "#0a0f1e"
                Column {
                    anchors.left: parent.left; anchors.bottom: parent.bottom
                    anchors.margins: 70; anchors.bottomMargin: 24; spacing: 6
                    Text { text: (bridge.match.badge || "") + "  ·  " + (bridge.match.sub || ""); color: "#f5c518"; font.pixelSize: 15; font.bold: true }
                    Text { text: (bridge.match.title || "").toUpperCase(); color: "white"; font.pixelSize: 40; font.bold: true }
                }
            }
            Text { x: 70; text: "SERVERS — PICK ONE, PLAYBACK STARTS INSTANTLY"; color: "white"; font.pixelSize: 18; font.bold: true }
            Repeater {
                model: bridge.servers
                delegate: Rectangle {
                    x: 70; width: 1050; height: 64
                    color: "#141821"; radius: 6
                    border.color: "#f5c518"; border.width: root.mrow === index ? 4 : 0
                    Text {
                        anchors.left: parent.left; anchors.verticalCenter: parent.verticalCenter
                        anchors.leftMargin: 24
                        text: modelData.title + "   " + (modelData.note || "")
                        color: "white"; font.pixelSize: 17; font.bold: true
                    }
                    Text {
                        anchors.right: parent.right; anchors.verticalCenter: parent.verticalCenter
                        anchors.rightMargin: 24
                        text: "▶ WATCH"; color: root.mrow === index ? "#f5c518" : "#999"; font.pixelSize: 16; font.bold: true
                    }
                    MouseArea {
                        anchors.fill: parent; hoverEnabled: true
                        onEntered: root.mrow = index
                        onClicked: bridge.playServer(index)
                    }
                }
            }
            Text { x: 70; text: bridge.status; color: "#f5c518"; font.pixelSize: 14; visible: bridge.status !== "" }
            Text { x: 70; text: "ESC back"; color: "#666"; font.pixelSize: 13 }
        }
    }
}
