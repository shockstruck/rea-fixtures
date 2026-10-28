import { greet } from './greet.js';
import { add } from './math.js';

globalThis.fixtureResult = { greeting: greet('reader'), total: add(20, 22) };
