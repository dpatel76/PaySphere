/**
 * Lineage Graph Viewer Component
 * Interactive visualization of data lineage using Cytoscape.js
 */
import React, { useEffect, useRef, useState, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  ToggleButtonGroup,
  ToggleButton,
  CircularProgress,
  Alert,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  ZoomIn as ZoomInIcon,
  ZoomOut as ZoomOutIcon,
  CenterFocusStrong as FitIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import cytoscape, { Core, ElementDefinition, StylesheetStyle } from 'cytoscape';
import dagre from 'cytoscape-dagre';
import { useQuery } from '@tanstack/react-query';
import { graphApi, schemaApi } from '../../api/client';
import type { EnhancedLineageNode, EnhancedLineageEdge } from '../../types';
import { colors } from '../../styles/design-system';

// Register dagre layout
cytoscape.use(dagre);

interface LineageGraphViewerProps {
  messageType?: string;
  selectedField?: string;
  onNodeClick?: (nodeId: string, nodeType: string) => void;
}

type ViewMode = 'message-type' | 'field';

// Zone colors for styling nodes
const zoneColors: Record<string, { bg: string; border: string; text: string }> = {
  bronze: { bg: colors.zones.bronze.light, border: colors.zones.bronze.main, text: colors.zones.bronze.dark },
  silver: { bg: colors.zones.silver.light, border: colors.zones.silver.main, text: colors.zones.silver.dark },
  gold: { bg: colors.zones.gold.light, border: colors.zones.gold.main, text: colors.zones.gold.dark },
  analytics: { bg: colors.zones.analytical.light, border: colors.zones.analytical.main, text: colors.zones.analytical.dark },
  analytical: { bg: colors.zones.analytical.light, border: colors.zones.analytical.main, text: colors.zones.analytical.dark },
};

// Cytoscape stylesheet
const graphStyles: StylesheetStyle[] = [
  {
    selector: 'node',
    style: {
      'background-color': '#f5f5f5',
      'border-width': 2,
      'border-color': '#666',
      label: 'data(label)',
      'text-valign': 'center',
      'text-halign': 'center',
      'font-size': '11px',
      'text-wrap': 'wrap',
      'text-max-width': '120px',
      width: 140,
      height: 50,
      shape: 'roundrectangle',
    },
  },
  {
    selector: 'node[type="zone"]',
    style: {
      'background-color': '#e3f2fd',
      'border-color': '#1976d2',
      'font-weight': 'bold',
      'font-size': '14px',
      width: 180,
      height: 60,
    },
  },
  {
    selector: 'node[type="entity"]',
    style: {
      'background-color': 'data(bgColor)',
      'border-color': 'data(borderColor)',
      color: 'data(textColor)',
      'font-weight': 'bold',
    },
  },
  {
    selector: 'node[type="field"]',
    style: {
      'background-color': '#fff',
      'border-color': 'data(borderColor)',
      'border-style': 'dashed',
      'font-size': '10px',
      width: 120,
      height: 40,
    },
  },
  {
    selector: 'node:selected',
    style: {
      'border-width': 4,
      'border-color': colors.primary.main,
      'background-color': colors.primary.light,
    },
  },
  {
    selector: 'edge',
    style: {
      width: 2,
      'line-color': '#999',
      'target-arrow-color': '#999',
      'target-arrow-shape': 'triangle',
      'curve-style': 'bezier',
      'arrow-scale': 1.2,
    },
  },
  {
    selector: 'edge[type="entity_transform"]',
    style: {
      width: 3,
      'line-color': colors.primary.main,
      'target-arrow-color': colors.primary.main,
    },
  },
  {
    selector: 'edge[type="field_mapping"]',
    style: {
      width: 2,
      'line-color': colors.info.main,
      'target-arrow-color': colors.info.main,
      'line-style': 'dashed',
    },
  },
  {
    selector: 'edge:selected',
    style: {
      width: 4,
      'line-color': colors.primary.dark,
      'target-arrow-color': colors.primary.dark,
    },
  },
];

const LineageGraphViewer: React.FC<LineageGraphViewerProps> = ({
  messageType = 'pain.001',
  selectedField,
  onNodeClick,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>('message-type');
  const [selectedNode, setSelectedNode] = useState<string | null>(null);

  // Fetch schema lineage for message type view
  const {
    data: schemaLineage,
    isLoading: loadingSchema,
    error: schemaError,
    refetch: refetchSchema,
  } = useQuery({
    queryKey: ['schemaLineage', messageType],
    queryFn: () => graphApi.getSchemaLineage(messageType),
    enabled: viewMode === 'message-type',
    staleTime: 5 * 60 * 1000,
  });

  // Fetch field lineage when a field is selected
  const {
    data: fieldLineage,
    isLoading: loadingField,
    error: fieldError,
  } = useQuery({
    queryKey: ['fieldLineage', messageType, selectedField],
    queryFn: () => graphApi.getFieldLineage(messageType, selectedField!),
    enabled: viewMode === 'field' && !!selectedField,
    staleTime: 5 * 60 * 1000,
  });

  // Convert schema lineage to Cytoscape elements
  const buildSchemaElements = useCallback((): ElementDefinition[] => {
    if (!schemaLineage) return [];

    const elements: ElementDefinition[] = [];
    const entities = schemaLineage.entities || [];
    const transforms = schemaLineage.transforms || [];

    // Create entity nodes grouped by layer
    const layerOrder = ['bronze', 'silver', 'gold', 'analytics'];

    entities.forEach((entityData: any) => {
      const entity = entityData.entity;
      if (!entity) return;

      const layer = entity.layer || 'unknown';
      const zoneStyle = zoneColors[layer] || zoneColors.bronze;

      elements.push({
        data: {
          id: entity.entity_id,
          label: entity.entity_type || entity.entity_id,
          type: 'entity',
          zone: layer,
          bgColor: zoneStyle.bg,
          borderColor: zoneStyle.border,
          textColor: zoneStyle.text,
        },
      });
    });

    // Create transformation edges
    transforms.forEach((t: any) => {
      if (t.source && t.target) {
        elements.push({
          data: {
            id: `${t.source.entity_id}-${t.target.entity_id}`,
            source: t.source.entity_id,
            target: t.target.entity_id,
            type: 'entity_transform',
            label: t.transform?.transformation_type || '',
          },
        });
      }
    });

    return elements;
  }, [schemaLineage]);

  // Convert field lineage to Cytoscape elements
  const buildFieldElements = useCallback((): ElementDefinition[] => {
    if (!fieldLineage) return [];

    const elements: ElementDefinition[] = [];
    const nodes = fieldLineage.nodes || [];
    const edges = fieldLineage.edges || [];

    nodes.forEach((node: any) => {
      // Extract layer from node id (e.g., "bronze.table.field" -> "bronze")
      const layer = node.id?.split('.')[0] || 'unknown';
      const zoneStyle = zoneColors[layer] || zoneColors.bronze;

      elements.push({
        data: {
          id: node.id,
          label: node.label || node.field_name,
          type: 'field',
          zone: layer,
          fieldName: node.field_name,
          dataType: node.data_type,
          borderColor: zoneStyle.border,
        },
      });
    });

    edges.forEach((edge: any, index: number) => {
      elements.push({
        data: {
          id: `edge-${index}`,
          source: edge.source,
          target: edge.target,
          type: 'field_mapping',
          transformType: edge.transform_type,
          logic: edge.logic,
        },
      });
    });

    return elements;
  }, [fieldLineage]);

  // Initialize Cytoscape
  useEffect(() => {
    if (!containerRef.current) return;

    const elements = viewMode === 'message-type' ? buildSchemaElements() : buildFieldElements();

    // Destroy existing instance
    if (cyRef.current) {
      cyRef.current.destroy();
    }

    // Create new instance
    cyRef.current = cytoscape({
      container: containerRef.current,
      elements,
      style: graphStyles,
      layout: {
        name: 'dagre',
        rankDir: 'LR', // Left to right
        nodeSep: 80,
        rankSep: 150,
        padding: 50,
      } as any,
      minZoom: 0.3,
      maxZoom: 3,
      wheelSensitivity: 0.2,
    });

    // Add click handler
    cyRef.current.on('tap', 'node', (evt) => {
      const node = evt.target;
      const nodeId = node.id();
      const nodeType = node.data('type');
      setSelectedNode(nodeId);
      onNodeClick?.(nodeId, nodeType);
    });

    // Fit to container
    cyRef.current.fit(undefined, 50);

    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
        cyRef.current = null;
      }
    };
  }, [viewMode, buildSchemaElements, buildFieldElements, onNodeClick]);

  // Zoom controls
  const handleZoomIn = () => {
    cyRef.current?.zoom(cyRef.current.zoom() * 1.2);
  };

  const handleZoomOut = () => {
    cyRef.current?.zoom(cyRef.current.zoom() / 1.2);
  };

  const handleFit = () => {
    cyRef.current?.fit(undefined, 50);
  };

  const handleRefresh = () => {
    refetchSchema();
  };

  const handleViewModeChange = (
    _event: React.MouseEvent<HTMLElement>,
    newMode: ViewMode | null
  ) => {
    if (newMode) {
      setViewMode(newMode);
      setSelectedNode(null);
    }
  };

  const isLoading = loadingSchema || loadingField;
  const error = schemaError || fieldError;

  return (
    <Paper elevation={1} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box
        sx={{
          p: 2,
          borderBottom: `1px solid ${colors.grey[200]}`,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="h6" fontWeight={600}>
            Data Lineage
          </Typography>
          <Chip
            label={messageType}
            size="small"
            sx={{
              backgroundColor: colors.primary.light + '30',
              fontWeight: 500,
            }}
          />
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          {/* View Mode Toggle */}
          <ToggleButtonGroup
            value={viewMode}
            exclusive
            onChange={handleViewModeChange}
            size="small"
          >
            <ToggleButton value="message-type">
              Entity View
            </ToggleButton>
            <ToggleButton value="field" disabled={!selectedField}>
              Field View
            </ToggleButton>
          </ToggleButtonGroup>

          {/* Zoom Controls */}
          <Box sx={{ display: 'flex', gap: 0.5 }}>
            <Tooltip title="Zoom In">
              <IconButton size="small" onClick={handleZoomIn}>
                <ZoomInIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            <Tooltip title="Zoom Out">
              <IconButton size="small" onClick={handleZoomOut}>
                <ZoomOutIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            <Tooltip title="Fit to View">
              <IconButton size="small" onClick={handleFit}>
                <FitIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            <Tooltip title="Refresh">
              <IconButton size="small" onClick={handleRefresh}>
                <RefreshIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
      </Box>

      {/* Legend */}
      <Box
        sx={{
          px: 2,
          py: 1,
          borderBottom: `1px solid ${colors.grey[200]}`,
          display: 'flex',
          gap: 2,
          flexWrap: 'wrap',
        }}
      >
        {Object.entries(zoneColors).slice(0, 4).map(([zone, style]) => (
          <Box key={zone} sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <Box
              sx={{
                width: 16,
                height: 16,
                borderRadius: 1,
                backgroundColor: style.bg,
                border: `2px solid ${style.border}`,
              }}
            />
            <Typography variant="caption" sx={{ textTransform: 'capitalize' }}>
              {zone}
            </Typography>
          </Box>
        ))}
      </Box>

      {/* Graph Container */}
      <Box sx={{ flex: 1, position: 'relative', minHeight: 400 }}>
        {isLoading && (
          <Box
            sx={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              zIndex: 10,
            }}
          >
            <CircularProgress />
          </Box>
        )}

        {error && (
          <Alert severity="error" sx={{ m: 2 }}>
            Failed to load lineage data: {(error as Error).message}
          </Alert>
        )}

        <Box
          ref={containerRef}
          sx={{
            width: '100%',
            height: '100%',
            minHeight: 400,
            backgroundColor: colors.grey[50],
          }}
        />
      </Box>

      {/* Selected Node Info */}
      {selectedNode && (
        <Box
          sx={{
            p: 2,
            borderTop: `1px solid ${colors.grey[200]}`,
            backgroundColor: colors.grey[50],
          }}
        >
          <Typography variant="body2" color="text.secondary">
            Selected: <strong>{selectedNode}</strong>
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export default LineageGraphViewer;
