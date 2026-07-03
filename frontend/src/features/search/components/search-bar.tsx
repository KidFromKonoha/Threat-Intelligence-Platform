import React, { useEffect, useRef } from 'react';
import { Search, X } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  isFetching?: boolean;
}

export const SearchBar: React.FC<SearchBarProps> = ({ value, onChange, isFetching }) => {
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    // Focus search input on mount
    inputRef.current?.focus();
  }, []);

  return (
    <div className="relative w-full max-w-3xl">
      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <Search className={`h-5 w-5 ${isFetching ? 'text-primary animate-pulse' : 'text-muted-foreground'}`} />
      </div>
      <Input
        ref={inputRef}
        type="text"
        placeholder="Search for indicators, malware, actors..."
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="pl-10 pr-10 h-12 text-lg shadow-sm"
      />
      {value && (
        <Button
          variant="ghost"
          size="icon"
          className="absolute inset-y-0 right-0 h-12 w-10 text-muted-foreground hover:text-foreground"
          onClick={() => {
            onChange('');
            inputRef.current?.focus();
          }}
        >
          <X className="h-4 w-4" />
        </Button>
      )}
    </div>
  );
};
