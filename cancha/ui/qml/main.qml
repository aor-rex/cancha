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
    property int lrow: 0
    property int crow: 0
    property int hrow: 0
    property int srow: 0
    property var navItems: ["home", "sports", "livetv", "highlights", "search"]
    property var navLabels: ["HOME", "SPORTS", "LIVE TV", "HIGHLIGHTS", "SEARCH"]

    function homeRails() {
        var r = bridge.rails.slice(0, 2)
        if (bridge.favrail.length > 0) r = [{"title": "★ Favorites", "events": bridge.favrail}].concat(r).slice(0, 2)
        return r
    }
    function sportsRails() {
        var r = bridge.rails
        if (bridge.favrail.length > 0) r = [{"title": "★ Favorites", "events": bridge.favrail}].concat(r)
        return r.slice(0, 3)
    }
    function navGo(i) { bridge.go(navItems[i]) }

    Item {
        anchors.fill: parent
        focus: true

        Keys.onUpPressed: {
            if ((bridge.view === "home" || bridge.view === "sports") && row > 0) { row--; col = 0 }
            else if (bridge.view === "livetv" && lrow > 0) lrow--
            else if (bridge.view === "channels" && crow > 0) crow--
            else if (bridge.view === "highlights" && hrow > 0) hrow--
            else if (bridge.view === "search" && srow > 0) srow--
            else if (bridge.view === "match" && mrow > 0) mrow--
        }
        Keys.onDownPressed: {
            if (bridge.view === "home" && row < homeRails().length) { row++; col = 0 }
            else if (bridge.view === "sports" && row < sportsRails().length) { row++; col = 0 }
            else if (bridge.view === "livetv" && lrow < bridge.providers.length - 1) lrow++
            else if (bridge.view === "channels" && crow < bridge.channels.length - 1) crow++
            else if (bridge.view === "highlights" && hrow < bridge.reels.length - 1) hrow++
            else if (bridge.view === "search" && srow < bridge.results.length - 1) srow++
            else if (bridge.view === "match" && mrow < bridge.servers.length) mrow++
        }
        Keys.onLeftPressed: {
            if ((bridge.view === "home" || bridge.view === "sports") && col > 0) col--
        }
        Keys.onRightPressed: {
            if (bridge.view === "home" || bridge.view === "sports") {
                var lanes = row === 0 ? 5 : (row === 1 ? bridge.filters.length : (bridge.view === "home" ? homeRails()[row-1].events.length : sportsRails()[row-1].events.length))
                if (col < lanes - 1) col++
            }
        }
        Keys.onReturnPressed: activate()
        Keys.onEnterPressed: activate()
        Keys.onEscapePressed: {
            if (bridge.view === "channels") bridge.go("livetv")
            else if (bridge.view !== "home") bridge.go("home")
        }
        Keys.onPressed: {
            if (event.key === Qt.Key_F && bridge.view === "match") bridge.toggleFav()
        }

        function activate() {
            if (bridge.view === "home") {
                if (row === 0) navGo(col)
                else if (row === 1) bridge.setFilter(col)
                else { var ev = homeRails()[row-1].events[col]; if (ev) bridge.openMatch(ev.id) }
            } else if (bridge.view === "sports") {
                if (row === 0) navGo(col)
                else if (row === 1) bridge.setFilter(col)
                else { var ev2 = sportsRails()[row-1].events[col]; if (ev2) bridge.openMatch(ev2.id) }
            } else if (bridge.view === "livetv") {
                if (row === 0) navGo(col)
                else { var p = bridge.providers[lrow]; if (p) bridge.openProvider(p.ref) }
            } else if (bridge.view === "channels") {
                var c = bridge.channels[crow]; if (c) bridge.playChannel(c.id, c.url || "")
            } else if (bridge.view === "highlights") {
                var r = bridge.reels[hrow]; if (r) bridge.playReel(r.id)
            } else if (bridge.view === "search") {
                var s = bridge.results[srow]; if (s) bridge.openMatch(s.id)
            } else if (bridge.view === "match") {
                if (mrow === 0) bridge.toggleFav()
                else bridge.playServer(mrow - 1)
            }
        }

        // ---------- NAV ----------
        Row {
            id: navbar
            visible: bridge.view !== "match" && bridge.view !== "channels" && bridge.view !== "search"
            spacing: 28
            Repeater {
                model: 5
                delegate: Text {
                    y: 20; x: index === 0 ? 70 : 0
                    text: root.navLabels[index]
                    color: (root.row === 0 && root.col === index) ? "#f5c518" : (bridge.view === root.navItems[index] ? "white" : "#777")
                    font.pixelSize: 17; font.bold: true
                    MouseArea {
                        anchors.fill: parent; hoverEnabled: true
                        onEntered: { if (bridge.view === "home" || bridge.view === "sports" || bridge.view === "livetv" || bridge.view === "highlights") { root.row = 0; root.col = index } }
                        onClicked: root.navGo(index)
                    }
                }
            }
        }

        // ---------- HOME ----------
        Column {
            anchors.fill: parent
            anchors.topMargin: 56
            visible: bridge.view === "home"
            spacing: 0

            Rectangle {
                width: parent.width; height: 280
                color: "#0a0f1e"
                Row {
                    anchors.centerIn: parent
                    spacing: 60
                    opacity: 0.3
                    Image { width: 170; height: 170; fillMode: Image.PreserveAspectFit; source: bridge.hero.flagA || "" }
                    Image { width: 170; height: 170; fillMode: Image.PreserveAspectFit; source: bridge.hero.flagB || "" }
                }
                Column {
                    anchors.left: parent.left; anchors.right: parent.right
                    anchors.bottom: parent.bottom; anchors.margins: 70
                    anchors.bottomMargin: 24
                    spacing: 6
                    Text { text: (bridge.hero.badge || "") + "  ·  " + (bridge.hero.sub || ""); color: "#f5c518"; font.pixelSize: 16; font.bold: true }
                    Text { text: (bridge.hero.title || "Loading…").toUpperCase(); color: "white"; font.pixelSize: 50; font.bold: true }
                    Text { text: bridge.hero.count || ""; color: "#999"; font.pixelSize: 15 }
                }
            }

            Row {
                spacing: 12
                Repeater {
                    model: bridge.filters
                    delegate: Rectangle {
                        width: pillText.width + 44; height: 50
                        y: 16; x: index === 0 ? 70 : 0
                        color: root.row === 1 && root.col === index ? "#f5c518" : "#141821"
                        radius: 8
                        Text {
                            id: pillText
                            anchors.centerIn: parent
                            text: (modelData || "").toUpperCase()
                            color: root.row === 1 && root.col === index ? "black" : "white"
                            font.pixelSize: 17; font.bold: true
                        }
                        MouseArea {
                            anchors.fill: parent; hoverEnabled: true
                            onEntered: { root.row = 1; root.col = index }
                            onClicked: bridge.setFilter(index)
                        }
                    }
                }
            }

            Repeater {
                model: homeRails()
                delegate: Column {
                    property int railNum: index + 1
                    spacing: 8
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
                                spacing: 6
                                Rectangle {
                                    width: 340; height: 140
                                    color: "#1a2030"; radius: 6
                                    border.color: "#f5c518"; border.width: (root.row === railNum + 1 && root.col === index) ? 4 : 0
                                    Row {
                                        anchors.centerIn: parent
                                        spacing: 24
                                        Image { width: 68; height: 68; fillMode: Image.PreserveAspectFit; source: modelData.flagA || "" }
                                        Image { width: 68; height: 68; fillMode: Image.PreserveAspectFit; source: modelData.flagB || "" }
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
                                    onEntered: { root.row = railNum + 1; root.col = index }
                                    onClicked: bridge.openMatch(modelData.id)
                                }
                            }
                        }
                    }
                }
            }
            Text { x: 70; text: bridge.status; color: "#f5c518"; font.pixelSize: 14; visible: bridge.status !== "" }
        }

        // ---------- SPORTS ----------
        Column {
            anchors.fill: parent
            anchors.topMargin: 56
            visible: bridge.view === "sports"
            spacing: 0
            Row {
                spacing: 12
                Repeater {
                    model: bridge.filters
                    delegate: Rectangle {
                        width: pillText2.width + 44; height: 50
                        y: 16; x: index === 0 ? 70 : 0
                        color: root.row === 1 && root.col === index ? "#f5c518" : "#141821"
                        radius: 8
                        Text {
                            id: pillText2
                            anchors.centerIn: parent
                            text: (modelData || "").toUpperCase()
                            color: root.row === 1 && root.col === index ? "black" : "white"
                            font.pixelSize: 17; font.bold: true
                        }
                        MouseArea {
                            anchors.fill: parent; hoverEnabled: true
                            onEntered: { root.row = 1; root.col = index }
                            onClicked: bridge.setFilter(index)
                        }
                    }
                }
            }
            Repeater {
                model: sportsRails()
                delegate: Column {
                    property int railNum: index + 1
                    spacing: 8
                    Text { x: 70; text: (modelData.title || "").toUpperCase(); color: "white"; font.pixelSize: 19; font.bold: true }
                    Row {
                        spacing: 16
                        Repeater {
                            model: modelData.events.slice(0, 4)
                            delegate: Column {
                                width: 340
                                spacing: 6
                                Rectangle {
                                    width: 340; height: 130
                                    color: "#1a2030"; radius: 6
                                    border.color: "#f5c518"; border.width: (root.row === railNum + 1 && root.col === index) ? 4 : 0
                                    Row {
                                        anchors.centerIn: parent
                                        spacing: 24
                                        Image { width: 64; height: 64; fillMode: Image.PreserveAspectFit; source: modelData.flagA || "" }
                                        Image { width: 64; height: 64; fillMode: Image.PreserveAspectFit; source: modelData.flagB || "" }
                                    }
                                    Rectangle {
                                        x: 8; y: 8; width: badgeText2.width + 20; height: 26
                                        color: "white"; radius: 3
                                        Text { id: badgeText2; anchors.centerIn: parent; text: modelData.badge || ""; color: "black"; font.pixelSize: 12; font.bold: true }
                                    }
                                }
                                Text { text: (modelData.title || "").toUpperCase(); color: "white"; font.pixelSize: 15; font.bold: true; elide: Text.ElideRight; width: 340 }
                                Text { text: (modelData.sub || "") + " · " + (modelData.count || ""); color: "#999"; font.pixelSize: 13 }
                                MouseArea {
                                    anchors.fill: parent; hoverEnabled: true
                                    onEntered: { root.row = railNum + 1; root.col = index }
                                    onClicked: bridge.openMatch(modelData.id)
                                }
                            }
                        }
                    }
                }
            }
        }

        // ---------- LIVE TV ----------
        Column {
            anchors.fill: parent
            anchors.topMargin: 56
            visible: bridge.view === "livetv"
            spacing: 14
            Text { x: 70; text: "PROVIDERS — 74 NETWORKS, PICK ONE"; color: "white"; font.pixelSize: 19; font.bold: true }
            Repeater {
                model: bridge.providers.slice(0, 9)
                delegate: Rectangle {
                    x: 70; width: 1050; height: 58
                    color: "#141821"; radius: 6
                    border.color: "#f5c518"; border.width: root.lrow === index && root.row !== 0 ? 4 : 0
                    Text {
                        anchors.left: parent.left; anchors.verticalCenter: parent.verticalCenter
                        anchors.leftMargin: 24
                        text: modelData.name
                        color: "white"; font.pixelSize: 17; font.bold: true
                    }
                    Text {
                        anchors.right: parent.right; anchors.verticalCenter: parent.verticalCenter
                        anchors.rightMargin: 24
                        text: modelData.playlist ? "M3U ▸" : "HUB ▸"
                        color: root.lrow === index && root.row !== 0 ? "#f5c518" : "#999"; font.pixelSize: 15; font.bold: true
                    }
                    MouseArea {
                        anchors.fill: parent; hoverEnabled: true
                        onEntered: { root.row = 1; root.lrow = index }
                        onClicked: bridge.openProvider(modelData.ref)
                    }
                }
            }
            Text { x: 70; text: bridge.status; color: "#f5c518"; font.pixelSize: 14; visible: bridge.status !== "" }
            Text { x: 70; text: "Showing 9 of " + bridge.providers.length + " — search narrows it (phase 5)"; color: "#666"; font.pixelSize: 13 }
        }

        // ---------- CHANNELS ----------
        Column {
            anchors.fill: parent
            anchors.topMargin: 24
            visible: bridge.view === "channels"
            spacing: 14
            Text { x: 70; text: "CHANNELS — OK PLAYS INSTANTLY"; color: "white"; font.pixelSize: 19; font.bold: true }
            Repeater {
                model: bridge.channels.slice(0, 9)
                delegate: Rectangle {
                    x: 70; width: 1050; height: 58
                    color: "#141821"; radius: 6
                    border.color: "#f5c518"; border.width: root.crow === index ? 4 : 0
                    Row {
                        anchors.left: parent.left; anchors.verticalCenter: parent.verticalCenter
                        anchors.leftMargin: 24
                        spacing: 16
                        Image { width: 40; height: 40; fillMode: Image.PreserveAspectFit; source: modelData.image || ""; anchors.verticalCenter: parent.verticalCenter }
                        Text { text: modelData.title; color: "white"; font.pixelSize: 17; font.bold: true; anchors.verticalCenter: parent.verticalCenter }
                    }
                    Text {
                        anchors.right: parent.right; anchors.verticalCenter: parent.verticalCenter
                        anchors.rightMargin: 24
                        text: "▶ WATCH"; color: root.crow === index ? "#f5c518" : "#999"; font.pixelSize: 16; font.bold: true
                    }
                    MouseArea {
                        anchors.fill: parent; hoverEnabled: true
                        onEntered: root.crow = index
                        onClicked: bridge.playChannel(modelData.id, modelData.url || "")
                    }
                }
            }
            Text { x: 70; text: bridge.status; color: "#f5c518"; font.pixelSize: 14; visible: bridge.status !== "" }
            Text { x: 70; text: "ESC back to providers"; color: "#666"; font.pixelSize: 13 }
        }

        // ---------- HIGHLIGHTS ----------
        Column {
            anchors.fill: parent
            anchors.topMargin: 56
            visible: bridge.view === "highlights"
            spacing: 14
            Text { x: 70; text: "HIGHLIGHTS & REELS — OK PLAYS"; color: "white"; font.pixelSize: 19; font.bold: true }
            Repeater {
                model: bridge.reels.slice(0, 9)
                delegate: Rectangle {
                    x: 70; width: 1050; height: 58
                    color: "#141821"; radius: 6
                    border.color: "#f5c518"; border.width: root.hrow === index && root.row !== 0 ? 4 : 0
                    Text {
                        anchors.left: parent.left; anchors.verticalCenter: parent.verticalCenter
                        anchors.leftMargin: 24
                        text: modelData.title
                        color: "white"; font.pixelSize: 17; font.bold: true
                    }
                    Text {
                        anchors.right: parent.right; anchors.verticalCenter: parent.verticalCenter
                        anchors.rightMargin: 24
                        text: "▶ PLAY"; color: root.hrow === index && root.row !== 0 ? "#f5c518" : "#999"; font.pixelSize: 16; font.bold: true
                    }
                    MouseArea {
                        anchors.fill: parent; hoverEnabled: true
                        onEntered: { root.row = 1; root.hrow = index }
                        onClicked: bridge.playReel(modelData.id)
                    }
                }
            }
            Text { x: 70; text: bridge.status; color: "#f5c518"; font.pixelSize: 14; visible: bridge.status !== "" }
        }

        // ---------- SEARCH ----------
        Column {
            anchors.fill: parent
            anchors.topMargin: 24
            visible: bridge.view === "search"
            spacing: 14
            Text { x: 70; text: "SEARCH — TEAMS, COMPETITIONS, EVENTS"; color: "white"; font.pixelSize: 19; font.bold: true }
            Rectangle {
                x: 70; width: 600; height: 58
                color: "#141821"; radius: 6
                border.color: "#f5c518"; border.width: 2
                TextInput {
                    id: searchBox
                    anchors.fill: parent
                    anchors.margins: 16
                    color: "white"; font.pixelSize: 18
                    focus: bridge.view === "search" && bridge.results.length === 0
                    onAccepted: bridge.search(text)
                    Keys.onDownPressed: { searchBox.focus = false }
                }
            }
            Repeater {
                model: bridge.results.slice(0, 9)
                delegate: Rectangle {
                    x: 70; width: 1050; height: 58
                    color: "#141821"; radius: 6
                    border.color: "#f5c518"; border.width: root.srow === index ? 4 : 0
                    Text {
                        anchors.left: parent.left; anchors.verticalCenter: parent.verticalCenter
                        anchors.leftMargin: 24
                        text: modelData.title + "   ·   " + (modelData.sub || "")
                        color: "white"; font.pixelSize: 17; font.bold: true
                    }
                    MouseArea {
                        anchors.fill: parent; hoverEnabled: true
                        onEntered: root.srow = index
                        onClicked: bridge.openMatch(modelData.id)
                    }
                }
            }
            Text { x: 70; text: bridge.results.length + " results — ESC home"; color: "#666"; font.pixelSize: 13 }
        }

        // ---------- MATCH ----------
        Column {
            anchors.fill: parent
            anchors.topMargin: 24
            visible: bridge.view === "match"
            spacing: 14
            Rectangle { width: parent.width; height: 180; color: "#0a0f1e"
                Column {
                    anchors.left: parent.left; anchors.bottom: parent.bottom
                    anchors.margins: 70; anchors.bottomMargin: 24; spacing: 6
                    Text { text: (bridge.match.badge || "") + "  ·  " + (bridge.match.sub || ""); color: "#f5c518"; font.pixelSize: 15; font.bold: true }
                    Text { text: (bridge.match.title || "").toUpperCase(); color: "white"; font.pixelSize: 38; font.bold: true }
                }
            }
            Rectangle {
                x: 70; width: 1050; height: 58
                color: "#141821"; radius: 6
                border.color: "#f5c518"; border.width: root.mrow === 0 ? 4 : 0
                Text {
                    anchors.left: parent.left; anchors.verticalCenter: parent.verticalCenter
                    anchors.leftMargin: 24
                    text: bridge.matchstar + "  Favorite this team (F)"
                    color: "white"; font.pixelSize: 16; font.bold: true
                }
                MouseArea {
                    anchors.fill: parent; hoverEnabled: true
                    onEntered: root.mrow = 0
                    onClicked: bridge.toggleFav()
                }
            }
            Text { x: 70; text: "SERVERS — PICK ONE, PLAYBACK STARTS INSTANTLY"; color: "white"; font.pixelSize: 18; font.bold: true }
            Repeater {
                model: bridge.servers
                delegate: Rectangle {
                    x: 70; width: 1050; height: 60
                    color: "#141821"; radius: 6
                    border.color: "#f5c518"; border.width: root.mrow === index + 1 ? 4 : 0
                    Text {
                        anchors.left: parent.left; anchors.verticalCenter: parent.verticalCenter
                        anchors.leftMargin: 24
                        text: modelData.title + "   " + (modelData.note || "")
                        color: "white"; font.pixelSize: 17; font.bold: true
                    }
                    Text {
                        anchors.right: parent.right; anchors.verticalCenter: parent.verticalCenter
                        anchors.rightMargin: 24
                        text: "▶ WATCH"; color: root.mrow === index + 1 ? "#f5c518" : "#999"; font.pixelSize: 16; font.bold: true
                    }
                    MouseArea {
                        anchors.fill: parent; hoverEnabled: true
                        onEntered: root.mrow = index + 1
                        onClicked: bridge.playServer(index)
                    }
                }
            }
            Text { x: 70; text: bridge.status; color: "#f5c518"; font.pixelSize: 14; visible: bridge.status !== "" }
            Text { x: 70; text: "F favorite · ESC back"; color: "#666"; font.pixelSize: 13 }
        }
    }
}
