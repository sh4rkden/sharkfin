import * as App from '../../../../wailsjs/go/main/App';

document.getElementById('close-btn').addEventListener('click', () => {
    App.CloseWindow();
});

document.getElementById('minimize-btn').addEventListener('click', () => {
    App.MinimizeWindow();
});