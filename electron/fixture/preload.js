const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('fixture', {
  sum: (left, right) => ipcRenderer.invoke('fixture:sum', left, right),
});
