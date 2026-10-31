'use strict';
// Defense in depth for this trusted worker, NOT an OS sandbox for hostile code.
const Module = require('node:module');
const denied = new Set(['http','https','http2','net','tls','dns','dgram','child_process','cluster','worker_threads','wasi']);
const original = Module._load;
Module._load = function(name, ...args) {
  if (denied.has(name.replace(/^node:/, '').split('/')[0])) throw Error('Worker network/process API prohibited');
  return original.call(this, name, ...args);
};
globalThis.fetch = () => { throw Error('Worker network API prohibited'); };
