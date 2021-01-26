import { Controller } from "stimulus";
import EditorJS from "@editorjs/editorjs";
import validate, { async } from "validate.js";
const Validator = require('validate.js');
const Uppy = require("@uppy/core");
const XHRUpload = require("@uppy/xhr-upload");
const Dashboard = require("@uppy/dashboard");
const SpanishUppy = require("@uppy/locales/lib/es_ES");
const axios = require('axios').default;

require('@uppy/core/dist/style.css')
require('@uppy/dashboard/dist/style.css')

const restricciones = {
    headline: {
        presence: {
            allowEmpty: false,
            message: "^Título no puede estar vacio"
        }
    },
    creditline: {
        presence: {
            allowEmpty: false,
            message: "^Debes poner los creditos"
        }
    },
    keywords: {
        presence: {
            allowEmpty: false,
            message: "^Debes incluir palabras clave"
        }
    },
    files: {
        presence: {
            allowEmpty: false,
            message: "^Debes seleccionar al menos una foto"
        }
    },
    excerpt: {
        presence: {
            allowEmpty: false,
            message: "^Describe estas imágenes"
        },
        length: function (value, attributes, attributeName, options, constraints) {
            if ( value ) {
                if ( validate.isEmpty(value.blocks) ) {
                    return {message: "^Describe estas imágenes"}
                } else {
                    return null
                }
            }

            return false
        }
    }
}

export default class  CoverageUploadController extends Controller {

    static targets = [
        "resumen", "tags", "headline", "creditline", "photos", "takenby",
        "sendbtn"
    ]

    static values = {
        uploadendpoint: String,
        api: String,
        postback: String
    }

    disableGuardar() {
        this.sendbtnTarget.classList.add('disabled')
    }
    
    enableGuardar() {
        this.sendbtnTarget.classList.remove('disabled')
    }

    connect() {
        this.editor = new EditorJS({
            holder: this.resumenTarget.id,
            minHeight: 20,
            placeholder: "Escribe aquí una descripción de la cobertura"
        })
        M.Chips.init(this.tagsTarget, {
            placeholder: "Plabras clave",
            secondaryPlaceholder: "+Palabra"
        });

        this.uppy = new Uppy({
            autoProceed: false,
            locale: SpanishUppy,
            restrictions: {
                allowedFileTypes: ['image/*']
            }
        }).use(Dashboard, {
            inline: true,
            hideUploadButton: true,
            target: this.photosTarget,
            height: 480
        }).use(XHRUpload, {
            fieldName: 'image',
            endpoint: this.uploadendpointValue,
            limit: 4,
            timeout: 60 * 1000
        })

        this.enableGuardar()
    }

    disconnect() {
        if (this.editor) {
            this.editor.destroy()
        }
    }

    isValid(values) {
        // validar el formulario
        const results = Validator(values, restricciones)

        if (results) {
            // aqui hay errores
            for (const [field, msg] of Object.entries(results) ) {
                M.toast({
                    html: msg,
                    classes: 'red rounded'
                });
            }
            return false
        }
        
        return true
    }

    save(event) {
        event.preventDefault();
        event.stopPropagation();
        this.disableGuardar();

        // recopilar los datos, el editor tiene prioridad
        var tags = [];
        M.Chips.getInstance(this.tagsTarget).chipsData.forEach((tagData) => {
          tags.push(tagData.tag);
        })
        this.editor.save().then((description) => {

            var values = {
                headline: this.headlineTarget.value,
                creditline: this.creditlineTarget.value,
                takenby: this.takenbyTarget.value,
                keywords: tags,
                excerpt: description,
                files: this.uppy.getFiles()
            }
            const postback = this.postbackValue

            if (this.isValid(values)) {
                // agregar información a los metas de las imagenes
                // values.excerpt debe ser convertido a string
                values.excerpt = JSON.stringify(description)
                // values.keywords debe ser json tambien pues es una lista
                values.keywords = JSON.stringify(tags)
                // --
                // eliminar los files de aqui tambien
                delete values.files
                this.uppy.setMeta(values)

                // intentar mandar las fotos 
                this.uppy.upload().then((result) => {
                    var fotos = []
                    if (result.successful.length > 0) {
                        result.successful.forEach((file) => {
                            // copiamos los ids de las fotos que se subieron
                            // correctamente
                            fotos.push(file.response.body.md5)
                        })
                        // enviar la información al servidor
                        var payload = {
                            keywords: tags,
                            photos: fotos,
                            excerpt: JSON.stringify(description),
                            headline: this.headlineTarget.value,
                            credit_line: this.creditlineTarget.value
                        }
                        axios.post(this.apiValue, payload).then(function (response) {
                            M.toast({html: 'Tus cambios han sido guardados', classes: 'rounded'})
                            window.location.replace(postback);
                          }).catch( function (error) {
                            M.toast({
                              html: '<b>ERROR</b>: No se pudo guardar, error en el servidor',
                              classes: 'rounded red darken-4'
                            })
                            console.log(error)
                          })
                    } else {
                        // no se pudo subir nada correctamente, aqui pasa
                        // algo raro
                        M.toast({
                            html: "Algo esta mal con el servidor",
                            classes: 'red rounded'
                        });
                    }
                })
            }

        })

        this.enableGuardar();
    }

}
