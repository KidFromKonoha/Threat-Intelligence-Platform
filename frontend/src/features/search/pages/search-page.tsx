import React, { useState } from 'react';
import { SearchBar } from '../components/search-bar';
import { SearchResults } from '../components/search-results';
import { useGlobalSearch } from '../hooks/use-search';
import { useDebounce } from '@/hooks/use-debounce';
import { AlertCircle } from 'lucide-react';

export const SearchPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  
  // Debounce the search term to avoid excessive API requests while typing
  const debouncedSearchTerm = useDebounce(searchTerm, 300);

  const { data, isLoading, isFetching, isError, error } = useGlobalSearch({ q: debouncedSearchTerm });

  return (
    <div className="flex-1 flex flex-col items-center bg-background text-foreground h-full overflow-y-auto">
      
      {/* Fixed Header Section */}
      <div className="w-full max-w-4xl px-6 pt-10 pb-6 flex flex-col gap-2">
        <h1 className="text-3xl font-semibold tracking-tight">Global Search</h1>
        <p className="text-sm text-muted-foreground mb-4">
          Search across indicators, malware, campaigns, and other threat intelligence entities.
        </p>
        <SearchBar 
          value={searchTerm} 
          onChange={setSearchTerm} 
          isFetching={isFetching}
        />
      </div>

      {/* Results Section */}
      <div className="w-full max-w-4xl px-6 flex-1">
        {isError && (
          <div className="mb-6 p-4 border border-destructive/50 bg-destructive/10 text-destructive rounded-lg flex items-start gap-3">
            <AlertCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
            <div className="flex flex-col">
              <span className="font-semibold text-sm">Error</span>
              <span className="text-sm mt-1 opacity-90">
                {error instanceof Error ? error.message : 'An error occurred while fetching search results.'}
              </span>
            </div>
          </div>
        )}

        {!debouncedSearchTerm ? (
          <div className="flex flex-col items-center justify-center py-20 text-center opacity-50">
            <span className="text-lg font-medium">Enter a search term</span>
            <span className="text-sm">Type an IP address, domain, hash, or actor name</span>
          </div>
        ) : isLoading ? (
          <div className="space-y-4 w-full">
            <div className="h-4 w-32 bg-muted animate-pulse rounded"></div>
            <div className="h-24 w-full bg-muted animate-pulse rounded-lg"></div>
            <div className="h-24 w-full bg-muted animate-pulse rounded-lg"></div>
            <div className="h-24 w-full bg-muted animate-pulse rounded-lg"></div>
          </div>
        ) : data ? (
          <SearchResults data={data} />
        ) : null}
      </div>
    </div>
  );
};
