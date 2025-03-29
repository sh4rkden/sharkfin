const itemMenu = document.getElementById("itemMenu")

window.addEventListener("pywebviewready", function() {
    setTimeout(() => {
        document.getElementById("contextMenuContent").style.backdropFilter = "blur(0px)";
        document.getElementById('sharkfinscreen').style.scale = "0.8";
        document.getElementById('sharkfinscreen').style.opacity = "0";
    }, 1000)
    
    setTimeout(() => {
        document.getElementById('contextMenuScreen').style.zIndex = "-1";
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
    
    ffEditor.addEventListener("click", function() {
        document.getElementById("fflagEditorContent").style.backdropFilter = "blur(5px)";
        document.getElementById('fflagEditor').style.scale = "1";
        document.getElementById('fflagEditor').style.opacity = "1";
        document.getElementById('fflagEditorScreen').style.zIndex = "2";
    })

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
    
    window.pywebview.api.configureSetting("fflag-framerate-limit").then(framerate => {
        framerateLimit.value = framerate;
    }).catch(error => {
        framerateLimit.value = "-1";
        console.log("Error getting framerate limit:", error)
    })

    framerateLimit.addEventListener("change", function() {
        window.pywebview.api.configureSetting("fflag-framerate-limit", framerateLimit.value)
    })

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
    const guiHiding = document.getElementById("gui-hiding") // user input
    
    window.pywebview.api.configureSetting("fflag-interface-gui-hiding").then(groupId => {
        guiHiding.value = groupId;
    }).catch(error => {
        guiHiding.value = "0";
        console.log("Error getting framerate limit:", error)
    })

    guiHiding.addEventListener("change", function() {
        window.pywebview.api.configureSetting("fflag-interface-gui-hiding", guiHiding.value)
    })

    // customization - bootstrapper
    const loaderTheme = document.getElementById("loader-change-theme")
    const openBootstrapperFolder = document.getElementById("bootstrapper-themes-folder") // open folder
    
    loaderTheme.addEventListener("click", function() {
        window.pywebview.api.getLoaderThemeList().then(themeList => {
            const themesList = themeList.map(theme => ({
                text: theme,
                click: function() {
                    window.pywebview.api.configureSetting("sharkfin-loader-name", theme);
                }
            }));
    
            renderMenu(themesList);
        }).catch(error => {
            console.error("Error getting Theme list:", error);
        });
    })

    // customization - roblox client
    const robloxTheme = document.getElementById("roblox-theme")
    const robloxFont = document.getElementById("roblox-font")
    const fontSize = document.getElementById("font-size") // user input
    const robloxMouseCursor = document.getElementById("roblox-mouse-cursor")
    
    window.pywebview.api.configureSetting("customization-font-size").then(size => {
        fontSize.value = size;
    }).catch(error => {
        fontSize.value = "1";
        console.log("Error getting font size:", error)
    })

    fontSize.addEventListener("change", function() {
        window.pywebview.api.configureSetting("customization-font-size", fontSize.value)
    })
    
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
    const deploymentChannel = document.getElementById("deployment-channel") // user input or maybe a dynamic list (???)

    window.pywebview.api.configureSetting("deployment-roblox-channel").then(channel => {
        deploymentChannel.value = channel;
        window.pywebview.api.getClientSettings().then(result => {
            const [version, clientVersion] = result;
            document.getElementById("version").innerText = version;
            document.getElementById("versionguid").innerText = clientVersion;
        })
    }).catch(error => {
        deploymentChannel.value = "production";
        console.log("Error getting font size:", error)
    })

    deploymentChannel.addEventListener("change", function() {
        window.pywebview.api.configureSetting("deployment-roblox-channel", deploymentChannel.value)
        window.pywebview.api.getClientSettings().then(result => {
            const [version, clientVersion] = result;
            console.log(version, clientVersion)
            document.getElementById("version").innerText = version;
            document.getElementById("versionguid").innerText = clientVersion;
        })
    })
})

function hideMenu() {
    document.getElementById("contextMenuContent").style.backdropFilter = "blur(0px)";
    document.getElementById('itemMenu').style.scale = "0.8";
    document.getElementById('itemMenu').style.opacity = "0";
    setTimeout(() => {
        document.getElementById('contextMenuScreen').style.zIndex = "-1";
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
            
            // slight delay cuz of config not updating fast enough i think
            setTimeout(() => {
                window.pywebview.api.updateFrontendConfigDisplays();
            }, 10)
        });
        menuContainer.appendChild(interactable);
    });

    document.getElementById("contextMenuContent").style.backdropFilter = "blur(5px)";
    document.getElementById('itemMenu').style.scale = "1";
    document.getElementById('itemMenu').style.opacity = "1";
    document.getElementById('contextMenuScreen').style.zIndex = "2";
}