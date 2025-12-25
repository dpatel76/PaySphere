/**
 * Process File Page
 * Manual file processing with live progress visualization
 */
import React, { useState, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Paper,
  LinearProgress,
  Chip,
  Alert,
  Divider,
  Stepper,
  Step,
  StepLabel,
  StepContent,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  PlayArrow as StartIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  HourglassEmpty as ProcessingIcon,
} from '@mui/icons-material';
import { colors, pipelineConfig } from '../styles/design-system';

interface ProcessingStats {
  layer: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  total: number;
  processed: number;
  failed: number;
  startTime?: Date;
  endTime?: Date;
  dqPassed?: number;
  dqFailed?: number;
}

interface LayerProgress {
  bronze: ProcessingStats;
  silver: ProcessingStats;
  gold: ProcessingStats;
  analytical: ProcessingStats;
}

const ProcessFilePage: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [messageType, setMessageType] = useState('pain.001');
  const [sourceSystem, setSourceSystem] = useState('manual_upload');
  const [isProcessing, setIsProcessing] = useState(false);
  const [activeStep, setActiveStep] = useState(-1);
  const [progress, setProgress] = useState<LayerProgress>({
    bronze: { layer: 'bronze', status: 'pending', total: 0, processed: 0, failed: 0 },
    silver: { layer: 'silver', status: 'pending', total: 0, processed: 0, failed: 0 },
    gold: { layer: 'gold', status: 'pending', total: 0, processed: 0, failed: 0 },
    analytical: { layer: 'analytical', status: 'pending', total: 0, processed: 0, failed: 0 },
  });
  const [batchId, setBatchId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setSelectedFile(event.target.files[0]);
      setError(null);
    }
  };

  const simulateProcessing = useCallback(async () => {
    if (!selectedFile) return;

    setIsProcessing(true);
    setActiveStep(0);
    setBatchId(`batch-${Date.now()}`);
    setError(null);

    // Simulate Bronze processing
    setProgress(prev => ({
      ...prev,
      bronze: { ...prev.bronze, status: 'processing', startTime: new Date(), total: 100 },
    }));

    for (let i = 0; i <= 100; i += 10) {
      await new Promise(r => setTimeout(r, 200));
      setProgress(prev => ({
        ...prev,
        bronze: { ...prev.bronze, processed: i, failed: Math.floor(i * 0.02) },
      }));
    }

    setProgress(prev => ({
      ...prev,
      bronze: { ...prev.bronze, status: 'completed', endTime: new Date() },
    }));
    setActiveStep(1);

    // Simulate Silver processing
    setProgress(prev => ({
      ...prev,
      silver: {
        ...prev.silver,
        status: 'processing',
        startTime: new Date(),
        total: prev.bronze.processed - prev.bronze.failed,
      },
    }));

    for (let i = 0; i <= 98; i += 10) {
      await new Promise(r => setTimeout(r, 300));
      const dqFailed = Math.floor(i * 0.05);
      setProgress(prev => ({
        ...prev,
        silver: {
          ...prev.silver,
          processed: i,
          failed: Math.floor(i * 0.01),
          dqPassed: i - dqFailed,
          dqFailed,
        },
      }));
    }

    setProgress(prev => ({
      ...prev,
      silver: { ...prev.silver, status: 'completed', endTime: new Date() },
    }));
    setActiveStep(2);

    // Simulate Gold processing
    setProgress(prev => ({
      ...prev,
      gold: {
        ...prev.gold,
        status: 'processing',
        startTime: new Date(),
        total: prev.silver.dqPassed || prev.silver.processed,
      },
    }));

    for (let i = 0; i <= 93; i += 10) {
      await new Promise(r => setTimeout(r, 250));
      setProgress(prev => ({
        ...prev,
        gold: { ...prev.gold, processed: i, failed: 0 },
      }));
    }

    setProgress(prev => ({
      ...prev,
      gold: { ...prev.gold, status: 'completed', endTime: new Date() },
    }));
    setActiveStep(3);

    // Simulate Analytical processing
    setProgress(prev => ({
      ...prev,
      analytical: {
        ...prev.analytical,
        status: 'processing',
        startTime: new Date(),
        total: prev.gold.processed,
      },
    }));

    for (let i = 0; i <= 93; i += 15) {
      await new Promise(r => setTimeout(r, 150));
      setProgress(prev => ({
        ...prev,
        analytical: { ...prev.analytical, processed: i, failed: 0 },
      }));
    }

    setProgress(prev => ({
      ...prev,
      analytical: { ...prev.analytical, status: 'completed', endTime: new Date() },
    }));
    setActiveStep(4);
    setIsProcessing(false);
  }, [selectedFile]);

  const getStepIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <SuccessIcon sx={{ color: colors.success.main }} />;
      case 'failed':
        return <ErrorIcon sx={{ color: colors.error.main }} />;
      case 'processing':
        return <ProcessingIcon sx={{ color: colors.primary.main }} />;
      default:
        return undefined;
    }
  };

  const LayerProgressCard: React.FC<{ layer: keyof LayerProgress; stats: ProcessingStats }> = ({
    layer,
    stats,
  }) => {
    const layerColor = colors.zones[layer];
    const progressPercent = stats.total > 0 ? (stats.processed / stats.total) * 100 : 0;

    return (
      <Paper
        sx={{
          p: 2,
          border: `2px solid ${stats.status === 'processing' ? layerColor.main : colors.grey[200]}`,
          borderRadius: 2,
          opacity: stats.status === 'pending' ? 0.5 : 1,
          transition: 'all 0.3s ease',
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Box
              sx={{
                width: 10,
                height: 10,
                borderRadius: '50%',
                backgroundColor: layerColor.main,
                mr: 1,
              }}
            />
            <Typography variant="subtitle2" fontWeight={600}>
              {pipelineConfig.layerNames[layer]}
            </Typography>
          </Box>
          <Chip
            label={stats.status.toUpperCase()}
            size="small"
            color={
              stats.status === 'completed' ? 'success' :
              stats.status === 'processing' ? 'primary' :
              stats.status === 'failed' ? 'error' : 'default'
            }
          />
        </Box>

        <Box sx={{ mb: 1 }}>
          <LinearProgress
            variant={stats.status === 'processing' ? 'indeterminate' : 'determinate'}
            value={progressPercent}
            sx={{
              height: 8,
              borderRadius: 4,
              backgroundColor: colors.grey[200],
              '& .MuiLinearProgress-bar': {
                backgroundColor: layerColor.main,
                borderRadius: 4,
              },
            }}
          />
        </Box>

        <Grid container spacing={1}>
          <Grid size={4}>
            <Typography variant="caption" color="text.secondary">Total</Typography>
            <Typography variant="body2" fontWeight={600}>{stats.total}</Typography>
          </Grid>
          <Grid size={4}>
            <Typography variant="caption" color="text.secondary">Processed</Typography>
            <Typography variant="body2" fontWeight={600} color="success.main">
              {stats.processed}
            </Typography>
          </Grid>
          <Grid size={4}>
            <Typography variant="caption" color="text.secondary">Failed</Typography>
            <Typography variant="body2" fontWeight={600} color="error.main">
              {stats.failed}
            </Typography>
          </Grid>
        </Grid>

        {stats.dqPassed !== undefined && (
          <Box sx={{ mt: 1, pt: 1, borderTop: `1px solid ${colors.grey[200]}` }}>
            <Typography variant="caption" color="text.secondary">DQ Results</Typography>
            <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
              <Chip
                size="small"
                icon={<SuccessIcon sx={{ fontSize: 14 }} />}
                label={`${stats.dqPassed} passed`}
                color="success"
                variant="outlined"
              />
              <Chip
                size="small"
                icon={<ErrorIcon sx={{ fontSize: 14 }} />}
                label={`${stats.dqFailed} failed`}
                color="error"
                variant="outlined"
              />
            </Box>
          </Box>
        )}

        {stats.endTime && stats.startTime && (
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
            Duration: {((stats.endTime.getTime() - stats.startTime.getTime()) / 1000).toFixed(1)}s
          </Typography>
        )}
      </Paper>
    );
  };

  return (
    <Box>
      {/* Page Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Process File
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Upload and process a payment message file through the full pipeline
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Left: Upload Form */}
        <Grid size={{ xs: 12, md: 4 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                File Upload
              </Typography>
              <Divider sx={{ mb: 2 }} />

              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Message Type</InputLabel>
                <Select
                  value={messageType}
                  label="Message Type"
                  onChange={(e) => setMessageType(e.target.value)}
                  disabled={isProcessing}
                >
                  <MenuItem value="pain.001">pain.001 - Customer Credit Transfer</MenuItem>
                  <MenuItem value="pain.002">pain.002 - Payment Status</MenuItem>
                  <MenuItem value="pacs.008">pacs.008 - FI Credit Transfer</MenuItem>
                  <MenuItem value="camt.053">camt.053 - Bank Statement</MenuItem>
                  <MenuItem value="MT103">MT103 - SWIFT Single Credit</MenuItem>
                </Select>
              </FormControl>

              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Source System</InputLabel>
                <Select
                  value={sourceSystem}
                  label="Source System"
                  onChange={(e) => setSourceSystem(e.target.value)}
                  disabled={isProcessing}
                >
                  <MenuItem value="manual_upload">Manual Upload</MenuItem>
                  <MenuItem value="swift_alliance">SWIFT Alliance</MenuItem>
                  <MenuItem value="core_banking">Core Banking</MenuItem>
                  <MenuItem value="payment_hub">Payment Hub</MenuItem>
                </Select>
              </FormControl>

              <Box
                sx={{
                  border: `2px dashed ${colors.grey[300]}`,
                  borderRadius: 2,
                  p: 3,
                  textAlign: 'center',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  '&:hover': {
                    borderColor: colors.primary.main,
                    backgroundColor: `${colors.primary.main}08`,
                  },
                }}
                component="label"
              >
                <input
                  type="file"
                  hidden
                  accept=".xml,.json,.txt"
                  onChange={handleFileChange}
                  disabled={isProcessing}
                />
                <UploadIcon sx={{ fontSize: 48, color: colors.grey[400], mb: 1 }} />
                {selectedFile ? (
                  <Typography variant="body2" fontWeight={500}>
                    {selectedFile.name}
                  </Typography>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    Click to upload XML, JSON, or text file
                  </Typography>
                )}
              </Box>

              {error && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  {error}
                </Alert>
              )}

              <Button
                fullWidth
                variant="contained"
                size="large"
                startIcon={<StartIcon />}
                onClick={simulateProcessing}
                disabled={!selectedFile || isProcessing}
                sx={{ mt: 2 }}
              >
                {isProcessing ? 'Processing...' : 'Start Processing'}
              </Button>

              {batchId && (
                <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                  Batch ID: {batchId}
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Right: Processing Progress */}
        <Grid size={{ xs: 12, md: 8 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                Processing Progress
              </Typography>
              <Divider sx={{ mb: 2 }} />

              <Grid container spacing={2}>
                <Grid size={{ xs: 12, sm: 6 }}>
                  <LayerProgressCard layer="bronze" stats={progress.bronze} />
                </Grid>
                <Grid size={{ xs: 12, sm: 6 }}>
                  <LayerProgressCard layer="silver" stats={progress.silver} />
                </Grid>
                <Grid size={{ xs: 12, sm: 6 }}>
                  <LayerProgressCard layer="gold" stats={progress.gold} />
                </Grid>
                <Grid size={{ xs: 12, sm: 6 }}>
                  <LayerProgressCard layer="analytical" stats={progress.analytical} />
                </Grid>
              </Grid>

              {/* Summary */}
              {activeStep === 4 && (
                <Alert severity="success" sx={{ mt: 3 }}>
                  <Typography variant="body2" fontWeight={500}>
                    Processing Complete!
                  </Typography>
                  <Typography variant="body2">
                    {progress.gold.processed} records successfully promoted to Gold layer.
                    {progress.silver.dqFailed} records failed DQ validation.
                  </Typography>
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ProcessFilePage;
