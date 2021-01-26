import { Controller } from "stimulus";
var moment = require("moment");

// Como usarlo
// <time data-controller="fecha" data-fecha-momento-value="una fecha"></time>

export default class FechaController extends Controller {
    static values = { momento: String, formato: String}

    initialize() {
        const locale = window.navigator.userLanguage || window.navigator.language;

        moment.locale(locale);
    }

    connect () {
        const fecha = this.momentoValue;
        const formato = this.formatoValue || 'lll';
        this.element.innerHTML = moment(fecha).format(formato);
    }
}
