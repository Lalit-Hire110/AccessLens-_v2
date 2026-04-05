import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // ── Backgrounds ──────────────────────────────────────────────────
        surface: {
          primary:  '#0a0a0a',   // body
          secondary:'#111118',   // page sections
          card:     '#181824',   // cards
          elevated: '#1f1f2e',   // hover / raised cards
        },
        // ── Brand ────────────────────────────────────────────────────────
        brand: {
          DEFAULT: '#3b82f6',    // primary blue
          soft:    '#60a5fa',    // lighter blue for text
          muted:   '#1d4ed8',    // darker blue for pressed states
        },
        // ── Semantic ─────────────────────────────────────────────────────
        success: {
          DEFAULT: '#22c55e',
          soft:    '#16a34a',
          bg:      '#052e16',
          border:  '#166534',
        },
        warning: {
          DEFAULT: '#f59e0b',
          soft:    '#d97706',
          bg:      '#1c1400',
          border:  '#92400e',
        },
        danger: {
          DEFAULT: '#ef4444',
          soft:    '#dc2626',
          bg:      '#1c0505',
          border:  '#991b1b',
        },
        // ── Text ─────────────────────────────────────────────────────────
        content: {
          primary:   '#f1f5f9',  // headings
          secondary: '#94a3b8',  // body text
          muted:     '#475569',  // captions, labels
          disabled:  '#334155',  // disabled states
        },
        // ── Borders ──────────────────────────────────────────────────────
        border: {
          subtle:  '#1e1e2e',    // default card border
          default: '#2d2d3d',    // visible border
          strong:  '#3d3d5c',    // hover border
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic':  'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
      },
    },
  },
  plugins: [],
}
export default config
