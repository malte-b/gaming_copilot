const { contextBridge, ipcRenderer } = require('electron')
const { IPC_EVENTS } = require('./utils/events')

/**
 * API to communicate between the renderer context and main context.
 */

contextBridge.exposeInMainWorld('electron', {
    goToInputWindow: () => {
        ipcRenderer.send(IPC_EVENTS.TRIGGER_INPUT_WINDOW)
    },
    minimize: () => {
        ipcRenderer.send(IPC_EVENTS.MINIMIZE)
    },
    screenshot: () => {
        ipcRenderer.send(IPC_EVENTS.SCREENSHOT)
    },
    screenshotTaken: (callback) => ipcRenderer.on(IPC_EVENTS.SCREENSHOT_TAKEN, (_, data) => callback(data))
})