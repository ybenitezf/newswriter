// Página para subir las fotos a PhotoStore
import { Application } from "stimulus";
import CoverageUploadController from "./controllers/newcov_controller";

window.jQuery = $; window.$ = $;

// stimulus part
const application = Application.start();
application.register('newcov', CoverageUploadController);
