UX/UI & Design System Patterns

This reference defines the visual language and usability standards for all generated interfaces. The goal is to create distinctive, modern, and highly intuitive experiences that avoid generic AI aesthetics.

1. Visual Identity (Look & Feel)
Core Aesthetic: Modern Glassmorphism. Use dark backgrounds with transparency layers, background blur (backdrop-filter: blur), and subtle borders to create depth.

Typography: The use of Plus Jakarta Sans is mandatory for a professional, tech-forward feel.

Headings: Semibold/Bold with tracking-tight.

Body: Regular with a line height of 1.6.

Colors (HSL System):

Background: hsl(220 20% 8%) (Deep background).

Surface: hsl(220 18% 12% / 0.6) (Glass layers).

Accent: Dynamic variable (Blue, Violet, or Emerald) with a subtle glow effect.

2. Usability Principles
Visual Hierarchy: The most important information (CTAs, critical status) must have higher visual weight or accent colors.

Affordance: Interactive elements must have hover (subtle lift) and active (slight compression) states to feel clearly clickable.

Feedback: Every user action (saving, deleting) must generate immediate visual feedback, such as a loading spinner or a confirmation toast.

Efficiency: Common actions (e.g., completing a task in UpTask) must be only one click away to minimize cognitive load.

3. Component Patterns (React + Tailwind)
Buttons and Triggers
Primary: Accent color background with high-contrast text for maximum visibility.

Ghost: Text or icon only, gaining a subtle background only on hover.

Loading State: Temporarily replace text with a Spinner component while maintaining the button's original width to prevent layout shifts.

Cards and Containers
Glass Card: Apply bg-surface/60 backdrop-blur-md border border-white/10 rounded-xl for the glass effect.

Empty States: Display minimalist illustrations with a clear Call to Action (CTA), such as "Create your first task," when no data is available.

Forms and Inputs
Labels: Must always be visible and correctly associated with the field via the htmlFor attribute.

Focus State: Clear visual indication with glowing borders in the accent color using ring-2 ring-accent/50.

Validation: Validation errors in soft red (text-red-400) displayed with a smooth fade-in animation.

4. Accessibility (a11y)
Contrast: Strictly maintain a minimum 4.5:1 ratio to ensure legibility for all text.

Navigation: All interactive elements must be fully accessible via keyboard (Tab) and have a visible focus indicator.

ARIA Attributes: Use aria-label mandatorily on buttons that contain only icons for screen reader support.

Motion: Respect the user's "Reduced Motion" preferences configured in the operating system.

5. Animations and Micro-interactions
Entry: Use the custom animate-fade-in animation class for introducing new elements.

Transitions: Standardize state transitions at duration-200 ease-out for fluidity.

Staggered Load: Apply sequential delays (animation-delay) in lists to guide the user's eye and make loading feel organic.