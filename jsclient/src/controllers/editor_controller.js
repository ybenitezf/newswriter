import { Controller } from "stimulus";
import ImageTool from '@editorjs/image';
import EditorJS from '@editorjs/editorjs';
import Quote from '@editorjs/quote';
import List from '@editorjs/list';
import Delimiter from '@editorjs/delimiter';
import Warning from '@editorjs/warning';
import Paragraph from '@editorjs/paragraph';
import Header from '@editorjs/header';
import LinkTool from '@editorjs/link';
import RawTool from '@editorjs/raw';
import validate, { async } from "validate.js";
import Photo from "../photo";

const axios = require('axios').default;
const Validator = require('validate.js');
const AttachesTool = require('@editorjs/attaches');

var contrains = {
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
  summary: {
    presence: {
      allowEmpty: false,
      message: "^Debes escribir el resumen"
    }
  },
  keywords: {
    presence: {
      allowEmpty: false,
      message: "^Debes incluir palabras clave"
    }
  },
  content: {
    presence: {
      allowEmpty: false,
      message: "^El trabajo no tiene contenido"
    },
    length: function (value, attributes, attributeName, options, constraints) {
      if (value) {
        if (validate.isEmpty(value.blocks)) {
          return { message: "^El trabajo no tiene contenido" }
        } else {
          return false
        }
      }

      return false
    }
  }
}

export default class EditorController extends Controller {

  static targets = [
    "content", "headline", "creditline", "tags", "toolbox",
    "summary"
  ]
  static values = {
    author: String,
    apiendpoint: String,
    imageupload: String,
    imagefetchurl: String,
    photoupload: String,
    linkendpoint: String,
    attachupload: String
  }

  initialize() {
    this.loadEditorJS.bind(this)
  }

  connect() {
    const apiUrl = this.apiendpointValue;
    M.Chips.init(this.tagsTarget, {
      placeholder: "Plabras clave"
    });
    // cargar datos del editor desde remoto
    axios.get(apiUrl).then(
      (response) => this.loadEditorJS(response.data)
    ).catch((error) => {
      this.loadEditorJS({})
      console.log(error)
      console.log("No pude cargar " + apiUrl)
      M.toast({
        html: '<b>ERROR</b>: No se pudo recuperar la información',
        classes: 'rounded red darken-4'
      })
    })
  }

