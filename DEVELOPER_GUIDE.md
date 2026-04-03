# Developer Guide - UI Improvements

## Quick Reference

### Access Gap Thresholds
```typescript
// Low: 0 - 0.2 (Green)
// Moderate: 0.2 - 0.4 (Yellow)
// High: > 0.4 (Red)

function getAccessGapInfo(accessGap: number) {
  if (accessGap <= 0.2) return { level: "Low Access Gap", color: "green" };
  if (accessGap <= 0.4) return { level: "Moderate Access Gap", color: "yellow" };
  return { level: "High Access Gap", color: "red" };
}
```

### Score Label Thresholds
```typescript
// High: >= 0.7
// Medium: 0.4 - 0.7
// Low: < 0.4

function getScoreLabel(score: number): string {
  if (score >= 0.7) return "HIGH";
  if (score >= 0.4) return "MEDIUM";
  return "LOW";
}
```

## Component Structure

### ResultsDisplay.tsx
```
ResultsDisplay (main component)
├── Persona Card
└── Recommendations
    └── SchemeCard (for each recommendation)
        ├── Header (name + badge)
        ├── AccessGapCard (prominent, colored)
        ├── ScoresGrid (eligibility + risk with labels)
        ├── InsightCard (if available)
        └── ExplanationSection (collapsible)
            ├── Summary (always visible)
            ├── Toggle Button
            └── Details (when expanded)
                ├── Why You Qualify
                ├── Potential Barriers
                ├── Access Gap Explanation
                └── Recommended Next Steps
```

## Customization Points

### 1. Adjusting Access Gap Thresholds
Location: `getAccessGapInfo()` function

```typescript
// Current thresholds
if (accessGap <= 0.2) // Low
if (accessGap <= 0.4) // Moderate
else                  // High

// To adjust, modify the comparison values
```

### 2. Changing Score Label Thresholds
Location: `getScoreLabel()` function

```typescript
// Current thresholds
if (score >= 0.7) // HIGH
if (score >= 0.4) // MEDIUM
else              // LOW
```

### 3. Modifying Colors
All colors use Tailwind CSS classes:

```typescript
// Green (Low Access Gap)
color: "text-green-400"
bgColor: "bg-green-500/10"
borderColor: "border-green-500/30"

// Yellow (Moderate)
color: "text-yellow-400"
bgColor: "bg-yellow-500/10"
borderColor: "border-yellow-500/30"

// Red (High)
color: "text-red-400"
bgColor: "bg-red-500/10"
borderColor: "border-red-500/30"
```

### 4. Adjusting Decimal Precision
Current: 3 decimal places (`.toFixed(3)`)

```typescript
// To change precision
{rec.access_gap.toFixed(3)} // Current
{rec.access_gap.toFixed(2)} // 2 decimals
{rec.access_gap.toFixed(4)} // 4 decimals
```

### 5. Loading Animation Timing
Location: `ExplanationLoader` component

```typescript
// Current settings
animationDelay: `${idx * 200}ms`  // Stagger delay
animationDuration: "1.5s"         // Pulse duration

// To adjust
animationDelay: `${idx * 300}ms`  // Slower stagger
animationDuration: "2s"           // Slower pulse
```

## State Management

### Collapse State
Each card manages its own collapse state independently:

```typescript
const [isExpanded, setIsExpanded] = useState(false);
```

This means:
- Each card can be expanded/collapsed independently
- State is not persisted (resets on re-render)
- No global state management needed

### To Add Global Collapse Control
```typescript
// In parent component (ResultsDisplay)
const [expandedCards, setExpandedCards] = useState<Set<number>>(new Set());

// Pass to ExplanationSection
<ExplanationSection 
  exp={exp} 
  isExpanded={expandedCards.has(idx)}
  onToggle={() => {
    const newSet = new Set(expandedCards);
    if (newSet.has(idx)) newSet.delete(idx);
    else newSet.add(idx);
    setExpandedCards(newSet);
  }}
/>
```

## Styling Guidelines

### Spacing Scale
- `gap-2` / `space-y-2` = 0.5rem (8px)
- `gap-3` / `space-y-3` = 0.75rem (12px)
- `gap-4` / `space-y-4` = 1rem (16px)
- `gap-6` / `space-y-6` = 1.5rem (24px)

### Padding Scale
- `p-3` = 0.75rem (12px)
- `p-4` = 1rem (16px)
- `p-5` = 1.25rem (20px)
- `p-6` = 1.5rem (24px)

### Text Sizes
- `text-xs` = 0.75rem (12px)
- `text-sm` = 0.875rem (14px)
- `text-base` = 1rem (16px)
- `text-lg` = 1.125rem (18px)

## Accessibility Considerations

### Color Contrast
All color combinations meet WCAG AA standards:
- Green text on dark background: ✓
- Yellow text on dark background: ✓
- Red text on dark background: ✓

### Interactive Elements
- Toggle button has hover state
- Cards have hover effects
- All interactive elements are keyboard accessible

### Screen Readers
- Semantic HTML structure maintained
- Icons are decorative (not read by screen readers)
- Labels are descriptive

## Performance Notes

### Re-render Optimization
- Collapse state is local to each card
- No unnecessary parent re-renders
- Helper functions are pure (no side effects)

### Bundle Size Impact
- No new dependencies added
- Only added ~100 lines of code
- Minimal impact on bundle size

## Testing Checklist

- [ ] Test with access_gap = 0.1 (should show green)
- [ ] Test with access_gap = 0.3 (should show yellow)
- [ ] Test with access_gap = 0.6 (should show red)
- [ ] Test collapse/expand for each card
- [ ] Test with empty barriers array
- [ ] Test with no next_steps
- [ ] Test loading state
- [ ] Test error state
- [ ] Test hover effects
- [ ] Test on mobile viewport
- [ ] Test keyboard navigation

## Common Issues & Solutions

### Issue: Colors not showing
**Solution:** Ensure Tailwind CSS is properly configured and includes the color classes used.

### Issue: Animation not working
**Solution:** Check that the `animate-pulse` utility is available in your Tailwind config.

### Issue: Collapse not working
**Solution:** Verify React useState is imported and the component is a client component (`"use client"`).

### Issue: TypeScript errors
**Solution:** Run `npm run build` to see detailed error messages. All types should be properly inferred.

## Future Enhancement Ideas

1. **Persist collapse state** in localStorage
2. **Add "Expand All" / "Collapse All"** buttons
3. **Animate the collapse transition** with CSS transitions
4. **Add tooltips** for score labels
5. **Export recommendations** as PDF
6. **Add filtering** by access gap level
7. **Add sorting** by different metrics
8. **Add comparison mode** to compare multiple schemes side-by-side

## Maintenance Notes

### When Backend Changes
If the backend adds new fields to the response:
1. Update TypeScript types in `lib/api.ts`
2. Update display logic in `ResultsDisplay.tsx`
3. Update documentation

### When Design Changes
All styling is in Tailwind classes - no separate CSS files to maintain.

### Version Compatibility
- React 18+
- Next.js 13+ (App Router)
- TypeScript 5+
- Tailwind CSS 3+
