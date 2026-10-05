// made by ycangignacy
import init, {Session, effect_catalog} from './assets/js/wte/ttfx.js';
import {paint} from './renderer.js';

const canvas = document.querySelector('canvas');
const art = document.querySelector('pre').textContent.replace(/^\n/, '').trimEnd();
const query = new URLSearchParams(location.search);
let session, frame, metrics, ctx, names, lastEffect;
let ticks = 0, previous = 0, frames = 0;

function resize() {
    const width = innerWidth, height = innerHeight;
    const artCols = Math.max(...art.split('\n').map(line => [...line].length));
    const cellWidth = Math.max(1, Math.min(11, Math.floor(width / artCols), Math.floor(height / (art.split('\n').length * 2))));
    const cellHeight = cellWidth * 2;
    const dpr = devicePixelRatio || 1;
    canvas.width = Math.round(width * dpr);
    canvas.height = Math.round(height * dpr);
    ctx = canvas.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    metrics = {width, height, cellWidth, cellHeight};
    const columns = Math.max(artCols, Math.floor(width / cellWidth));
    const rows = Math.max(art.split('\n').length, Math.floor(height / cellHeight));
    const count = columns * rows;
    frame = {columns, rows, symbols: new Uint32Array(count), fg: new Uint32Array(count), bg: new Uint32Array(count), flags: new Uint8Array(count)};
    nextEffect();
}

function nextEffect() {
    session?.free();
    const pool = names.filter(n => n !== lastEffect);
    const requested = query.get('effect');
    lastEffect = names.includes(requested) ? requested : pool[Math.floor(Math.random() * pool.length)];
    const seed = query.has('seed') ? Number(query.get('seed')) : undefined;
    session = new Session(art, lastEffect, frame.columns, frame.rows, seed, 120);
}

function step(count = 1) {
    for (let i = 0; i < count; i++) {
        if (!session.step()) { nextEffect(); break; }
    }
    session.fill(frame.symbols, frame.fg, frame.bg, frame.flags);
    paint(ctx, metrics, frame);
    frames++;
    return {effect: lastEffect, effects: names.length, frames};
}

function tick(now) {
    if (!document.hidden) {
        ticks = Math.min(4, ticks + Math.max(0, now - previous) * 120 / 1000);
        const count = Math.floor(ticks);
        ticks -= count;
        if (count) step(count);
    }
    previous = now;
    requestAnimationFrame(tick);
}

try {
    await document.fonts.load('18px "JetBrains Mono"');
    const response = await fetch('./assets/js/wte/ttfx.wasm');
    if (!response.ok) throw new Error(`Animation engine: HTTP ${response.status}`);
    await init({module_or_path: await response.arrayBuffer()});
    names = JSON.parse(effect_catalog()).map(effect => effect.name);
    resize();
    window.saver = {step, get status() {return {effect: lastEffect, effects: names.length, frames};}};
    step();
    addEventListener('resize', resize);
    if (!query.has('capture')) requestAnimationFrame(tick);
} catch (error) {
    window.saverError = String(error);
    document.querySelector('pre').style.display = 'grid';
    console.error(error);
}
