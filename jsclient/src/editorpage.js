import $ from 'jquery';
import { Application } from "stimulus";
import EditorController from "./controllers/editor_controller";
// import { definitionsFromContext } from "stimulus/webpack-helpers";

window.jQuery = $; window.$ = $;

// stimulus part
const application = Application.start();
application.register('editor', EditorController);
// const sticontext = require.context("./controllers", true, /\.js$/)
// stiapp.load(definitionsFromContext(sticontext))
