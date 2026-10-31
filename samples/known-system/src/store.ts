import { Pool } from 'pg';
const pool = new Pool();
export function load() { return pool.query('select 1'); }
