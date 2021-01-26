/* Cargador de imagenes para photostore
*  
*  Este es para usar con un formulario que debe incluir los datos generales
*  de la foto + el archivo que se va a subir, por ejemplo:

    <form  data-controller="imageupload" action="<uploadendpoit>" method="POST" data-imageupload-apiendpoint-value="endpoint-de-covertura-para-la-foto">
        <input type="hidden" name="healine" value='...'>
        <input type="hidden" name="creditline" value='...'>
        <input type="hidden" name="keywords" value='...'>
        <input type="hidden" name="excerpt" value='...'>
        <input type="hidden" name="taken_by" value='...'>
        <div class="file-field input-field">
            <div class="btn waves-effect waves-light" data-imageupload-target="btn">
                <span>Agregar Foto</span>
                <input type="file" name="image" accept="image/*" data-imageupload-target="file" />
            </div>
            <div class="file-path-wrapper">
                <input class="file-path validate" type="text">
            </div>
        </div>
    </form>
*  
*  Si se da el valor de photo_coverage, debe ser el id de una cobertura, en 
*  cuyo caso el resto de los parametros es ignorados y se toman los valores
*  de la cobertura.
*  
*  healine: titular
*  creditline: credito de la foto
*  keywords: lista de palabras claves
*  excerpt: resumen en formato de editorjs
*  taken_by: autor de la foto
*/
import { Controller } from "stimulus";


export default class ImageUploader extends Controller {
    static targets = [ "file", "btn" ]
    static values = { apiendpoint: String }

    connect() {
        this.fileTarget.addEventListener('change', (e) => {
            this.sendData()
        });
    }

    sendData(e) {
        // enviar la foto aqui
        const formData = new FormData(this.element)
        const boton = this.btnTarget
        boton.classList.add('disabled')
        const apiendpoint = this.apiendpointValue
        fetch(
            this.element.getAttribute('action'),
            {
                method: 'POST',
                body: formData
            }
        ).then( function(r) {
            if (r.ok) {
                r.json().then( function(data) {
                    // esperar antes de redireccionar para que se vea el 
                    // mensaje
                    M.toast({html: 'Foto guardada', classes: 'rounded'})
                    // llamar al api the photostore para asociar la foto
                    // a la galeria
                    fetch(apiendpoint,{
                        method: 'POST',
                        body: JSON.stringify({photos: [data.md5]}),
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    }).then(res => res.json())
                    .catch(error => console.log(error))
                    .then(function () {
                            window.location.replace(window.location.href);
                    })
                })
            } else {
                M.toast({
                    html: '<b>ERROR</b>: No se pudo guardar, error en el servidor',
                    classes: 'rounded red darken-4'
                })
                boton.classList.remove('disabled')
                console.log("Error en la peticion")
            }
        }).catch( function(error) {
            M.toast({
                html: '<b>ERROR</b>: No se pudo guardar, error en el servidor',
                classes: 'rounded red darken-4'
            })
            boton.classList.remove('disabled')
            console.log(error)
        });
    }

}
