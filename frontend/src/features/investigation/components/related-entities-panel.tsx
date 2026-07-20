import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface Props {
  threatActors?: any[];
  campaigns?: any[];
  malware?: any[];
  mitreTechniques?: any[];
  indicators?: any[];
}

export const RelatedEntitiesPanel: React.FC<Props> = ({ 
  threatActors = [], 
  campaigns = [], 
  malware = [], 
  mitreTechniques = [],
  indicators = []
}) => {
  const sections = [
    { title: 'Threat Actors', data: threatActors, key: 'name', color: 'bg-red-500/10 text-red-500 border-red-500/20' },
    { title: 'Campaigns', data: campaigns, key: 'name', color: 'bg-purple-500/10 text-purple-500 border-purple-500/20' },
    { title: 'Malware', data: malware, key: 'name', color: 'bg-orange-500/10 text-orange-500 border-orange-500/20' },
    { title: 'MITRE Techniques', data: mitreTechniques, key: 'name', color: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20' },
    { title: 'Indicators', data: indicators, key: 'value', color: 'bg-blue-500/10 text-blue-500 border-blue-500/20' },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {sections.map(section => {
        if (section.data.length === 0) return null;
        return (
          <Card key={section.title} className="bg-muted/30">
            <CardHeader className="py-3 px-4">
              <CardTitle className="text-sm">{section.title}</CardTitle>
            </CardHeader>
            <CardContent className="px-4 pb-4">
              <div className="flex flex-wrap gap-2">
                {section.data.map((item, idx) => (
                  <Badge key={item.id || idx} variant="outline" className={section.color}>
                    {item[section.key]}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
};
