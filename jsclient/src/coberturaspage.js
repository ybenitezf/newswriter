import { Application } from "stimulus";
import URLCopyController from "./controllers/urlcopy_controller";
import FechaController from "./controllers/fecha_controller";

const application = Application.start();
application.register('urlcopy', URLCopyController);
application.register('fecha', FechaController);
