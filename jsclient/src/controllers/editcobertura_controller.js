import { Controller } from "stimulus";
import validate from "validate.js";
const Validator = require('validate.js');

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

export default class EditCoberturaController extends Controller {
    static values = { apiendpoint: String }
    static targets = [ "headline", "creditline", "tags", "excerpt", "updatephotos", "btn" ]

    objectToQueryString(obj) {
        return Object.keys(obj).map(key => key + '=' + obj[key]).join('&');
    }

    connect() {
        this.btnTarget.classList.remove('disabled')
    }

    disconnect() {
        this.btnTarget.classList.add('disabled')
    }

    isValid(values) {
        // validar el formulario
        const results = Validator(values, restricciones)

        if (results) {
            // aqui hay errores
            for (const [field, msg] of Object.entries(results) ) {
                M.toast({
                    html: msg,
                    classes: 'red rounded darken-4'
                });
            }
            return false
        }
        
        return true
    }

    guardar(event) {
        var btn = this.btnTarget
        btn.classList.add('disabled')
        var tags = this.application.getControllerForElementAndIdentifier(
            this.tagsTarget, "chips").getValuesAsList()
        const headline = this.headlineTarget.value
        const creditline = this.creditlineTarget.value
        var apiendpoint = this.apiendpointValue + '?'
        apiendpoint += this.objectToQueryString(
            {updatephotos: this.updatephotosTarget.checked})

        this.application.getControllerForElementAndIdentifier(
            this.excerptTarget, "editor"
        ).getData().then((data) => {
            if(this.isValid({
                headline: headline,
                creditline: creditline,
                keywords: tags,
                excerpt: data
            })){

                fetch(apiendpoint, {
                    method: 'PUT',
                    body: JSON.stringify({
                        id: '',
                        excerpt: JSON.stringify(data),
                        headline: headline,
                        credit_line: creditline,
                        photos: [],
                        keywords: tags
                    }),
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }).then( function(r) {
                    if (r.ok) {
                        M.toast({
                            html: 'Se guardaron los cambios',
                            classes: 'rounded'
                        })
                        btn.classList.remove('disabled')
                    } else {
                        M.toast({
                            html: '<b>ERROR</b>: El servidor respondio con error',
                            classes: 'rounded red darken-4'
                        })
                        btn.classList.remove('disabled')
                    }
                }).catch( function(error) {
                    M.toast({
                        html: '<b>ERROR</b>: No se pudo enviar la petición',
                        classes: 'rounded red darken-4'
                    })
                    console.log(error)
                    btn.classList.remove('disabled')
                });

            } else { // No es valido, faltan datos
                btn.classList.remove('disabled')
                M.toast({
                    html: 'Hay errores en el formulario',
                    classes: 'rounded red darken-4'
                })
            }

        })
    }

}
