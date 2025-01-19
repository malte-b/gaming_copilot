const { BrowserWindow, app, screen, ipcMain, desktopCapturer } = require("electron");
const path = require("path");
const fs = require('fs')
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
        width: 500,
        height: 700,
        esizable: false,
        frame: false,
        alwaysOnTop: true,
        show: false, // we will manually display inputWindow when bubble is clicked
        x: width - 500 - 100,
        y: height - 700 - 200,
        webPreferences: {
            preload: path.join(__dirname, "preload.js"),
            nodeIntegration: true,
            webSecurity: false
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

    /** Handling screenshot */
    ipcMain.on(IPC_EVENTS.SCREENSHOT, async () => {
        try {
            const sources = await desktopCapturer.getSources({
                types: ['screen', 'window']
            })

            const entireScreen = sources.find(source => source.name === 'Entire screen')
            if (!entireScreen) {
                // @TODO: Show an alert
                return
            }

            // Get the thumbnail image
            const screenshot = entireScreen.thumbnail.toPNG();

            // Define a save path
            const savePath = path.join(__dirname, "screenshot.png");

            // Write the image to a file
            fs.writeFileSync(savePath, screenshot);


        } catch (cause) {
            console.log(cause)
        }
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
