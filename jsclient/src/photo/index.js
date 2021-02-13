import Icon from "./camera.svg";

const preloader_content = `<div class="spinner-layer spinner-blue-only">
<div class="circle-clipper left">
<div class="circle"></div>
</div><div class="gap-patch">
<div class="circle"></div>
</div><div class="circle-clipper right">
<div class="circle"></div>
</div>
</div>
`

export default class Photo {

    constructor({ data, config, api, readOnly }) {
        /**
         * data should have:
         * url: image url
         * caption: photo caption
         * credits: photo credits
         * ...
         */
        this.config = config
        this.data = {
            file: data.file || { url: "" },
            caption: data.caption || "",
            credit: data.credit || ""
        }
        this.api = api
        this.readOnly = readOnly || false

        this.ui = {
            wrapper: make('div', ['py-2'])
        }
        this.ui.upload = {}
        this.ui.uploading = {
            // UPLOADING VIEW
            wrapper: make(
                'div', ['center', 'hide']),
            inner: make(
                'div', ['preloader-wrapper', 'active', 'hide'])
        }
        this.ui.uploading.wrapper.appendChild(this.ui.uploading.inner)
        this.ui.uploading.inner.innerHTML = preloader_content
        this.ui.image = {
            // IMAGE VIEW
            wrapper: make('div', ['hide']),
            img_wrapper: make('div', 'center'),
            image: make('img', 'responsive-img', {
                src: ''
            }),
            captionInput: make('div', this.api.styles.input, {
                contentEditable: !this.readOnly,
            }),
            creditInput: make('div', this.api.styles.input, {
                contentEditable: !this.readOnly,
            })
        }
        this.ui.image.wrapper.appendChild(this.ui.image.img_wrapper)
        this.ui.image.img_wrapper.appendChild(this.ui.image.image)
        this.ui.image.wrapper.appendChild(this.ui.image.captionInput)
        this.ui.image.wrapper.appendChild(this.ui.image.creditInput)

        this.ui.upload = {
            // UI elements
            wrapper: make('div', ['file-field', 'input-field', 'hide']),
            btn: make('div', ['btn']),
            btn_text: make('span', []),
            fileInput: make('input', [], {
                type: 'file',
                name: 'archive',
                accept: '.zip,application/gzip,application/zip'
            }),
            file_path: make('div', ['file-path-wrapper']),
            showfilename: make('input', ['file-path', 'validate'], {
                placeholder: "Seleccionar .zip de photostore"
            })
        }

        /**
         * EMPTY VIEW
         * <div class="file-field input-field">
         *  <div class="btn">
         *    <span>File</span>
         *    <input type="file" multiple>
         *  </div>
         *  <div class="file-path-wrapper">
         *   <input class="file-path validate" type="text" placeholder="...">
         *  </div>
         * </div>
         */
        this.ui.upload.btn_text.innerHTML = "Archivo"
        this.ui.upload.btn.appendChild(this.ui.upload.btn_text)
        this.ui.upload.btn.appendChild(this.ui.upload.fileInput)
        this.ui.upload.file_path.appendChild(this.ui.upload.showfilename)
        this.ui.upload.wrapper.appendChild(this.ui.upload.btn)
        this.ui.upload.wrapper.appendChild(this.ui.upload.file_path)

        this.ui.upload.fileInput.addEventListener('change', () => {
            this.fileSelected()
        })

        // TODO: append the image part to
        this.ui.wrapper.appendChild(this.ui.upload.wrapper)
        this.ui.wrapper.appendChild(this.ui.uploading.wrapper)
        this.ui.wrapper.appendChild(this.ui.image.wrapper)
        // EMPTY, UPLOADING,  FILLED, ERROR
        if (!this.data.file.url) {
            this.setState('EMPTY')
        } else {
            this.setState('FILLED')
        }
    }

    upload(file) {
        var formData = new FormData();
        formData.append('archive', file);
        fetch(this.config.endpoints.byFile, {
            method: 'POST',
            body: formData
        }).then(
            response => response.json()
        ).then(data => {
            if (data.success != 1) {
                this.setState('ERROR');
                this.api.notifier.show({
                    message: "El archivo no es valido, intente con otro",
                    style: 'error',
                });
            } else {
                this.data.file = data.file
                this.data.credit = data.credit
                this.data.caption = data.caption
                this.setState('FILLED')
            }
        }).catch(error => {
            this.setState('ERROR');
            this.api.notifier.show({
                message: "Error en el servidor, imposible mandar archivo",
                style: 'error',
            });
            console.log(error)
        })
    }

    dataToImage() {
        // take this.data and fill image component
        var cmp = this.ui.image;
        cmp.image.src = this.data.file.url
        cmp.captionInput.innerHTML = this.data.caption
        cmp.creditInput.innerHTML = this.data.credit
    }

    fileSelected() {
        // hide this.ui.upload
        // show preloader
        this.setState('UPLOADING')
        this.upload(this.ui.upload.fileInput.files[0])
    }

    setState(state) {
        switch (state) {
            case "UPLOADING":
                this.ui.uploading.wrapper.classList.remove('hide')
                this.ui.upload.wrapper.classList.add('hide')
                this.ui.image.wrapper.classList.add('hide')
                break;
            case "FILLED":
                this.dataToImage()
                this.ui.uploading.wrapper.classList.add('hide')
                this.ui.upload.wrapper.classList.add('hide')
                this.ui.image.wrapper.classList.remove('hide')
                break;
            case "ERROR":
                this.ui.uploading.wrapper.classList.add('hide')
                this.ui.upload.wrapper.classList.remove('hide')
                this.ui.image.wrapper.classList.add('hide')
                this.ui.upload.showfilename.classList.add("invalid")
            default:
                this.ui.uploading.wrapper.classList.add('hide')
                this.ui.upload.wrapper.classList.remove('hide')
                this.ui.image.wrapper.classList.add('hide')
                break;
        }
    }

    static get toolbox() {
        return {
            title: 'Foto',
            icon: Icon
        };
    }

    render() {
        return this.ui.wrapper
    }

    save(blockContent) {
        // REVIEW: what to do with empty data
        if (!this.data.file.url) {
            this.data.caption = this.ui.image.captionInput.innerHTML
            this.data.credit = this.ui.image.creditInput.innerHTML
            return this.data
        } else {
            return null
        }
    }

    /**
     * Fires after clicks on the Toolbox Image Icon
     * Initiates click on the Select File button
     *
     * @public
     */
    rendered() {
        if (!this.data.file.url) {
            this.ui.upload.fileInput.click();
        }
    }
}

/**
 * Helper for making Elements with attributes
 *
 * @param  {string} tagName           - new Element tag name
 * @param  {Array|string} classNames  - list or name of CSS class
 * @param  {object} attributes        - any attributes
 * @returns {Element}
 */
export const make = function make(tagName, classNames = null, attributes = {}) {
    const el = document.createElement(tagName);

    if (Array.isArray(classNames)) {
        el.classList.add(...classNames);
    } else if (classNames) {
        el.classList.add(classNames);
    }

    for (const attrName in attributes) {
        el[attrName] = attributes[attrName];
    }

    return el;
};
