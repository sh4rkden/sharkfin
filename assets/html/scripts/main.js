const itemMenu = document.getElementById("itemMenu")

window.addEventListener("pywebviewready", function() {
    setTimeout(() => {
        document.getElementById("screenContent").style.backdropFilter = "blur(0px)";
        document.getElementById('sharkfinscreen').style.scale = "0.8";
        document.getElementById('sharkfinscreen').style.opacity = "0";
    }, 1000)
    
    setTimeout(() => {
        document.getElementById('focusScreen').style.zIndex = "-1";
        document.getElementById('sharkfinscreen')?.remove();
    }, 1500);

    window.pywebview.api.updateFrontendConfigDisplays();

    // modding
    // none... yet.
    
    // fastflags
    const ffEditor = document.getElementById("ff-editor") // flag browser
    const preferredGPU = document.getElementById("preferred-gpu")
    const renderingMode = document.getElementById("rendering-mode")
    const msaaQuality = document.getElementById("msaa-quality")
    const textureQuality = document.getElementById("texture-quality")
    const framerateLimit = document.getElementById("framerate-limit") // user input
    const lightingTechnology = document.getElementById("lighting-technology")
    
    window.pywebview.api.getGPUList().then(gpuList => {
        const menuItems = [
            {
                text: 'Automatic',
                click: function() {
                    window.pywebview.api.configureSetting("fflag-preferred-gpu", "auto");
                }
            }
        ];

        const gpuMenuItems = gpuList.map(gpuName => ({
            text: gpuName,
            click: function() {
                window.pywebview.api.configureSetting("fflag-preferred-gpu", gpuName);
            }
        }));

        const allMenuItems = menuItems.concat(gpuMenuItems);

        preferredGPU.addEventListener("click", function() {
            renderMenu(allMenuItems);
        })
    }).catch(error => {
        console.error("Error getting GPU list:", error);
    });

    renderingMode.addEventListener("click", function() {
        renderMenu([
            {
                text: 'Automatic',
                click: function() {
                    window.pywebview.api.configureSetting("fflag-rendering-mode", "auto")
                }
            },
            {
                text: 'Vulkan',
                click: function() {
                    window.pywebview.api.configureSetting("fflag-rendering-mode", "vulkan")
                }
            },
            {
                text: 'OpenGL',
                click: function() {
                    window.pywebview.api.configureSetting("fflag-rendering-mode", "opengl")
                }
            },
            {
                text: 'Direct3D 10',
                click: function() {
                    window.pywebview.api.configureSetting("fflag-rendering-mode", "d3d10")
                }
            },
            {
                text: 'Direct3D 11',
                click: function() {
                    window.pywebview.api.configureSetting("fflag-rendering-mode", "d3d11")
                }
            }
        ])}
    )
    
    msaaQuality.addEventListener("click", function() {
        renderMenu([
            {
                text: 'Automatic',
                click: function() {
                    window.pywebview.api.configureSetting("fflag-msaa-quality", "auto")
                }
            },
            {
                text: '1x',
                click: function() {
                    window.pywebview.api.configureSetting("fflag-msaa-quality", "1")
                }
            },
            {
                text: '2x',
                click: function() {
                    window.pywebview.api.configureSetting("fflag-msaa-quality", "2")
                }
            },
            {
                text: '4x',
                click: function() {
                    window.pywebview.api.configureSetting("fflag-msaa-quality", "4")
                }
            },
            {
                text: '8x (buggy)',
                click: function() {
                    window.pywebview.api.configureSetting("fflag-msaa-quality", "8")
                }
            },
            {
                text: '16x (buggy)',
                click: function() {
                    window.pywebview.api.configureSetting("fflag-msaa-quality", "16")
                }
            }
        ])}
    )
    
    textureQuality.addEventListener("click", function() {
        renderMenu([
            {
                text: 'Automatic',
                click: function() {
                    window.pywebview.api.configureSetting("fflag-texture-quality", "auto")
                }
            },
            {
                text: 'Lowest (0)',
                click: function() {
                    window.pywebview.api.configureSetting("fflag-texture-quality", "0")
                }
            },
            {
                text: 'Low (1)',
                click: function() {
                    window.pywebview.api.configureSetting("fflag-texture-quality", "1")
                }
            },
            {
                text: 'High (2)',
                click: function() {
                    window.pywebview.api.configureSetting("fflag-texture-quality", "2")
                }
            },
            {
                text: 'Highest (3)',
                click: function() {
                    window.pywebview.api.configureSetting("fflag-texture-quality", "3")
                }
            }
        ])}
    )
    
    lightingTechnology.addEventListener("click", function() {
        renderMenu([
            {
                text: 'Automatic',
                click: function() {
                    window.pywebview.api.configureSetting("fflag-lighting-technology", "auto")
                }
            },
            {
                text: 'Voxel',
                click: function() {
                    window.pywebview.api.configureSetting("fflag-lighting-technology", "voxel")
                }
            },
            {
                text: 'Shadow Map',
                click: function() {
                    window.pywebview.api.configureSetting("fflag-lighting-technology", "shadowmap")
                }
            },
            {
                text: 'Future',
                click: function() {
                    window.pywebview.api.configureSetting("fflag-lighting-technology", "future")
                }
            }
        ])}
    )
    
    // fastflags - ui & layout
    const fontSize = document.getElementById("font-size") // user input
    const guiHiding = document.getElementById("gui-hiding") // user input
    
    // fastflags - debugging
    const flagState = document.getElementById("flag-state") // user input
    
    // customization - bootstrapper
    const bootstrapperTheme = document.getElementById("bootstrapper-change-theme")
    const openBootstrapperFolder = document.getElementById("bootstrapper-themes-folder") // open folder
    
    // customization - roblox client
    const robloxTheme = document.getElementById("roblox-theme")
    const robloxFont = document.getElementById("roblox-font")
    const robloxMouseCursor = document.getElementById("roblox-mouse-cursor")
    
    robloxMouseCursor.addEventListener("click", function() {
        renderMenu([
            {
                text: 'Default',
                click: function() {
                    window.pywebview.api.configureSetting("customization-custom-cursor", "default")
                }
            },
            {
                text: 'Angular',
                click: function() {
                    window.pywebview.api.configureSetting("customization-custom-cursor", "angular")
                }
            },
            {
                text: 'Cartoony',
                click: function() {
                    window.pywebview.api.configureSetting("customization-custom-cursor", "cartoony")
                }
            }
        ])}
    )
    
    // deployment - roblox
    const deploymentChannel = document.getElementById("roblox-deployment-channel") // user input or maybe a dynamic list (???)

})

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
            option.click();
            window.pywebview.api.updateFrontendConfigDisplays();
        });
        menuContainer.appendChild(interactable);
    });

    document.getElementById("screenContent").style.backdropFilter = "blur(5px)";
    document.getElementById('itemMenu').style.scale = "1";
    document.getElementById('itemMenu').style.opacity = "1";
    document.getElementById('focusScreen').style.zIndex = "2";
}