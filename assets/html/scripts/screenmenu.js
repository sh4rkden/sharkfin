const itemMenu = document.getElementById("itemMenu")

function hideMenu() {
    document.getElementById("screenContent").style.backdropFilter = "blur(0px)";
    document.getElementById('itemMenu').style.scale = "0.8";
    document.getElementById('itemMenu').style.opacity = "0";
    setTimeout(() => {
        document.getElementById('focusScreen').style.zIndex = "-1";
    }, 320)
}

itemMenu.addEventListener("click", function() {
    hideMenu();
})

function renderMenu(options) {
    const menuContainer = document.getElementById('menuContainer');
    menuContainer.innerHTML = '';

    options.forEach(option => {
        const interactable = document.createElement('uiInteractable');
        interactable.style.cursor = 'pointer';
        const optionDiv = document.createElement('div');
        optionDiv.style.textAlign = 'center';
        const textElem = document.createElement('text');
        textElem.textContent = option.text;
        optionDiv.appendChild(textElem);
        interactable.appendChild(optionDiv);
        interactable.addEventListener('click', function() {
            option.onclick;
            window.pywebview.api.updateFrontendConfigDisplays();
            console.log("func")
        });
        menuContainer.appendChild(interactable);
    });

    document.getElementById("screenContent").style.backdropFilter = "blur(5px)";
    document.getElementById('itemMenu').style.scale = "1";
    document.getElementById('itemMenu').style.opacity = "1";
    document.getElementById('focusScreen').style.zIndex = "2";
}