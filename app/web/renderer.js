// made by ycangignacy
// Canvas rendering for the Unicode terminal cells returned by ttfx.
export function paint(ctx, metrics, frame) {
    const {width, height, cellWidth, cellHeight} = metrics;
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, width, height);
    ctx.font = `${Math.round(cellHeight / 1.2)}px "JetBrains Mono", monospace`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    const ox = Math.floor((width - frame.columns * cellWidth) / 2);
    const oy = Math.floor((height - frame.rows * cellHeight) / 2);
    const color = n => `#${(n & 0xffffff).toString(16).padStart(6, '0')}`;
    for (let i = 0; i < frame.symbols.length; i++) {
        const cp = frame.symbols[i];
        const flags = frame.flags[i];
        const x = ox + (i % frame.columns) * cellWidth;
        const y = oy + Math.floor(i / frame.columns) * cellHeight;
        if (frame.bg[i]) {
            ctx.fillStyle = color(frame.bg[i]);
            ctx.fillRect(x, y, cellWidth, cellHeight);
        }
        if (cp <= 32 || (flags & 32)) continue;
        if ((flags & 16) && Math.floor(performance.now() / 400) % 2) continue;
        ctx.font = `${flags & 2 ? 'italic ' : ''}${flags & 1 ? '700' : '400'} ${Math.round(cellHeight / 1.2)}px "JetBrains Mono", monospace`;
        ctx.fillStyle = color(frame.fg[i] || 0xc8c8c8);
        if (cp === 0x2588) ctx.fillRect(x, y, cellWidth, cellHeight);
        else if (cp === 0x2580) ctx.fillRect(x, y, cellWidth, cellHeight / 2);
        else if (cp >= 0x2581 && cp <= 0x2587) {
            const h = cellHeight * (cp - 0x2580) / 8;
            ctx.fillRect(x, y + cellHeight - h, cellWidth, h);
        } else if (cp === 0x258c) ctx.fillRect(x, y, cellWidth / 2, cellHeight);
        else if (cp === 0x2590) ctx.fillRect(x + cellWidth / 2, y, cellWidth / 2, cellHeight);
        else ctx.fillText(String.fromCodePoint(cp), x + cellWidth / 2, y + cellHeight / 2);
        if (flags & 4) ctx.fillRect(x, y + cellHeight - 1, cellWidth, 1);
        if (flags & 64) ctx.fillRect(x, y + Math.floor(cellHeight / 2), cellWidth, 1);
    }
}
