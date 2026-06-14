import type { Artifact } from './types/artifact';

const equipmentVariationTile =
  /^\/tiles\/equipment\/(?<category>normal|ego)\/(?<path>.+?)(?<variation>[12])\.png$/;

const weaponTiles: Record<string, string> = {
  arbalest: '/tiles/equipment/artifact/weapon/ranged/arbalest3.png',
  athame: '/tiles/equipment/artifact/weapon/athame3.png',
  bardiche: '/tiles/equipment/artifact/weapon/bardiche3.png',
  battleaxe: '/tiles/equipment/artifact/weapon/battle_axe3.png',
  'broad axe': '/tiles/equipment/artifact/weapon/broad_axe3.png',
  club: '/tiles/equipment/artifact/weapon/club2.png',
  dagger: '/tiles/equipment/artifact/weapon/dagger3.png',
  'demon blade': '/tiles/equipment/artifact/weapon/demon_blade3.png',
  'demon trident': '/tiles/equipment/artifact/weapon/demon_trident3.png',
  'demon whip': '/tiles/equipment/artifact/weapon/demon_whip3.png',
  'dire flail': '/tiles/equipment/artifact/weapon/dire_flail3.png',
  'double sword': '/tiles/equipment/artifact/weapon/double_sword3.png',
  eveningstar: '/tiles/equipment/artifact/weapon/eveningstar3.png',
  'eudemon blade': '/tiles/equipment/artifact/weapon/demon_blade3.png',
  "executioner's axe": '/tiles/equipment/artifact/weapon/executioner_axe3.png',
  falchion: '/tiles/equipment/artifact/weapon/falchion3.png',
  flail: '/tiles/equipment/artifact/weapon/flail3.png',
  'giant club': '/tiles/equipment/artifact/weapon/giant_club3.png',
  'giant spiked club': '/tiles/equipment/artifact/weapon/giant_spiked_club3.png',
  glaive: '/tiles/equipment/artifact/weapon/glaive3.png',
  'great mace': '/tiles/equipment/artifact/weapon/mace_large3.png',
  'great sword': '/tiles/equipment/artifact/weapon/greatsword3.png',
  halberd: '/tiles/equipment/artifact/weapon/halberd3.png',
  hammer: '/tiles/equipment/artifact/weapon/hammer3.png',
  'hand axe': '/tiles/equipment/artifact/weapon/hand_axe3.png',
  'hand cannon': '/tiles/equipment/artifact/weapon/ranged/hand_cannon3.png',
  lajatang: '/tiles/equipment/artifact/weapon/lajatang3.png',
  'long sword': '/tiles/equipment/artifact/weapon/long_sword3.png',
  longbow: '/tiles/equipment/artifact/weapon/ranged/longbow3.png',
  mace: '/tiles/equipment/artifact/weapon/mace3.png',
  morningstar: '/tiles/equipment/artifact/weapon/morningstar3.png',
  orcbow: '/tiles/equipment/artifact/weapon/ranged/orcbow3.png',
  partisan: '/tiles/equipment/artifact/weapon/partisan3.png',
  quarterstaff: '/tiles/equipment/artifact/weapon/quarterstaff3.png',
  'quick blade': '/tiles/equipment/artifact/weapon/quickblade3.png',
  rapier: '/tiles/equipment/artifact/weapon/rapier3.png',
  'sacred scourge': '/tiles/equipment/artifact/weapon/demon_whip3.png',
  scimitar: '/tiles/equipment/artifact/weapon/scimitar3.png',
  'short sword': '/tiles/equipment/artifact/weapon/short_sword3.png',
  shortbow: '/tiles/equipment/artifact/weapon/ranged/shortbow3.png',
  sling: '/tiles/equipment/artifact/weapon/ranged/sling3.png',
  spear: '/tiles/equipment/artifact/weapon/spear3.png',
  staff: '/tiles/equipment/artifact/weapon/quarterstaff3.png',
  trident: '/tiles/equipment/artifact/weapon/trident3.png',
  trishula: '/tiles/equipment/artifact/weapon/demon_trident3.png',
  'triple crossbow': '/tiles/equipment/artifact/weapon/ranged/triple_crossbow2.png',
  'triple sword': '/tiles/equipment/artifact/weapon/triple_sword3.png',
  'war axe': '/tiles/equipment/artifact/weapon/war_axe3.png',
  whip: '/tiles/equipment/artifact/weapon/bullwhip3.png',
};

