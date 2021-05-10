import { Controller } from "stimulus";

export default class extends Controller {

    static targets = ["removelink"]
    static values = {
        csrf: String
    }

    delete(event) {
        event.preventDefault();
        if (confirm('¿Rebocar este permiso?')) {
            // TODO: hacer un post al DICED para permisos
            var form = new FormData()
            form.append("csrf_token", this.csrfValue)

            fetch(this.removelinkTarget, {
                method: "POST",
                body: form
            }).then(res => {
                if (res.ok) {
                    res.json().then(data => {
                        this.element.classList.add('hide')
                        M.toast({
                            html: data.message,
                            classes: 'rounded yellow darken-4'
                        })
                    })
                } else {
                    M.toast({
                        html: 'No se pude rebocar el permiso',
                        classes: 'rounded red darken-3'
                    })
                }
            }).catch(error => {
                console.log(error)
                M.toast({
                    html: 'Error en la petición',
                    classes: 'rounded red darken-3'
                })
            })
        }
    }

}
