import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Download, FileText, Calendar } from 'lucide-react';
import type { ReportResponse } from '../types/report';
import type { ReportType } from '../api/report-api';
import { useExportReport } from '../hooks/use-report';

interface Props {
  report: ReportResponse;
  reportType: ReportType;
}

export const ReportHeader: React.FC<Props> = ({ report, reportType }) => {
  const { mutate: exportReport, isPending } = useExportReport();

  return (
    <Card className="mb-6">
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-primary/10 rounded-md">
                <FileText className="w-6 h-6 text-primary" />
              </div>
              <h1 className="text-2xl font-bold tracking-tight capitalize">
                {reportType} Intelligence Report
              </h1>
            </div>
            
            <div className="flex items-center gap-4 text-sm text-muted-foreground ml-11">
              <div className="flex items-center gap-1.5">
                <Calendar className="w-4 h-4" />
                <span>Generated: {new Date(report.generated_at).toLocaleString()}</span>
              </div>
            </div>
          </div>
          
          <Button 
            onClick={() => exportReport(reportType)}
            disabled={isPending}
            variant="outline"
          >
            <Download className="w-4 h-4 mr-2" />
            {isPending ? 'Exporting...' : 'Export PDF'}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};