const armourTiles: Record<string, string> = {
  'acid dragon scales': '/tiles/equipment/artifact/armour/acid_dragon_armour_art.png',
  'animal skin': '/tiles/equipment/artifact/armour/animal_skin3.png',
  barding: '/tiles/equipment/artifact/armour/barding3.png',
  boots: '/tiles/equipment/artifact/armour/boots_art1.png',
  'pair of boots': '/tiles/equipment/artifact/armour/boots_art1.png',
  buckler: '/tiles/equipment/artifact/armour/shields/buckler3.png',
  cap: '/tiles/equipment/artifact/armour/headgear/hat3.png',
  'centaur barding': '/tiles/equipment/artifact/armour/barding3.png',
  'chain mail': '/tiles/equipment/artifact/armour/chain_mail3.png',
  cloak: '/tiles/equipment/artifact/armour/cloak4.png',
  'crystal plate armour': '/tiles/equipment/artifact/armour/crystal_plate3.png',
  'fire dragon scales': '/tiles/equipment/artifact/armour/fire_dragon_armour_art.png',
  'gold dragon scales': '/tiles/equipment/artifact/armour/golden_dragon_armour_art.png',
  'golden dragon scales': '/tiles/equipment/artifact/armour/golden_dragon_armour_art.png',
  gloves: '/tiles/equipment/artifact/armour/glove5.png',
  'pair of gloves': '/tiles/equipment/artifact/armour/glove5.png',
  hat: '/tiles/equipment/artifact/armour/headgear/hat3.png',
  helmet: '/tiles/equipment/artifact/armour/headgear/helmet_art1.png',
  'ice dragon scales': '/tiles/equipment/artifact/armour/ice_dragon_armour_art.png',
  'kite shield': '/tiles/equipment/artifact/armour/shields/kite_shield3.png',
  'leather armour': '/tiles/equipment/artifact/armour/leather_armour3.png',
  orb: '/tiles/equipment/artifact/armour/shields/orb_randart1.png',
  'pearl dragon scales': '/tiles/equipment/artifact/armour/pearl_dragon_armour_art.png',
  'plate armour': '/tiles/equipment/artifact/armour/plate3.png',
  'quicksilver dragon scales': '/tiles/equipment/artifact/armour/quicksilver_dragon_armour_art.png',
  'ring mail': '/tiles/equipment/artifact/armour/ring_mail3.png',
  robe: '/tiles/equipment/artifact/armour/robe_art1.png',
  'scale mail': '/tiles/equipment/artifact/armour/scale_mail3.png',
  scarf: '/tiles/equipment/artifact/armour/scarf3.png',
  'shadow dragon scales': '/tiles/equipment/artifact/armour/shadow_dragon_armour_art.png',
  shield: '/tiles/equipment/artifact/armour/shields/kite_shield3.png',
  'steam dragon scales': '/tiles/equipment/artifact/armour/steam_dragon_armour_art.png',
  'storm dragon scales': '/tiles/equipment/artifact/armour/storm_dragon_armour_art.png',
  'swamp dragon scales': '/tiles/equipment/artifact/armour/swamp_dragon_armour_art.png',
  'tower shield': '/tiles/equipment/artifact/armour/shields/tower_shield3.png',
  'troll leather armour': '/tiles/equipment/artifact/armour/troll_leather_armour_art.png',
  'troll skin': '/tiles/equipment/artifact/armour/troll_leather_armour_art.png',
};

