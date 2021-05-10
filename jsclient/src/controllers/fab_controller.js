import { Controller } from "stimulus";

export default class extends Controller {

    connect() {
        this.instance = M.FloatingActionButton.init(this.element, {});
    }

    disconnect() {
        if (this.instance) {
            this.instance.destroy();
        }
    }

}
