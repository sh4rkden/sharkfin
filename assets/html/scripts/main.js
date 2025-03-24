
const uiInteractables = document.querySelectorAll('.uiInteractable');

uiInteractables.forEach(element => {
    element.addEventListener('click', () => {
        element.classList.add('active');
        setTimeout(() => {
            element.classList.remove('active');
        }, 500);
    });
});

// startup things lol
setTimeout(() => {
    document.querySelector('#integrations')?.scrollIntoView({ behavior: 'smooth' });
}, 2000);
setTimeout(() => {
    document.getElementById('sharkfinscreen')?.remove();
}, 2550);