const talismanTiles: Record<string, string> = {
  'blade talisman': '/tiles/equipment/artifact/talisman/blade.png',
  'dragon-coil talisman': '/tiles/equipment/artifact/talisman/dragon.png',
  'dragon-blood talisman': '/tiles/equipment/artifact/talisman/dragon.png',
  'eel talisman': '/tiles/equipment/artifact/talisman/eel.png',
  'fortress talisman': '/tiles/equipment/artifact/talisman/fortress.png',
  'granite talisman': '/tiles/equipment/artifact/talisman/statue.png',
  'hive talisman': '/tiles/equipment/artifact/talisman/hive.png',
  'inkwell talisman': '/tiles/equipment/artifact/talisman/inkwell.png',
  'lupine talisman': '/tiles/equipment/artifact/talisman/lupine.png',
  'maw talisman': '/tiles/equipment/artifact/talisman/maw.png',
  'medusa talisman': '/tiles/equipment/artifact/talisman/medusa.png',
  'protean talisman': '/tiles/equipment/artifact/talisman/protean.png',
  'quill talisman': '/tiles/equipment/artifact/talisman/quill.png',
  'riddle talisman': '/tiles/equipment/artifact/talisman/protean.png',
  'rimehorn talisman': '/tiles/equipment/artifact/talisman/rimehorn.png',
  'sanguine talisman': '/tiles/equipment/artifact/talisman/vampire.png',
  'scarab talisman': '/tiles/equipment/artifact/talisman/scarab.png',
  'serpent talisman': '/tiles/equipment/artifact/talisman/snake.png',
  'sphinx talisman': '/tiles/equipment/artifact/talisman/sphinx.png',
  'spider talisman': '/tiles/equipment/artifact/talisman/spider.png',
  'spore talisman': '/tiles/equipment/artifact/talisman/spore.png',
  'statue talisman': '/tiles/equipment/artifact/talisman/statue.png',
  'storm talisman': '/tiles/equipment/artifact/talisman/storm.png',
  'talisman of death': '/tiles/equipment/artifact/talisman/death.png',
  'vampire talisman': '/tiles/equipment/artifact/talisman/vampire.png',
  'wellspring talisman': '/tiles/equipment/artifact/talisman/water.png',
};

export function displayTileForArtifact(artifact: Artifact): string {
  const tile = artifact.tile.trim();
  if (tile.startsWith('/tiles/equipment/artifact/')) return tile;

  const fallback = fallbackTileForArtifact(artifact);

  const equipmentMatch = equipmentVariationTile.exec(tile);
  if (equipmentMatch?.groups) {
    return fallback ?? `/tiles/equipment/artifact/${equipmentMatch.groups.path}3.png`;
  }

  return fallback ?? tile;
}

function fallbackTileForArtifact(artifact: Artifact): string | null {
  const baseItem = artifact.baseItem.trim().toLowerCase();
  const subtype = artifact.subtype.trim().toLowerCase();

  if (artifact.type === 'weapon') {
    return weaponTiles[baseItem] ?? weaponTiles[subtype] ?? '/tiles/equipment/artifact/weapon/dagger3.png';
  }
  if (artifact.type === 'armour') {
    const armourSubtype = artifact.armourSubtype?.trim().toLowerCase() ?? '';
    const armourSlot = artifact.armourSlot?.trim().toLowerCase() ?? '';
    return (
      armourTiles[armourSubtype] ??
      armourTiles[baseItem] ??
      armourTiles[subtype] ??
      armourTiles[armourSlot] ??
      '/tiles/equipment/artifact/armour/robe_art1.png'
    );
  }
  if (artifact.type === 'jewellery') {
    if (artifact.jewellerySlot === 'amulet' || subtype.startsWith('amulet of ')) {
      return '/tiles/equipment/artifact/amulet/randarts/azure.png';
    }
    return '/tiles/equipment/artifact/ring/randarts/anvil.png';
  }
  if (artifact.type === 'talisman') {
    return talismanTiles[subtype] ?? talismanTiles[baseItem] ?? '/tiles/equipment/artifact/talisman/statue.png';
  }
  if (artifact.type === 'staff') {
    return '/tiles/equipment/artifact/staff/staff-artefact1.png';
  }
  if (artifact.type === 'misc') {
    if (baseItem === "charlatan's orb" || artifact.name.toLowerCase().includes('charlatan')) {
      return '/tiles/equipment/artifact/armour/artefact/urand_charlatan.png';
    }
    if (baseItem === 'crystal ball' || artifact.name.toLowerCase().includes('wucad mu')) {
      return '/tiles/equipment/artifact/armour/artefact/urand_wucad_mu.png';
    }
    if (baseItem === 'skull') {
      return '/tiles/equipment/artifact/armour/artefact/urand_skull_of_zonguldrok.png';
    }
    return '/tiles/equipment/artifact/ring/randarts/anvil.png';
  }
  return null;
}
