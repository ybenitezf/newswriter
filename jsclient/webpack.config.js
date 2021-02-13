var HtmlWebpackPlugin = require('html-webpack-plugin');
var path = require( 'path' );

module.exports = {
    context: __dirname,
    entry: {
      app: './src/app.js',
    },
    output: {
        path: path.resolve( __dirname, '../newswriter/static/js' ),
        filename: '[name].js',
    },
    plugins: [new HtmlWebpackPlugin({
        inject: false,
        template: 'src/jsimports.ejs',
        publicPath: '',
        filename: path.resolve( __dirname, '../newswriter/templates/jsfiles.html'),
    })],
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
            },
            {
              test: /\.svg$/,
              loader: 'svg-inline-loader?removeSVGTagAttrs=false'
            }
        ]
    },
    externals: {
      jquery: 'jQuery'
    },
    optimization: {
        runtimeChunk: 'single',
        splitChunks: {
          chunks: 'all',
          maxInitialRequests: Infinity,
          minSize: 0,
          cacheGroups: {
            vendor: {
              test: /[\\/]node_modules[\\/]/,
              name(module) {
                // get the name. E.g. node_modules/packageName/not/this/part.js
                // or node_modules/packageName
                const packageName = module.context.match(/[\\/]node_modules[\\/](.*?)([\\/]|$)/)[1];
    
                // npm package names are URL-safe, but some servers don't like @ symbols
                return `vendor.${packageName.replace('@', '')}`;
              },
            },
          },
        }
    },
};
