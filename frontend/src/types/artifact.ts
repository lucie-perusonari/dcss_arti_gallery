export type ArtifactType = 'weapon' | 'armour' | 'jewellery' | 'talisman' | 'staff' | 'misc';

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
  weaponSubtype?: string | null;
  armourSlot?: string | null;
  jewellerySlot?: string | null;
  tile: string;
  source: {
    player: string;
  };
  randomAttributes: string[];
  score: ArtifactEvaluation;
  dcssDescription: string;
};

export type ArtifactFilters = {
  search: string;
  type: ArtifactType | 'all';
  slot: string;
  luxuryOnly: boolean;
  player: string;
};
