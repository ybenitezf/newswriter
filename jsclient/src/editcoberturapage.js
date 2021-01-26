// Página para subir las fotos a PhotoStore
import { Application } from "stimulus";
import ChipsController from "./controllers/chips_controller";
import EditorExcerptController from "./controllers/excerptEditor";
import ImageUploader from "./controllers/image_uploader";
import EditCoberturaController from "./controllers/editcobertura_controller";
import GaleriaController from "./controllers/galeria_controller";
import FotoController from "./controllers/foto_controller";


// stimulus part
const application = Application.start();
application.register('chips', ChipsController);
application.register('editor', EditorExcerptController);
application.register('imageupload', ImageUploader);
application.register('cobertura', EditCoberturaController);
application.register('galeria', GaleriaController);
application.register('foto', FotoController);
