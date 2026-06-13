import { mockArtifacts } from "../data/mockArtifacts";
import type {
  Artifact,
  ArtifactFilters,
  ArtifactType,
} from "../types/artifact";

const API_BASE_URL = (import.meta.env.VITE_ARTIFACT_API_URL ?? "").trim();

type ArtifactResponse = {
  artifacts: Artifact[];
};

export type PlayerArtifactsRequest = {
  nickname: string;
};

export type PlayerArtifactsResponse = {
  nickname: string;
  status: "completed" | "failed";
  message?: string;
  artifactCount?: number;
  error?: string;
  artifacts?: Artifact[];
};

const delay = (ms: number) =>
  new Promise((resolve) => window.setTimeout(resolve, ms));

const apiUrl = (path: string) => `${API_BASE_URL.replace(/\/$/, "")}${path}`;

async function apiError(response: Response, fallback: string) {
  let detail = "";
  try {
    const data = (await response.json()) as { detail?: unknown };
    detail = typeof data.detail === "string" ? `: ${data.detail}` : "";
  } catch {
    detail = "";
  }
  return new Error(`${fallback} with ${response.status}${detail}`);
}

const matchesFilters = (artifact: Artifact, filters: ArtifactFilters) => {
  const search = filters.search.trim().toLowerCase();
  const player = filters.player.trim().toLowerCase();
  const searchable = [
    artifact.name,
    artifact.baseItem,
    artifact.subtype,
    artifact.randomAttributes.join(" "),
  ]
    .join(" ")
    .toLowerCase();

  return (
    (filters.type === "all" || artifact.type === filters.type) &&
    (!search || searchable.includes(search)) &&
    (!player || artifact.source.player.toLowerCase() === player)
  );
};

export const artifactApi = {
  async listArtifacts(filters: ArtifactFilters): Promise<Artifact[]> {
    if (!API_BASE_URL) {
      await delay(120);
      return mockArtifacts.filter((artifact) =>
        matchesFilters(artifact, filters),
      );
    }

    const params = new URLSearchParams();
    if (filters.search.trim()) params.set("q", filters.search.trim());
    if (filters.type !== "all") params.set("type", filters.type);
    if (filters.player.trim()) params.set("player", filters.player.trim());

    const response = await fetch(apiUrl(`/artifacts?${params.toString()}`));
    if (!response.ok) {
      throw await apiError(response, "Artifact API failed");
    }

    const data = (await response.json()) as ArtifactResponse;
    return data.artifacts;
  },

  async getArtifact(id: string): Promise<Artifact | null> {
    if (!API_BASE_URL) {
      await delay(80);
      return mockArtifacts.find((artifact) => artifact.id === id) ?? null;
    }

    const response = await fetch(apiUrl(`/artifacts/${id}`));
    if (response.status === 404) return null;
    if (!response.ok) {
      throw await apiError(response, "Artifact API failed");
    }

    return (await response.json()) as Artifact;
  },

  async listTypes(): Promise<Array<ArtifactType | "all">> {
    if (!API_BASE_URL) {
      return ["all", "weapon", "armour", "jewellery", "talisman", "staff", "misc"];
    }

    const response = await fetch(apiUrl("/artifact-types"));
    if (!response.ok) {
      throw await apiError(response, "Artifact type API failed");
    }

    return (await response.json()) as Array<ArtifactType | "all">;
  },

  async listPlayerArtifacts(
    request: PlayerArtifactsRequest,
  ): Promise<PlayerArtifactsResponse> {
    const nickname = request.nickname.trim();
    if (!nickname) {
      throw new Error("Nickname is required");
    }

    if (!API_BASE_URL) {
      await delay(180);
      const artifacts = mockArtifacts.filter(
        (artifact) => artifact.source.player.toLowerCase() === nickname.toLowerCase(),
      );
      return {
        nickname,
        status: "completed",
        artifactCount: artifacts.length,
        message: `Loaded ${artifacts.length} stored artifacts for ${nickname}.`,
        artifacts,
      };
    }

    const params = new URLSearchParams({ player: nickname });
    const response = await fetch(apiUrl(`/artifacts?${params.toString()}`));
    if (!response.ok) {
      throw await apiError(response, "Player artifact API failed");
    }

    const data = (await response.json()) as ArtifactResponse;
    return {
      nickname,
      status: "completed",
      message: `Loaded ${data.artifacts.length} stored artifacts for ${nickname}.`,
      artifactCount: data.artifacts.length,
      artifacts: data.artifacts,
    };
  },
};