  loadEditorJS(data) {
    M.FloatingActionButton.init(this.toolboxTarget, {});

    this.headlineTarget.value = data.headline;
    this.creditlineTarget.value = data.creditline;
    this.summaryTarget.value = data.summary;
    M.textareaAutoResize(this.summaryTarget);
    var tags = M.Chips.getInstance(this.tagsTarget);
    if (data.keywords) {
      data.keywords.forEach((keyword) =>
        tags.addChip({
          tag: keyword
        })
      )
    }
    this.editor = new EditorJS({
      holder: this.contentTarget.id,

      tools: {
        paragraph: {
          class: Paragraph,
          inlineToolbar: true,
        },
        list: {
          class: List,
          inlineToolbar: true,
        },
        header: {
          class: Header,
          config: {
            levels: [2, 3],
            defaultLevel: 2,
            placeholder: 'Escribe un título'
          }
        },
        image: {
          class: ImageTool,
          inlineToolbar: true,
          config: {
            buttonContent: "Seleccionar una imágen",
            captionPlaceholder: "Pie de foto",
            creditPlaceholder: "Creditos",
            endpoints: {
              byFile: this.imageuploadValue,
              byUrl: this.imagefetchurlValue,
            }
          }
        },
        delimiter: Delimiter,
        photo: {
          class: Photo,
          inlineToolbar: true,
          config: {
            endpoints: {
              byFile: this.photouploadValue
            }
          }
        },
        quote: {
          class: Quote,
          inlineToolbar: true,
          shortcut: 'CMD+SHIFT+O',
          config: {
            quotePlaceholder: 'Entre la cita',
            captionPlaceholder: 'Autor de la cita',
          },
        },
        linkTool: {
          class: LinkTool,
          config: {
            endpoint: this.linkendpointValue
          }
        },
        warning: {
          class: Warning,
          inlineToolbar: true,
          shortcut: 'CMD+SHIFT+W',
          config: {
            titlePlaceholder: 'Title',
            messagePlaceholder: 'Message',
            author: this.authorValue
          },
        },
        attaches: {
          class: AttachesTool,
          config: {
            endpoint: this.attachuploadValue,
            buttonText: "Seleccione archivo",
            errorMessage: "Error al cargar el archivo"
          }
        },
        rawCode: {
          class: RawTool,
          config: {
            placeholder: 'Pegar código aqui'
          }
        }
      },
      i18n: {
        messages: {
          ui: {
            // Translations of internal UI components of the editor.js core
            "blockTunes": {
              "toggler": {
                "Click to tune": "Clic para configurar"
              },
            },
            "inlineToolbar": {
              "converter": {
                "Convert to": "Covertir a"
              }
            },
            "toolbar": {
              "toolbox": {
                "Add": "Agregar"
              }
            }
          },
          toolNames: {
            // Section for translation Tool Names: both block and inline tools
            "Heading": "Titulo",
            "Text": "Párrafo",
            "List": "Lista",
            "Image": "Imagen",
            "Delimiter": "Separador",
            "Quote": "Cita",
            "Link": "Enlace",
            "Warning": "Aviso",
            "Raw HTML": "Código HTML",
            "Attaches": "Adjunto",
            "Bold": "Negrita",
            "Italic": "Italica"
          },
          tools: {
            // Section for passing translations to the external tools classes
            // The first-level keys of this object should be equal of keys ot the 'tools' property of EditorConfig
            "image": {

            }
          },
          blockTunes: {
            // Section allows to translate Block Tunes
            "delete": {
              "Delete": "Eliminar"
            },
            "moveUp": {
              "Move up": "Mover arriba"
            },
            "moveDown": {
              "Move down": "Mover abajo"
            }
          },
        }
      },
      placeholder: 'Da clic aquí para comenzar a escribir',
      data: data.content ? data.content : {},
      logLevel: 'VERBOSE',
      onReady: () => {
        this.enableGuardar()
      }
    });
  }

  disableGuardar() {
    var el = document.querySelector('*[data-action="editor#guardar"]')
    el.classList.add('disabled')
  }

  enableGuardar() {
    var el = document.querySelector('*[data-action="editor#guardar"]')
    el.classList.remove('disabled')
  }

  validate(values) {
    const results = Validator(values, contrains);

    if (results) {
      // show errors
      for (const [field, msg] of Object.entries(results)) {
        M.toast({
          html: msg,
          classes: 'rounded red darken-4'
        });
      }
      return false
    }

    return true;
  }

  guardar(event) {
    // desactivar el boton un momento
    const apiUrl = this.apiendpointValue;
    this.disableGuardar();
    var keywords = [];
    M.Chips.getInstance(this.tagsTarget).chipsData.forEach((tagData) => {
      keywords.push(tagData.tag);
    })

    this.editor.save().then((editorData) => {

      const outData = {
        headline: this.headlineTarget.value,
        creditline: this.creditlineTarget.value,
        summary: this.summaryTarget.value,
        keywords: keywords,
        content: editorData
      }

      if (this.validate(outData)) {
        axios.post(apiUrl, outData).then(function (response) {
          M.toast({ html: 'Tus cambios han sido guardados', classes: 'rounded' })
        }).catch(function (error) {
          M.toast({
            html: '<b>ERROR</b>: No se pudo guardar, error en el servidor',
            classes: 'rounded red darken-4'
          })
          console.log('Saving failed: ', error)
        });
      }

    });

    this.enableGuardar()
  }

  disconnect() {
    if (this.editor) {
      this.editor.destroy();
    }
  }

}
