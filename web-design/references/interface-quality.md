# Interface Quality

Use this reference while implementing or reviewing the behavior of a web interface. Apply only relevant checks, but design every state the chosen flow can actually enter.

## Semantics And Access

- Use landmarks, one descriptive `h1`, ordered headings, and a skip link for substantial pages.
- Prefer native `button`, `a`, `label`, `input`, `select`, `table`, and `dialog` semantics before ARIA.
- Use links for navigation and buttons for actions. Do not make a clickable `div` imitate either.
- Give controls accessible names, decorative media empty alternatives or `aria-hidden`, and meaningful images useful alt text.
- Make every flow keyboard-operable with a visible `:focus-visible` state. Manage focus when dialogs open/close and after failed submission.
- Announce asynchronous updates and inline validation without stealing focus unnecessarily.
- Never rely on color alone. Verify text, control, chart, hover, active, focus, disabled, and error contrast.
- Respect browser zoom and reduced-motion preferences.

## Touch And Interaction

- Make the interactive hit area match the apparent control. Expand small targets; target roughly 44 px on touch interfaces.
- Use at least 16 px input text on mobile unless the platform behavior is otherwise controlled safely.
- Keep interactions forgiving: no dead zones, accidental dismissal, immediate destructive action, or precision-only pointer target.
- Confirm destructive actions or provide a reliable undo window.
- Preserve scroll and focus when navigating back. Put shareable filters, tabs, pagination, and expanded state in the URL when users expect refresh and Back/Forward to work.
- Keep loading labels recognizable, prevent double submission after a request begins, and reconcile optimistic changes on failure.
- Do not block paste. Support password managers, autofill, and one-time-code entry where relevant.

## Forms

- Pair every control with a visible label when possible; make labels clickable.
- Use meaningful `name`, `autocomplete`, `type`, and `inputmode` values. Disable spellcheck only for fields such as codes, emails, or usernames.
- Treat placeholders as examples, not labels.
- Show errors beside the field, explain recovery, preserve the user's input, and focus the first error on submit.
- Warn before abandoning genuinely unsaved work.
- Make empty, invalid, submitting, success, failure, disabled, and permission-denied states intentional.

## Layout And Content Resilience

- Prefer intrinsic grid, flex, wrapping, and container behavior over JavaScript measurement.
- Give flex and grid children `min-width: 0`; fix the cause of overflow instead of hiding the page scrollbar.
- Account for safe-area insets in full-bleed mobile layouts.
- Test narrow mobile, representative laptop, and wide layout when the page can expand. Recompose before shrinking type or tap targets.
- Keep reading measures comfortable and align peers by shared baselines, edges, and value positions.
- Reserve image and skeleton dimensions to avoid layout shift. Skeletons should match the final geometry.
- Handle empty, sparse, dense, loading, error, short, long, and user-generated content.
- Use locale-aware number, currency, date, time, and plural formatting. Protect code tokens and brand names from inappropriate translation.
- Give every screen a next step, recovery path, or clear terminal state.

## Navigation And State

- Use real anchors so open-in-new-tab, copy-link, and browser history work.
- Give the document an accurate title and deep-link headings or states that users may share.
- Avoid hydration that loses input value or focus. Do not suppress hydration warnings as a general fix.
- Keep one canonical state model for calculators and data tools: variables, units, ranges, defaults, precision, formulas, and dependencies.

## Motion

- Default to stillness. Animate only state change, continuity, spatial relationship, or feedback.
- Prefer `transform` and `opacity`; list transitioned properties instead of `transition: all`.
- Make animations interruptible and supply a reduced-motion behavior.
- Do not gate reading behind reveal animation or add motion to compensate for weak hierarchy.

## Media And Data

- Use supplied or authorized media when it adds evidence, understanding, or brand meaning. Avoid decorative stock media and fake product imagery.
- Set explicit image dimensions; eagerly load only critical above-fold media and lazy-load the rest.
- Use consistent scales, units, precision, and baselines for peer values. Align numeric columns and use tabular numerals.
- Prefer direct labels over distant legends. Keep chart labels readable and supply a semantic table or text alternative for material data.

## Performance And Robustness

- Verify on realistic CPU/network conditions when the flow depends on latency.
- Avoid layout reads during render and interleaved DOM reads/writes.
- Keep keystroke work cheap; virtualize or use content visibility for genuinely large lists.
- Preload only critical assets, preconnect only to required origins, and avoid shipping unused font ranges or animation code.
- Test the browsers and device modes that can invalidate the design, especially Safari, touch, dark native controls, and persistent scrollbars.
