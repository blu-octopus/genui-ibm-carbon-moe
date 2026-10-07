export type CarbonNode = {
  type: string;
  props?: Record<string, unknown>;
  children?: CarbonNode[];
};

export type CarbonDocument = {
  id: string;
  root: CarbonNode;
};
