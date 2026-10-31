// Compatibility entry point: preserves the browser intake regression with the redesigned explorer.
process.env.VERIFY_ZIP='1';
require('./verify_exploration.cjs');
