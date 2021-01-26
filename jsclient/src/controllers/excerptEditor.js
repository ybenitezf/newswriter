import { Controller } from "stimulus"
import EditorJS from "@editorjs/editorjs";

export default class EditorExcerptController extends Controller {
    static values = { placeholder: String, minheight: Number }
    static targets = ["editor", "input"]

    connect() {
        var data = JSON.parse(this.inputTarget.value)
        const placeholder = this.hasPlaceholderValue ? this.placeholderValue: 'Escribe aqui'
        const minHeight = this.hasMinheightValue ? this.minheightValue: 20
        this.editor = new EditorJS({
            holder: this.editorTarget.id,
            minHeight: minHeight,
            data: data,
            placeholder: placeholder
        })
    }

    disconnect() {
        if (this.editor) {
            this.editor.destroy()
        }
    }

    getData() {
        return this.editor.save()
    }

    saveToInput(data) {
        this.inputTarget.value = JSON.stringify(data)
    }
}
