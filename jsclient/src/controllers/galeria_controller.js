import { Controller } from "stimulus"

export default class GaleriaController extends Controller {

    photoRemoved(event) {
        const el = event.target
        el.parentNode.removeChild(el);
    }

}
