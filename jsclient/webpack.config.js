const path = require( 'path' );

module.exports = {
    context: __dirname,
    entry: {
      editorcomp: './src/editorpage.js',
      photoupload: './src/photostoreupload.js',
      editcobertura: './src/editcoberturapage.js',
      coberturaspage: './src/coberturaspage.js',
      myphotospage: './src/myphotospage.js',
      photosearch_page: './src/photosearch_page.js',
      photodetails_page: './src/photodetails_page.js',
      photoedit_page: './src/photoedit_page.js'
    },
    output: {
        path: path.resolve( __dirname, '../application/static/js' ),
        filename: '[name].js',
    },
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                use: 'babel-loader',
            },
            {
                test: /\.css$/i,
                use: ['style-loader', 'css-loader'],
            }
        ]
    },
    externals: {
      jquery: 'jQuery'
    }
};
