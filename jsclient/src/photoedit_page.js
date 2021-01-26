import { Application, Controller } from "stimulus";
import ChipsController from "./controllers/chips_controller";
import EditorExcerptController from "./controllers/excerptEditor";

class PhotoEditForm extends Controller {

    static targets = ["submit", "excerpt", "chips"]

    connect() {
        this.enableSubmit()
    }

    disableSubmit() {
        this.submitTarget.classList.add('disabled')
    }

    enableSubmit() {
        this.submitTarget.classList.remove('disabled')
    }

    onSubmit(event) {
        event.preventDefault()
        event.stopPropagation()
        this.disableSubmit()

        this.application.getControllerForElementAndIdentifier(
            this.chipsTarget, 'chips').saveToInput()

        const excerptEditor = this.application.getControllerForElementAndIdentifier(
            this.excerptTarget, 'editor'
        )

        excerptEditor.getData().then(data => {
            excerptEditor.saveToInput(data)

            this.enableSubmit()
            this.element.submit()
        }).catch( error => {
            console.log(error)
            this.enableSubmit()
        })
    }

}

const application = Application.start();
application.register('chips', ChipsController);
application.register('editor', EditorExcerptController);
application.register('PhotoEditForm', PhotoEditForm);
