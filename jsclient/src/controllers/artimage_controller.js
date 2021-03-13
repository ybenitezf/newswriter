import { Controller } from "stimulus";

export default class extends Controller {
    
    static targets = ["image"]

    connect() {
        if (this.imageTarget.classList.contains('materialboxed')) {
            this.instance = M.Materialbox.init(this.imageTarget, {});
        }
    }

    disconnect() {
        if ( this.instance ) {
            this.instance.destroy();
        }
    }

}
