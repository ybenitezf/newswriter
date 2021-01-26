import { Controller } from "stimulus"

export default class FotoController extends Controller {

    static targets = [ "btnRemove" ]

    static values = { 
        id: String,
        apiremove: String
    }

    connect() {
        this.btnRemoveTarget.classList.remove("disabled")
        // console.log("FotoController#connected")
        // console.log(this.apiremoveValue)
        // console.log(this.idValue)
    }

    removeFromCoverage(e) {
        var btn = this.btnRemoveTarget
        const el = this.element
        btn.classList.add("disabled")
        const apiendpoint = this.apiremoveValue
        const todettach = this.idValue
        fetch(apiendpoint, {
            method: 'DELETE',
            body: JSON.stringify({
                photos: [todettach]
            }),
            headers: {'Content-Type': 'application/json'}
        }).then( function (r) {
            if (r.ok) {
                // ok se quito
                M.toast({
                    html: "Foto quitada de la cobertura",
                    classes: 'rounded'
                })
                // enviar evento cuando la foto sea quitada de la galeria
                const event = document.createEvent("CustomEvent")
                event.initCustomEvent("photo-removed", true, true, null)
                el.dispatchEvent(event)
            } else {
                // ummm el server dio error
                M.toast({
                    html: 'El servidor respondio con error',
                    classes: 'rounded red darken-4'
                })
                console.log(r)
                btn.classList.remove('disabled')
            }
        }).catch( function(error) {
            M.toast({
                html: 'No se pudo enviar la petición',
                classes: 'rounded red darken-4'
            })
            console.log(error)
        });

        this.btnRemoveTarget.classList.remove("disabled")
    }

}
