(function (root, factory) {
  if (typeof exports === 'object' && typeof module === 'object') {
    module.exports = factory(require('@nocobase/client'));
  } else if (typeof define === 'function' && define.amd) {
    define('@commonplace/plugin-proof-ingest', ['@nocobase/client'], factory);
  } else if (typeof exports === 'object') {
    exports['@commonplace/plugin-proof-ingest'] = factory(require('@nocobase/client'));
  } else {
    root['@commonplace/plugin-proof-ingest'] = factory(root['@nocobase/client']);
  }
})(typeof self !== 'undefined' ? self : globalThis, function (client) {
  'use strict';

  class PluginProofIngestClient extends client.Plugin {}

  return {
    __esModule: true,
    PluginProofIngestClient,
    default: PluginProofIngestClient,
  };
});
