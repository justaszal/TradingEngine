const path = require('path');
const UglifyJsPlugin = require('uglifyjs-webpack-plugin');
const ExtractTextPlugin = require('extract-text-webpack-plugin');
const webpack = require('webpack');
// const NgAnnotatePlugin = require('ng-annotate-webpack-plugin');
const BabelObjectSpread = require('babel-plugin-transform-object-rest-spread');

module.exports = {
  entry: {
    index: path.join(__dirname, 'public/root.module.js'),
  },
  output: {
    filename: '[name]-bundle.js',
    // path: path.resolve(__dirname, 'dist'),
    // path: path.join(__dirname, '/dist/'),
    devtoolLineToLine: true,
    pathinfo: true,
    sourceMapFilename: '[name].js.map',
    // publicPath: path.resolve(__dirname, 'public'),
    publicPath: path.join(__dirname, '/dist/'),
  },
  mode: 'development',
  module: {
    rules: [
      {
        test: /\.js$/,
        loader: 'babel-loader',
        exclude: ['node_modules/', 'public/vendor/materialize-src'],
        query: {
          presets: [['env', { modules: false, targets: { node: 6 } }]],
          plugins: [BabelObjectSpread],
        },
      },
      {
        test: /\.scss$/,
        use: ExtractTextPlugin.extract({
          fallback: 'style-loader',
          use: ['css-loader', 'sass-loader'],
        }),
      },
      {
        test: /\.html$/,
        loader: 'raw-loader',
        exclude: '/public/vendor/',
      },
      {
        test: /\.(png|jpe?g|gif|ico)$/,
        loader: 'file-loader?name=assets/[name].[hash].[ext]',
      },
      {
        test: /\.woff(\?v=\d+\.\d+\.\d+)?$/,
        loader: 'url-loader?limit=10000&mimetype=application/font-woff',
      },
      {
        test: /\.woff2(\?v=\d+\.\d+\.\d+)?$/,
        loader: 'url-loader?limit=10000&mimetype=application/font-woff',
      },
      {
        test: /\.ttf(\?v=\d+\.\d+\.\d+)?$/,
        loader: 'url-loader?limit=10000&mimetype=application/octet-stream',
      },
      {
        test: /\.eot(\?v=\d+\.\d+\.\d+)?$/,
        loader: 'file-loader',
      },
      {
        test: /\.svg(\?v=\d+\.\d+\.\d+)?$/,
        loader: 'url-loader?limit=10000&mimetype=image/svg+xml',
      },
    ],
  },
  plugins: [
    new webpack.HotModuleReplacementPlugin(),
    // new NgAnnotatePlugin({
    //   add: true,
    // }),
    new UglifyJsPlugin(),
    new ExtractTextPlugin({
      filename: 'style.css',
    }),
  ],
  devServer: {
    publicPath: '/',
    contentBase: path.resolve(__dirname, 'dist'),
    compress: true,
    watchContentBase: true,
    // headers: {
    //   'Access-Control-Allow-Origin': '*',
    //   'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, PATCH, OPTIONS',
    //   'Access-Control-Allow-Headers': 'X-Requested-With, content-type, Authorization',
    // },
  },
  devtool: 'eval-source-map',
};
