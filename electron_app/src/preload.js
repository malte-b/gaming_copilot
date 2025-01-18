const { contextBridge, ipcRenderer } = require('electron')
const { IPC_EVENTS } = require('./utils/events')

/**
 * API to communicate between the renderer context and main context.
 */

contextBridge.exposeInMainWorld('electron', {
    goToInputWindow: () => {
        ipcRenderer.send(IPC_EVENTS.TRIGGER_INPUT_WINDOW)
    }
})