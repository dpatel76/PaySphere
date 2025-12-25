/**
 * Type declarations for cytoscape-dagre extension
 */
declare module 'cytoscape-dagre' {
  import { Core, LayoutOptions } from 'cytoscape';

  interface DagreLayoutOptions extends LayoutOptions {
    name: 'dagre';
    rankDir?: 'TB' | 'BT' | 'LR' | 'RL';
    rankSep?: number;
    nodeSep?: number;
    edgeSep?: number;
    padding?: number;
    spacingFactor?: number;
    animate?: boolean;
    animationDuration?: number;
    fit?: boolean;
  }

  function dagreExtension(cy: typeof import('cytoscape')): void;

  export = dagreExtension;
}
