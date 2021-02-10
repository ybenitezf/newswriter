import { Controller } from "stimulus"

/**
 * Materializecss sidenav activator component
 * 
 * User as a button or link, and pass the id of the sidenav as a value
 * to the stimulus component, example:
 * 
 * <a href="#" 
 *    data-target="slide-out" <!-- for Materialize -->
 *    data-controller="sidenav" 
 *    data-sidenav-menuid-value="slide-out" 
 *    class="sidenav-trigger show-on-large">
 *    <i class="material-icons">menu</i>
 * </a>
 * <ul id="slide-out" class="sidenav">
 *     ...
 * </ul>
 */

export default class extends Controller {

    static values = { menuid: String }

    connect() {
        M.Sidenav.init(this.getMenuElement(), {})
    }

    getMenuElement() {
        return document.getElementById(this.menuidValue)
    }

    getComponentInstace() {
        return M.Sidenav.getInstance(this.getMenuElement())
    }

    disconnect() {
        var instance = this.getComponentInstace()

        if (instance) {
            instance.destroy()
        }
    }

}
