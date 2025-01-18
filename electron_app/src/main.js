const { BrowserWindow, app, screen, ipcMain } = require("electron");
const path = require("path");
const { IPC_EVENTS } = require("./utils/events");

let bubbleWindow
let inputWindow

function createWindow() {
    const { width, height } = screen.getPrimaryDisplay().workAreaSize;

    bubbleWindow = new BrowserWindow({
        width: 100,
        height: 100,
        frame: false,
        resizable: false,
        transparent: true,
        alwaysOnTop: true,
        webPreferences: {
            preload: path.join(__dirname, "preload.js"),
            nodeIntegration: true,
        },
        x: width - 200,
        y: height - 200
    });

    bubbleWindow.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true });
    bubbleWindow.setHasShadow(false);

    bubbleWindow.loadFile(path.join(__dirname, "windows", "bubble.html"));

    inputWindow = new BrowserWindow({
        width: width - 400,
        height: height - 400,
        center: true,
        resizable: false,
        frame: false,
        alwaysOnTop: true,
        show: false, // we will manually display inputWindow when bubble is clicked
        webPreferences: {
            preload: path.join(__dirname, "preload.js"),
            nodeIntegration: true,
        }
    })
    inputWindow.loadFile(path.join(__dirname, "windows", "input.html"));
}

app.whenReady().then(() => {
    createWindow();

    /** Handling the event when user clicks on the bubble */
    ipcMain.on(IPC_EVENTS.TRIGGER_INPUT_WINDOW, () => {
        bubbleWindow.hide()
        inputWindow.show()
        // inputWindow.webContents.openDevTools({ mode: 'detach' })
    })

    /** Handling the event when user clicks on the minimize button */
    ipcMain.on(IPC_EVENTS.MINIMIZE, () => {
        inputWindow.hide()
        bubbleWindow.show()
    })

    app.on("activate", () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on("window-all-closed", () => {
    if (process.platform !== "darwin") {
        app.quit();
    }
});
