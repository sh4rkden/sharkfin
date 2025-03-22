
class SwitchElement extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        this.shadowRoot.innerHTML = `
            <style>
                .switch {
                    position: relative;
                    display: inline-block;
                    width: 50px;
                    height: 26px;
                }
                .switch input {
                    opacity: 0;
                    width: 0;
                    height: 0;
                }
                .slider {
                    position: absolute;
                    cursor: pointer;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background-color: #E1E1E1;
                    transition: 0.2s ease;
                    border-radius: 14px;
                }
                .slider:before {
                    content: "";
                    position: absolute;
                    height: 22px;
                    width: 22px;
                    left: 3px;
                    top: 2px;
                    background-color: white;
                    transition: 0.2s ease;
                    border-radius: 50%;
                    transform: translateX(0) scale(1);
                    transform-origin: center;
                }
                input:checked + .slider {
                    background-color: #0078D4;
                }
                input:checked + .slider:before {
                    transform: translateX(22px) scale(1);
                }
                input:focus + .slider {
                    box-shadow: 0 0 1px #0078D4;
                }
            </style>
            <label class="switch">
                <input type="checkbox">
                <span class="slider"></span>
            </label>
        `;
    }
    
    connectedCallback() {
        if (this.hasAttribute("value")) {
            this.checked = this.getAttribute("value") === "true";
        }
    }
    
    get checked() {
        return this.shadowRoot.querySelector("input").checked;
    }
    
    set checked(val) {
        this.shadowRoot.querySelector("input").checked = val;
    }
    
    toggle() {
        this.checked = !this.checked;
    }
}
    
customElements.define("switch-toggle", SwitchElement);
    
function toggleSwitch(dataId, value) {
    const el = document.querySelector('switch-toggle[data-id="' + dataId + '"]');
    if (el) {
        el.checked = value;
    }
}
    
function getSwitchValue(dataId) {
    const el = document.querySelector('switch-toggle[data-id="' + dataId + '"]');
    return el ? el.checked : null;
}
