const fs = require('fs');
const glob = require('glob');
const path = require('path');

const files = glob.sync('frontend/src/features/dashboard/components/*.tsx');

files.forEach(file => {
  let content = fs.readFileSync(file, 'utf-8');
  
  // Add import for Skeleton if not present
  if (!content.includes('Skeleton')) {
    content = content.replace(/import \{ Card, CardContent, CardHeader, CardTitle \} from '@\/components\/ui\/card';/, "import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';\nimport { Skeleton } from '@/components/ui/skeleton';");
  }

  // Replace <span className="text-muted-foreground text-sm">Loading ...</span>
  const loadingRegex = /<Card className="h-full flex items-center justify-center min-h-\[([^\]]+)\]"><span className="text-muted-foreground text-sm">Loading ([^<]+)<\/span><\/Card>/;
  const match = content.match(loadingRegex);
  
  if (match) {
    const minHeight = match[1];
    const replacement = `<Card className="h-full min-h-[${minHeight}] p-6">\n      <div className="space-y-4">\n        <Skeleton className="h-4 w-1/3" />\n        <Skeleton className="h-8 w-full" />\n        <Skeleton className="h-8 w-full" />\n      </div>\n    </Card>`;
    content = content.replace(loadingRegex, replacement);
  }
  
  fs.writeFileSync(file, content);
  console.log('Updated', file);
});
