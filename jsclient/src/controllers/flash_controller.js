import { Controller } from "stimulus";

export default class extends Controller {

    connect() {
        M.toast({
            html: this.element.innerHTML,
            classes: 'rounded yellow darken-4'
        })
    }

}
