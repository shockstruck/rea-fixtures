const { app, BrowserWindow, ipcMain } = require('electron');

ipcMain.handle('fixture:sum', (_event, left, right) => left + right);

app.whenReady().then(() => {
  const window = new BrowserWindow({
    webPreferences: { preload: __dirname + '/preload.js' },
  });
  window.loadFile('index.html');
});
