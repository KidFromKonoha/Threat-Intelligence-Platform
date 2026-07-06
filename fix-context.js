const fs = require('fs');
let b = fs.readFileSync('IMPLEMENTATION_CONTEXT.md');

// Try parsing as utf-16le first
let text = b.toString('utf-16le');
if (!text.includes('Frontend Phase')) {
  // If it doesn't look right, fall back to utf-8
  text = b.toString('utf-8');
}

// Remove any existing F6 blocks that were appended improperly
text = text.replace(/## Frontend Phase F6.*/gs, '');

text += `
## Frontend Phase F6

### Investigations Architecture Implemented
- **Feature isolation**: Kept investigations logic in \`features/investigations\` mapping to \`/api/v1/investigations\`.
- **TanStack Query**: Implemented data fetching, caching, and invalidation for lists, summaries, and timelines.
- **UI Components**: Built an Investigation-focused layout using \`InvestigationHeader\`, \`InvestigationTimeline\`, and \`InvestigationEntities\` to display comprehensive summary data.
- **Modals**: Added \`InvestigationCreateModal\` utilizing \`react-hook-form\` and \`zod\` for payload validation before sending mutations.

### Architectural Decisions
- Used feature-sliced design to isolate investigation views from the rest of the dashboard.
- Display cards on the investigations list were crafted to emphasize status and priority, adhering strictly to analyst-oriented density.
- De-coupled the entity summaries and activity timelines into independent queries (\`useInvestigationSummary\`, \`useInvestigationTimeline\`) to enable smoother progressive rendering of complex detail pages.
`;

// Remove null bytes if any snuck in due to PowerShell UTF-16
text = text.replace(/\0/g, '');

fs.writeFileSync('IMPLEMENTATION_CONTEXT.md', text, 'utf-8');
