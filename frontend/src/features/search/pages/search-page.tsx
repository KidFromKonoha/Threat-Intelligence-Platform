import React from 'react';
import { useSearchParams } from 'react-router-dom';
import { SearchBar } from '../components/search-bar';
import { SearchResults } from '../components/search-results';
import { useGlobalSearch } from '../hooks/use-search';
import { useDebounce } from '@/hooks/use-debounce';
import { AlertCircle } from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';

export const SearchPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const searchTerm = searchParams.get('q') || '';

  const handleSearchChange = (val: string) => {
    if (val) {
      setSearchParams({ q: val }, { replace: true });
    } else {
      setSearchParams({}, { replace: true });
    }
  };

  const debouncedSearchTerm = useDebounce(searchTerm, 300);
  const { data, isLoading, isFetching, isError, error } = useGlobalSearch({ q: debouncedSearchTerm });

  return (
    <div className="flex-1 flex flex-col items-center h-full overflow-y-auto">
      {/* Search header — sticky, centered */}
      <div className="w-full max-w-3xl px-6 pt-12 pb-6">
        <h1 className="text-lg font-semibold tracking-tight mb-1">Global Search</h1>
        <p className="text-xs text-muted-foreground mb-4">
          Search across indicators, malware, campaigns, and other threat intelligence entities
        </p>
        <SearchBar
          value={searchTerm}
          onChange={handleSearchChange}
          isFetching={isFetching}
        />
      </div>

      {/* Results */}
      <div className="w-full max-w-3xl px-6 pb-8">
        {isError && (
          <div className="mb-4 p-3 border border-destructive/50 bg-destructive/10 text-destructive rounded-md flex items-center gap-3">
            <AlertCircle className="h-4 w-4 flex-shrink-0" />
            <span className="text-sm">
              {error instanceof Error ? error.message : 'An error occurred while fetching search results.'}
            </span>
          </div>
        )}

        {!debouncedSearchTerm ? (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <p className="text-sm text-muted-foreground">Enter a search term to find indicators, actors, campaigns, and more</p>
          </div>
        ) : isLoading ? (
          <div className="space-y-3">
            <Skeleton className="h-3 w-24" />
            <Skeleton className="h-16 w-full rounded-lg" />
            <Skeleton className="h-16 w-full rounded-lg" />
            <Skeleton className="h-16 w-full rounded-lg" />
          </div>
        ) : data ? (
          <SearchResults data={data} />
        ) : null}
      </div>
    </div>
  );
};
