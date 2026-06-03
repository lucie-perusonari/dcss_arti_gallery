export type ArtifactType = 'weapon' | 'armour' | 'jewellery' | 'talisman' | 'staff' | 'misc';

export type ArtifactAttribute = {
  token: string;
  kind: 'resistance' | 'stat' | 'property' | 'penalty' | 'brand' | 'spell_school';
  description: string;
  scoreImpact: 'positive' | 'negative' | 'neutral';
};

export type ArtifactEvaluation = {
  total: number;
  practical_score?: number | null;
  rarity_score?: number;
  offense: number;
  defense: number;
  utility: number;
  penalty: number;
  base_fit?: number;
  grade?: string;
  luxury_grade?: string | null;
};

export type Artifact = {
  id: string;
  name: string;
  baseItem: string;
  type: ArtifactType;
  subtype: string;
  tile: string;
  enchantment: string | null;
  brand: string | null;
  origin: string;
  source: {
    player: string;
    file: string;
    url?: string | null;
    line?: number;
    version?: string;
  };
  attributes: ArtifactAttribute[];
  allAttributes?: string[];
  baseAttributes?: string[];
  randomAttributes: string[];
  allAttributeText?: string;
  baseAttributeText?: string;
  randomAttributeText?: string;
  evaluation?: ArtifactEvaluation;
  score: ArtifactEvaluation;
  rawDescription: string[];
  dcssDescription: string;
};

export type ArtifactFilters = {
  search: string;
  type: ArtifactType | 'all';
};
