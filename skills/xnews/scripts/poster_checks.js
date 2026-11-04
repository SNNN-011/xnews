// Kirim ekspresi ini ke js() di browser_exec SETELAH viewport diset 1080x1350
// dan halaman di-reload. Cetak JSON-nya; semua harus true / 0.
(() => {
  const R = e => {
    const r = e.getBoundingClientRect();
    return [+r.x.toFixed(1), +r.y.toFixed(1), +r.width.toFixed(1), +r.height.toFixed(1), +r.bottom.toFixed(1)];
  };
  const q = s => document.querySelector(s);
  const poster = q('#poster');
  const lines = [...document.querySelectorAll('.headline .ln')];
  const lum = c => {
    const [r, g, b] = c.match(/\d+/g).slice(0, 3).map(Number).map(v => {
      v /= 255;
      return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  };
  const onBlack = c => +(((lum(c) + 0.05) / 0.05)).toFixed(2);
  const accentColor = getComputedStyle(q('.headline .accent')).color;

  return {
    viewport: [innerWidth, innerHeight, devicePixelRatio],
    fit: getComputedStyle(document.documentElement).getPropertyValue('--fit').trim(),
    poster: R(poster),
    poster_at_origin: R(poster)[0] === 0 && R(poster)[1] === 0,
    canvas_ok: R(poster)[2] === 1080 && R(poster)[3] === 1350,
    overflow: [poster.scrollWidth - poster.clientWidth, document.documentElement.scrollWidth - innerWidth],
    headline_lines: lines.length,
    line_wraps: lines.map(l => {
      const r = document.createRange();
      r.selectNodeContents(l);
      return r.getClientRects().length;      // harus 1 semua
    }),
    headline_overflow: q('#headline').scrollWidth - q('#headline').clientWidth,
    weights: [...lines, q('.handle')].map(e => getComputedStyle(e).fontWeight),
    images_ok: [...document.images].every(i => i.complete && i.naturalWidth > 0),
    fonts_loaded: [document.fonts.check('800 86px Mont'), document.fonts.check('400 21px Mont')],
    contrast: {white: onBlack('rgb(255,255,255)'), accent: onBlack(accentColor)},
    accent: accentColor,
  };
})()
