import { Controller } from "stimulus"

export default class ChipsController extends Controller {
    // controlador simple para los chips de materializecss
    static values = { 
        placeholder: String,
        secondary: String,
        limit: Number
    }
    static targets = ["view", "input"]

    initialize() {
        var limit = this.hasLimitValue ? this.limitValue : Infinity;
        var placeholder = this.hasPlaceholderValue ? this.placeholderValue : "Tags"
        var secondary = this.hasSecondaryValue ? this.secondaryValue : "+Tag"

        M.Chips.init(
            this.viewTarget, {
                placeholder: placeholder,
                secondaryPlaceholder: secondary,
                limit: limit,
                data: []
            }
        )

        this.chips = M.Chips.getInstance(this.viewTarget);
    }

    connect() {
        const valores_iniciales = JSON.parse(this.inputTarget.value)
        valores_iniciales.forEach(v => {
            this.chips.addChip({
                tag: v,
                image: ''
            });
        })
    }

    getValuesAsList() {
        var tags = [];
        this.chips.getData().forEach((tagData) => {
            tags.push(tagData.tag);
        })

        return tags
    }

    saveToInput() {
        this.inputTarget.value = JSON.stringify(this.getValuesAsList())
    }

    disconnect() {
        this.chips.destroy();
    }

}
