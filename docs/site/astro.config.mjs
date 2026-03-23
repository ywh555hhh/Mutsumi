import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import starlightLinksValidator from 'starlight-links-validator';
import starlightViewModes from 'starlight-view-modes';
import starlightImageZoom from 'starlight-image-zoom';

const isProd = process.env.NODE_ENV === 'production' || process.argv.includes('build');

export default defineConfig({
  site: 'https://ywh555hhh.github.io',
  base: isProd ? '/Mutsumi' : '/',
  integrations: [
    starlight({
      title: 'Mutsumi',
      tagline: 'Never lose a thread.',
      logo: {
        light: './src/assets/logo-light.svg',
        dark: './src/assets/logo-dark.svg',
        replacesTitle: true,
      },
      head: [
        {
          tag: 'script',
          attrs: { type: 'module' },
          content: `
import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
function initMermaid() {
  const theme = document.documentElement.dataset.theme === 'light' ? 'default' : 'dark';
  document.querySelectorAll('.expressive-code .ec-line').forEach(line => {
    const codeBlock = line.closest('[data-language="mermaid"]');
    if (codeBlock && !codeBlock.dataset.mermaidProcessed) {
      codeBlock.dataset.mermaidProcessed = 'true';
      const code = Array.from(codeBlock.querySelectorAll('.ec-line'))
        .map(l => l.textContent).join('\\n');
      const div = document.createElement('div');
      div.className = 'mermaid';
      div.textContent = code;
      const figure = codeBlock.closest('figure') || codeBlock.closest('.expressive-code');
      if (figure) figure.replaceWith(div);
    }
  });
  mermaid.initialize({ startOnLoad: false, theme });
  mermaid.run();
}
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initMermaid);
} else {
  initMermaid();
}
document.addEventListener('astro:after-swap', initMermaid);
`,
        },
        {
          tag: 'script',
          attrs: { type: 'module' },
          content: `
import TurndownService from 'https://cdn.jsdelivr.net/npm/turndown@7/lib/turndown.browser.es.min.js';
const td = new TurndownService({ headingStyle: 'atx', codeBlockStyle: 'fenced' });
td.addRule('skip-bar', { filter: n => n.classList?.contains('mu-page-bar'), replacement: () => '' });

const copyLabels = { en: ['Copy Markdown', 'Copied!'], 'zh-CN': ['复制 Markdown', '已复制'], ja: ['Markdown をコピー', 'コピー済み'] };
const copyIcon = '<svg width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>';
const checkIcon = '<svg width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>';

function initPageBar() {
  if (document.querySelector('.mu-page-bar')) return;
  const title = document.querySelector('h1[id="_top"]');
  if (!title) return;

  const bar = document.createElement('div');
  bar.className = 'mu-page-bar sl-flex print:hidden';

  /* Move edit link */
  const footerMeta = document.querySelector('footer .meta');
  if (footerMeta) {
    const editLink = footerMeta.querySelector('a');
    const lastUpdated = footerMeta.querySelector('p');
    if (editLink) bar.appendChild(editLink.cloneNode(true));
    if (lastUpdated) { const span = document.createElement('span'); span.className = 'mu-last-updated'; span.textContent = lastUpdated.textContent; bar.appendChild(span); }
    footerMeta.remove();
  }

  /* Copy Markdown button */
  const lang = document.documentElement.lang || 'en';
  const [label, copied] = copyLabels[lang] || copyLabels.en;
  const btn = document.createElement('button');
  btn.className = 'mu-copy-md sl-flex';
  btn.type = 'button';
  const iconSpan = document.createElement('span');
  iconSpan.insertAdjacentHTML('afterbegin', copyIcon);
  btn.appendChild(iconSpan);
  btn.appendChild(document.createTextNode(label));
  btn.addEventListener('click', () => {
    const content = document.querySelector('.sl-markdown-content');
    if (!content) return;
    const md = td.turndown(content.cloneNode(true));
    navigator.clipboard.writeText(md).then(() => {
      iconSpan.replaceChildren();
      iconSpan.insertAdjacentHTML('afterbegin', checkIcon);
      btn.lastChild.textContent = copied;
      setTimeout(() => { iconSpan.replaceChildren(); iconSpan.insertAdjacentHTML('afterbegin', copyIcon); btn.lastChild.textContent = label; }, 1500);
    });
  });
  bar.appendChild(btn);

  title.insertAdjacentElement('afterend', bar);
}

if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initPageBar);
else initPageBar();
document.addEventListener('astro:after-swap', initPageBar);
`,
        },
      ],
      social: [
        { icon: 'github', label: 'GitHub', href: 'https://github.com/ywh555hhh/Mutsumi' },
      ],
      editLink: {
        baseUrl: 'https://github.com/ywh555hhh/Mutsumi/edit/main/docs/site/',
      },
      lastUpdated: true,
      customCss: ['./src/styles/custom.css'],
      defaultLocale: 'root',
      locales: {
        root: { label: 'English', lang: 'en' },
        'zh-cn': { label: '简体中文', lang: 'zh-CN' },
        ja: { label: '日本語', lang: 'ja' },
      },
      sidebar: [
        {
          label: 'Introduction',
          translations: { 'zh-CN': '介绍', ja: 'はじめに' },
          items: [
            { slug: 'introduction/what-is-mutsumi' },
            { slug: 'introduction/architecture' },
            { slug: 'introduction/comparison' },
          ],
        },
        {
          label: 'Getting Started',
          translations: { 'zh-CN': '快速开始', ja: 'クイックスタート' },
          items: [
            { slug: 'getting-started/installation' },
            { slug: 'getting-started/quick-start' },
            { slug: 'getting-started/agent-setup' },
            { slug: 'getting-started/startup-flow' },
            { slug: 'getting-started/terminal-integration' },
            { slug: 'getting-started/workflow-sop' },
          ],
        },
        {
          label: 'Features',
          translations: { 'zh-CN': '功能', ja: '機能' },
          items: [
            { slug: 'features/tui-overview' },
            { slug: 'features/task-management' },
            { slug: 'features/keybindings' },
            { slug: 'features/themes' },
            { slug: 'features/configuration' },
            { slug: 'features/i18n' },
            { slug: 'features/cli' },
            { slug: 'features/multi-source' },
            { slug: 'features/event-log' },
          ],
        },
        {
          label: 'Customization',
          translations: { 'zh-CN': '自定义', ja: 'カスタマイズ' },
          items: [
            { slug: 'customization/custom-themes' },
            { slug: 'customization/custom-keybindings' },
            { slug: 'customization/custom-css' },
            { slug: 'customization/agent-protocol' },
            { slug: 'customization/data-contract' },
            { slug: 'customization/plugin-vision' },
          ],
        },
        {
          label: 'Reference',
          translations: { 'zh-CN': '参考', ja: 'リファレンス' },
          items: [
            { slug: 'reference/task-schema' },
            { slug: 'reference/cli-commands' },
            { slug: 'reference/config-reference' },
            { slug: 'reference/keybinding-reference' },
            { slug: 'reference/faq' },
          ],
        },
      ],
      plugins: [
        starlightLinksValidator({
          errorOnRelativeLinks: false,
          errorOnFallbackPages: false,
        }),
        starlightViewModes({
          zenModeSettings: {
            displayOptions: {
              showHeader: true,
            },
            keyboardShortcut: ['Ctrl+Shift+Z'],
          },
        }),
        starlightImageZoom(),
      ],
    }),
  ],
});
