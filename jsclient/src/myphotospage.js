import { Application } from "stimulus";
import URLCopyController from "./controllers/urlcopy_controller";

const application = Application.start();
application.register('urlcopy', URLCopyController);
