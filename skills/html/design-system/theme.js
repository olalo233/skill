/* Optional bridge for Canvas / chart libraries: MBTheme.watch(render). */
(() => {
  const listeners = new Set();
  const scheme = matchMedia('(prefers-color-scheme: dark)');
  const names = ['bg', 'surface', 'subtle', 'hover', 'ink', 'ink-body', 'border', 'rule', 'muted',
    'faint', 'link', 'accent', 'code-bg', 'add-bg', 'add-ink', 'del-bg', 'del-ink',
    'series-1', 'series-2', 'series-3', 'series-4'];
  function colors() {
    const css = getComputedStyle(document.documentElement);
    return Object.fromEntries(names.map(name =>
      [name, css.getPropertyValue('--mb-' + name).trim()]));
  }
  function notify() { const palette = colors(); listeners.forEach(render => render(palette)); }
  scheme.addEventListener('change', notify);
  // Printing uses the light CSS palette even when the display is dark.
  addEventListener('beforeprint', notify);
  addEventListener('afterprint', () => requestAnimationFrame(notify));
  window.MBTheme = Object.freeze({ colors, watch(render) {
    listeners.add(render);
    render(colors());
    return () => listeners.delete(render);
  }});
})();
