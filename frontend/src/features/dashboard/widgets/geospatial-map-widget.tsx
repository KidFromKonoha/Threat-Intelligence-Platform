import React, { useMemo, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { useDashboardGeospatial } from '../hooks/use-dashboard';
import { Globe, Maximize2, Minimize2 } from 'lucide-react';
import {
  ComposableMap,
  Geographies,
  Geography,
  Sphere,
  Graticule
} from 'react-simple-maps';
import { scaleLinear } from 'd3-scale';

const geoUrl = "https://unpkg.com/world-atlas@2.0.2/countries-110m.json";

export const GeospatialMapWidget: React.FC = () => {
  const { data, isLoading, isError } = useDashboardGeospatial();
  const [isFullscreen, setIsFullscreen] = useState(false);

  const maxCount = useMemo(() => {
    if (!data || data.countries.length === 0) return 1;
    return Math.max(...data.countries.map(c => c.count));
  }, [data]);

  // Premium dark mode gradient from a subtle purple to intense red for threat hotspots
  const colorScale = scaleLinear<string>()
    .domain([0, maxCount])
    .range(["#2A2A35", "#ef4444"]);

  if (isLoading) {
    return <Card className="h-full p-6 bg-background/50 backdrop-blur-xl border-border/50"><Skeleton className="h-64 w-full" /></Card>;
  }

  if (isError) {
    return <Card className="h-full p-6 bg-background/50 backdrop-blur-xl"><span className="text-destructive text-sm">Failed to load map</span></Card>;
  }

  return (
    <Card className={`flex flex-col bg-background/80 backdrop-blur-xl border-border/50 shadow-xl overflow-hidden relative transition-all duration-300 ${isFullscreen ? 'fixed inset-4 z-50 h-auto' : 'h-full'}`}>
      <CardHeader className="pb-2 relative z-10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-2 bg-rose-500/10 rounded-md">
              <Globe className="w-4 h-4 text-rose-500" />
            </div>
            <CardTitle className="text-sm font-semibold tracking-wider uppercase text-foreground/90">Global Threat Origins</CardTitle>
          </div>
          <button 
            onClick={() => setIsFullscreen(!isFullscreen)} 
            className="p-1.5 hover:bg-muted/50 rounded-md text-muted-foreground transition-colors"
            title={isFullscreen ? "Restore size" : "Maximize"}
          >
            {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </button>
        </div>
      </CardHeader>

      <CardContent className={`flex-1 p-0 m-0 overflow-hidden relative z-0 bg-[#0a0a0f] ${isFullscreen ? 'min-h-[600px]' : 'min-h-[300px]'}`}>
        {/* Map Container */}
        <div className="w-full h-full flex items-center justify-center">
          <ComposableMap
            projectionConfig={{
              scale: 140,
              center: [0, 15]
            }}
            width={800}
            height={400}
            style={{ width: "100%", height: "100%" }}
          >
            <Sphere stroke="#1F1F28" strokeWidth={0.5} fill="transparent" id="sphere" />
            <Graticule stroke="#1F1F28" strokeWidth={0.5} />
            
            <Geographies geography={geoUrl}>
              {({ geographies }) =>
                geographies.map((geo) => {
                  // Map the country name from the map data to our API data
                  // Note: Real world mapping might require ISO alpha-3 code matching
                  const countryName = geo.properties.name;
                  const d = data?.countries.find((s) => s.country === countryName);
                  const count = d ? d.count : 0;
                  
                  return (
                    <Geography
                      key={geo.rsmKey}
                      geography={geo}
                      fill={count > 0 ? colorScale(count) : "#1E1E28"}
                      stroke="#0f0f15"
                      strokeWidth={0.5}
                      style={{
                        default: { outline: "none" },
                        hover: { fill: "#818CF8", outline: "none", cursor: "pointer" },
                        pressed: { fill: "#6366F1", outline: "none" },
                      }}
                    />
                  );
                })
              }
            </Geographies>
          </ComposableMap>
        </div>
        
        {/* Top Countries Overlay */}
        <div className="absolute bottom-4 left-4 right-4 bg-background/90 backdrop-blur-md border border-border/50 rounded-lg p-3">
            <h4 className="text-[10px] uppercase text-muted-foreground font-bold mb-2 tracking-wider">Top Origin Sources</h4>
            <div className="flex gap-4 overflow-x-auto pb-1 scrollbar-none">
              {data?.countries.slice(0, 5).map((c, i) => (
                <div key={c.country} className="flex items-center gap-2 min-w-max">
                  <span className="text-xs text-muted-foreground font-mono">{i + 1}.</span>
                  <span className="text-xs font-semibold text-foreground">{c.country}</span>
                  <span className="text-[10px] bg-rose-500/20 text-rose-400 px-1.5 py-0.5 rounded tabular-nums font-bold">
                    {c.count}
                  </span>
                </div>
              ))}
              {(!data?.countries || data.countries.length === 0) && (
                <span className="text-xs text-muted-foreground">No geospatial data available.</span>
              )}
            </div>
        </div>
      </CardContent>
    </Card>
  );
};
