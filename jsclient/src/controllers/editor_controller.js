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

const axios = require('axios').default;

export default class EditorController extends Controller {

  static targets = [
    "content", "headline", "creditline", "tags", "toolbox"]
  static values = {
    author: String,
    apiendpoint: String,
    imageupload: String,
    imagefetchurl: String,
    linkendpoint: String
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
        rawCode: {
          class: RawTool,
          config: {
            placeholder: 'Pegar código aqui'
          }
        }
      },
      i18n: {},
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

  guardar(event) {
    // desactivar el boton un momento
    const apiUrl = this.apiendpointValue;
    this.disableGuardar();
    var keywords = [];
    M.Chips.getInstance(this.tagsTarget).chipsData.forEach((tagData) => {
      keywords.push(tagData.tag);
    })

    this.editor.save().then( (editorData) => {
      const outData = {
        headline: this.headlineTarget.value,
        creditline: this.creditlineTarget.value,
        keywords: keywords,
        content: editorData
      }
      axios.post(apiUrl, outData).then(function (response) {
        M.toast({html: 'Tus cambios han sido guardados', classes: 'rounded'})
      }).catch( function (error) {
        M.toast({
          html: '<b>ERROR</b>: No se pudo guardar, error en el servidor',
          classes: 'rounded red darken-4'
        })
        console.log('Saving failed: ', error)
      })
    });

    this.enableGuardar()
  }

  disconnect() {
    if (this.editor) {
      this.editor.destroy();
    }
  }

}
