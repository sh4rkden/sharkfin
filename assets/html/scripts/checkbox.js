document.addEventListener('DOMContentLoaded', () => {
    const preloader = document.createElement('checkbox-toggle');
    preloader.style.cssText = 'position: absolute; top: -9999px; visibility: hidden;';
    document.body.appendChild(preloader);
});

const checkboxTemplate = document.createElement('template');
checkboxTemplate.innerHTML = `
    <style>
        :host {
            display: inline-block;
            margin: 0;
            padding: 0;
            line-height: 0;
            vertical-align: middle;
            contain: content;
        }
        .checkbox {
            position: relative;
            display: inline-block;
            width: 42px;
            height: 42px;
            background: url('/assets/images/checkbox.webp') no-repeat center;
            background-size: contain;
            cursor: pointer;
        }
        .checkbox img {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: none;
            user-select: none;
            pointer-events: none;
            will-change: transform;
        }
        .checkbox.checked img.check {
            display: block;
        }
        .checkbox:not(.checked) img.mark {
            display: block;
        }
        @keyframes bounce-translate {
            0% { transform: translateY(0); }
            30% { transform: translateY(-8px); }
            50% { transform: translateY(0); }
            70% { transform: translateY(-4px); }
            100% { transform: translateY(0); }
        }
        .bounce-translate {
            animation: bounce-translate 400ms ease-out;
        }
        @keyframes bounce-scale {
            0% { transform: scale(0.9); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
        .bounce-scale {
            animation: bounce-scale 350ms cubic-bezier(0.28, 0.84, 0.42, 1) both;
        }
    </style>
    <div class="checkbox">
        <img class="check" src="/assets/images/check.webp" alt="Checked" draggable="false">
        <img class="mark" src="/assets/images/cross.webp" alt="Not Checked" draggable="false">
    </div>
`;

class CheckboxElement extends HTMLElement {
    constructor() {
        super();
        this._checked = false;
        this.attachShadow({ mode: 'open' });
        this.shadowRoot.appendChild(checkboxTemplate.content.cloneNode(true));
    }

    connectedCallback() {
        this._checkbox = this.shadowRoot.querySelector('.checkbox');
        this._checkImage = this.shadowRoot.querySelector('.check');
        this._markImage = this.shadowRoot.querySelector('.mark');

        if (this.hasAttribute('value')) {
            this._checked = this.getAttribute('value') === 'true';
        }

        this._checkImage.addEventListener('animationend', () => {
            this._checkImage.classList.remove('bounce-translate');
        });
        this._markImage.addEventListener('animationend', () => {
            this._markImage.classList.remove('bounce-scale');
        });

        this._pointerDownHandler = this.toggle.bind(this);
        this._checkbox.addEventListener('pointerdown', this._pointerDownHandler, { passive: true });
        this.updateUI();
    }

    disconnectedCallback() {
        this._checkbox.removeEventListener('pointerdown', this._pointerDownHandler);
    }

    get checked() {
        return this._checked;
    }

    set checked(val) {
        this._checked = Boolean(val);
        this.updateUI();
    }

    toggle() {
        this.checked = !this.checked;
        this.dispatchEvent(new Event('change', { bubbles: true, composed: true }));

        const targetImage = this.checked ? this._checkImage : this._markImage;
        const animationClass = this.checked ? 'bounce-translate' : 'bounce-scale';
        requestAnimationFrame(() => {
            targetImage.classList.add(animationClass);
        });
    }

    updateUI() {
        if (this._checkbox) {
            this._checkbox.classList.toggle('checked', this._checked);
        }
    }
}

customElements.define('checkbox-toggle', CheckboxElement);

function toggleCheckbox(dataId, value) {
    const el = document.querySelector(`checkbox-toggle[data-id="${dataId}"]`);
    if (el) {
        el.checked = value;
    }
}

function getCheckboxValue(dataId) {
    const el = document.querySelector(`checkbox-toggle[data-id="${dataId}"]`);
    return el ? el.checked : null;
}
